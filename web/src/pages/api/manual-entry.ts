import type { NextApiRequest, NextApiResponse } from 'next';
import { z } from 'zod';
import { prisma } from '@/server/db';
import { getUsdEurRateForDate } from '@/lib/exchangeRates';

const Body = z.object({
  walletAddress: z.string().min(10),
  date: z.string(), // ISO date or datetime
  category: z.enum(['deposit', 'withdrawal']),
  amountEUR: z.number(),
});

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });
  try {
    const data = Body.parse(typeof req.body === 'string' ? JSON.parse(req.body) : req.body);
    const ts = new Date(data.date);
    if (isNaN(ts.getTime())) return res.status(400).json({ error: 'invalid date' });
    const rate = await getUsdEurRateForDate(ts);
    const amountUSDC = data.amountEUR / rate;
    const txHash = `manual-${data.category}-${ts.getTime()}`;
    const tx = await prisma.transaction.upsert({
      where: { walletAddress_txHash: { walletAddress: data.walletAddress, txHash } },
      create: {
        walletAddress: data.walletAddress,
        txHash,
        category: data.category,
        symbol: 'USDC',
        amountUSDC,
        amountEUR: data.amountEUR,
        timestamp: ts,
      },
      update: {
        amountUSDC,
        amountEUR: data.amountEUR,
        timestamp: ts,
      },
    });
    res.status(200).json({ ok: true, id: tx.id });
  } catch (e: any) {
    res.status(400).json({ error: e?.message || 'invalid body' });
  }
}

