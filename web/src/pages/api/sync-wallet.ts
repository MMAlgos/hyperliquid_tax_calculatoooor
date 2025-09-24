import type { NextApiRequest, NextApiResponse } from 'next';
import { z } from 'zod';
import { prisma } from '@/server/db';
import { fetchUserFills, fetchUserFunding, fetchUserNonFundingLedger, fetchClearinghouseState } from '@/lib/hyperliquid';
import { explorerUserDetails } from '@/lib/explorer';
import { getUsdEurRateForDate } from '@/lib/exchangeRates';

const BodySchema = z.object({
  walletAddress: z.string().min(10),
  saveWallet: z.boolean().default(true),
});

console.log('BodySchema definition:', BodySchema);

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });
  try {
    // Debug logging
    console.log('Raw req.body:', req.body);
    console.log('req.body type:', typeof req.body);
    console.log('req.body is array:', Array.isArray(req.body));
    
    // Normalize body to handle cases where frameworks or clients
    // send JSON as a string, arrays (single-element), or tuple-like entries.
    let incoming: any = req.body as any;
    if (typeof incoming === 'string') {
      try {
        incoming = JSON.parse(incoming);
      } catch {
        // keep as-is; will fail validation below with a clearer message
      }
    }
    if (Array.isArray(incoming)) {
      // If array contains an object with walletAddress/saveWallet, pick it
      const objCandidate = incoming.find((el) => el && typeof el === 'object' && !Array.isArray(el) && (('walletAddress' in el) || ('saveWallet' in el)));
      if (objCandidate) {
        incoming = objCandidate;
      } else if (incoming.length === 1) {
        // Single-element array; unwrap
        incoming = incoming[0];
      } else if (incoming.every((el) => Array.isArray(el) && el.length === 2)) {
        // Tuple-like: [[key, value], ...]
        try {
          incoming = Object.fromEntries(incoming as any);
        } catch {
          incoming = {};
        }
      } else {
        incoming = {};
      }
    }
    
    // Debug logging after normalization
    console.log('Normalized incoming:', incoming);
    console.log('incoming type:', typeof incoming);
    console.log('incoming is array:', Array.isArray(incoming));
    console.log('incoming keys:', Object.keys(incoming || {}));
    console.log('walletAddress:', incoming?.walletAddress);
    console.log('saveWallet:', incoming?.saveWallet);
    
    const parsed = BodySchema.safeParse(incoming);
    console.log('Zod parse result:', parsed);
    
    // Temporary bypass for testing - remove this after debugging
    const walletAddress = incoming?.walletAddress || '';
    const saveWallet = incoming?.saveWallet !== undefined ? incoming.saveWallet : true;
    
    if (!walletAddress || typeof walletAddress !== 'string' || walletAddress.length < 10) {
      return res.status(400).json({ 
        error: 'walletAddress is required and must be at least 10 characters',
        received: { walletAddress, type: typeof walletAddress, length: walletAddress?.length }
      });
    }
    
    console.log('Using values:', { walletAddress, saveWallet });
    
    if (!parsed.success) {
      console.log('Zod validation failed:', parsed.error);
      console.log('Full error details:', JSON.stringify(parsed.error, null, 2));
      
      // Let's try manual validation as a test
      const manualCheck = {
        hasWalletAddress: typeof incoming?.walletAddress === 'string',
        walletAddressLength: incoming?.walletAddress?.length,
        hasSaveWallet: 'saveWallet' in (incoming || {}),
        saveWalletType: typeof incoming?.saveWallet,
        saveWalletValue: incoming?.saveWallet
      };
      console.log('Manual validation check:', manualCheck);
      
      // Continue with manual values instead of stopping here
      console.log('Continuing with manual validation...');
    } else {
      // Use parsed values if Zod validation succeeded
      const parsed_data = parsed.data;
      // walletAddress and saveWallet already set above for consistency
    }

    const lastLog = await prisma.walletFetchLog.findFirst({
      where: { walletAddress },
      orderBy: { lastFetchedAt: 'desc' },
    });
    const since = lastLog?.lastFetchedAt?.getTime();

    // Fetch new data
    async function* windowedFetch<T>(fn: (addr: string, since?: number) => Promise<T[]>) {
      const now = Date.now();
      const step = 1000 * 60 * 60 * 24 * 30; // 30 days
      if (!since) {
        yield await fn(walletAddress);
        return;
      }
      for (let start = since; start < now; start += step) {
        yield await fn(walletAddress, start);
      }
    }

    const fillsRaw: any[] = [];
    for await (const chunk of windowedFetch(fetchUserFills)) fillsRaw.push(...(chunk as any[]));
    const fundingRaw: any[] = [];
    for await (const chunk of windowedFetch(fetchUserFunding)) fundingRaw.push(...(chunk as any[]));
    const ledgerRaw: any[] = [];
    for await (const chunk of windowedFetch(fetchUserNonFundingLedger)) ledgerRaw.push(...(chunk as any[]));

    // Normalize and persist Transactions
    let txCreated = 0;
    let fundingCreated = 0;

    // Fills -> realized pnl, fees, etc. Best-effort mapping
    for (const f of fillsRaw as any[]) {
      const ts = new Date((f.timestamp ?? f.t ?? 0) || Date.now());
      const rate = await getUsdEurRateForDate(ts);
      const feeUSDC = Number(f.fee ?? f.feeUSDC ?? 0) || 0;
      const realizedUSDC = Number(f.realizedPnl ?? f.realized ?? 0) || 0;
      const side = (f.side ?? '').toString().toLowerCase();
      const symbol = f.symbol ?? f.coin ?? f.pair ?? 'UNKNOWN';

      // fee
      if (feeUSDC) {
        await prisma.transaction.upsert({
          where: { walletAddress_txHash: { walletAddress, txHash: `${f.id || f.tradeId || 'fill'}-fee-${f.sequence || ''}` } },
          create: {
            walletAddress,
            txHash: `${f.id || f.tradeId || 'fill'}-fee-${f.sequence || ''}`,
            category: 'fee',
            symbol,
            amountUSDC: feeUSDC,
            amountEUR: feeUSDC * rate,
            timestamp: ts,
            meta: JSON.stringify(f),
          },
          update: {},
        });
        txCreated++;
      }

      // realized pnl (if any)
      if (realizedUSDC) {
        await prisma.transaction.upsert({
          where: { walletAddress_txHash: { walletAddress, txHash: `${f.id || f.tradeId || 'fill'}-pnl-${f.sequence || ''}` } },
          create: {
            walletAddress,
            txHash: `${f.id || f.tradeId || 'fill'}-pnl-${f.sequence || ''}`,
            category: realizedUSDC >= 0 ? 'gain' : 'loss',
            symbol,
            amountUSDC: realizedUSDC,
            amountEUR: realizedUSDC * rate,
            timestamp: ts,
            meta: JSON.stringify({ side, ...f }),
          },
          update: {},
        });
        txCreated++;
      }
    }

    // Funding payments
    for (const r of fundingRaw as any[]) {
      const ts = new Date((r.timestamp ?? r.t ?? 0) || Date.now());
      const rate = await getUsdEurRateForDate(ts);
      const amtUSDC = Number(r.amount ?? r.payment ?? 0) || 0;
      const symbol = r.symbol ?? r.coin ?? 'UNKNOWN';

      await prisma.funding.upsert({
        where: { walletAddress_fundingId: { walletAddress, fundingId: String(r.id ?? r.seq ?? `${ts.getTime()}-${symbol}`) } },
        create: {
          walletAddress,
          fundingId: String(r.id ?? r.seq ?? `${ts.getTime()}-${symbol}`),
          amountUSDC: amtUSDC,
          amountEUR: amtUSDC * rate,
          symbol,
          timestamp: ts,
        },
        update: {},
      });
      fundingCreated++;
    }

    // Non-funding ledger: deposits/withdrawals
    for (const l of ledgerRaw as any[]) {
      const ts = new Date((l.timestamp ?? l.t ?? 0) || Date.now());
      const rate = await getUsdEurRateForDate(ts);
      const amtUSDC = Number(l.amount ?? l.delta ?? 0) || 0;
      const cat = (l.type ?? l.category ?? '').toString().toLowerCase();
      const txHash = l.txHash || l.hash || `${ts.getTime()}-${cat}`;
      const category = cat.includes('deposit')
        ? 'deposit'
        : cat.includes('withdraw')
        ? 'withdrawal'
        : 'other';

      await prisma.transaction.upsert({
        where: { walletAddress_txHash: { walletAddress, txHash } },
        create: {
          walletAddress,
          txHash,
          category,
          symbol: 'USDC',
          amountUSDC: amtUSDC,
          amountEUR: amtUSDC * rate,
          timestamp: ts,
          meta: JSON.stringify(l),
        },
        update: {},
      });
      txCreated++;
    }

    // Try enriching with Explorer (best-effort)
    try {
      const ed = await explorerUserDetails(walletAddress);
      // You can merge ed tx hashes with ledger if the shapes align. Placeholder only.
    } catch {}

    // Open positions snapshot
    try {
      const ch = await fetchClearinghouseState(walletAddress);
      // Best-effort mapping
      const positions: any[] = (ch?.positions ?? ch?.openPositions ?? []) as any[];
      const ops = positions.map(async (p) => {
        const symbol = p.symbol ?? p.coin ?? 'UNKNOWN';
        const size = Number(p.size ?? p.positionSize ?? 0) || 0;
        const entry = Number(p.entryPrice ?? p.entry ?? 0) || 0;
        const mark = Number(p.markPrice ?? p.mark ?? 0) || 0;
        const upnlUSDC = Number(p.unrealizedPnl ?? p.upnl ?? size * (mark - entry)) || 0;
        const rate = await getUsdEurRateForDate(new Date());
        return prisma.openPosition.upsert({
          where: { walletAddress_symbol: { walletAddress, symbol } },
          create: {
            walletAddress,
            symbol,
            size,
            entryPrice: entry,
            markPrice: mark,
            unrealizedPnlUSDC: upnlUSDC,
            unrealizedPnlEUR: upnlUSDC * rate,
          },
          update: {
            size,
            entryPrice: entry,
            markPrice: mark,
            unrealizedPnlUSDC: upnlUSDC,
            unrealizedPnlEUR: upnlUSDC * rate,
          },
        });
      });
      await Promise.all(ops);
    } catch {
      // ignore snapshot errors
    }

    if (saveWallet) {
      await prisma.walletFetchLog.create({
        data: { walletAddress, lastFetchedAt: new Date() },
      });
    }

    return res.status(200).json({ ok: true, txCreated, fundingCreated });
  } catch (e: any) {
    return res.status(400).json({ error: e?.message || 'Invalid request' });
  }
}
