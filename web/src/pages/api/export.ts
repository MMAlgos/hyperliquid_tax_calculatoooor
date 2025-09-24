import type { NextApiRequest, NextApiResponse } from 'next';
import { prisma } from '@/server/db';
import { toCsv, toExcel, toPdf } from '@/lib/exports';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const wallet = String(req.query.wallet || '').trim();
  const type = String(req.query.type || 'csv');
  if (!wallet) return res.status(400).json({ error: 'wallet required' });

  const transactions = await prisma.transaction.findMany({ where: { walletAddress: wallet }, orderBy: { timestamp: 'asc' } });
  const funding = await prisma.funding.findMany({ where: { walletAddress: wallet }, orderBy: { timestamp: 'asc' } });

  if (type === 'transactions_csv') {
    const csv = toCsv(transactions.map((t) => ({
      timestamp: t.timestamp.toISOString(),
      category: t.category,
      symbol: t.symbol,
      amountUSDC: t.amountUSDC,
      amountEUR: t.amountEUR,
      txHash: t.txHash,
    })));
    res.setHeader('Content-Type', 'text/csv');
    res.setHeader('Content-Disposition', `attachment; filename=transactions_eur.csv`);
    return res.status(200).send(csv);
  }

  if (type === 'funding_csv') {
    const csv = toCsv(funding.map((f) => ({
      timestamp: f.timestamp.toISOString(),
      symbol: f.symbol,
      amountUSDC: f.amountUSDC,
      amountEUR: f.amountEUR,
      fundingId: f.fundingId,
    })));
    res.setHeader('Content-Type', 'text/csv');
    res.setHeader('Content-Disposition', `attachment; filename=funding_eur.csv`);
    return res.status(200).send(csv);
  }

  if (type === 'fees_csv') {
    const fees = transactions.filter((t) => t.category === 'fee');
    const csv = toCsv(fees.map((t) => ({ timestamp: t.timestamp.toISOString(), symbol: t.symbol, amountEUR: t.amountEUR, amountUSDC: t.amountUSDC })));
    res.setHeader('Content-Type', 'text/csv');
    res.setHeader('Content-Disposition', `attachment; filename=fees_eur.csv`);
    return res.status(200).send(csv);
  }

  if (type === 'summary_csv') {
    const realized = transactions.filter((t) => t.category === 'gain' || t.category === 'loss').reduce((s, t) => s + t.amountEUR, 0);
    const fees = transactions.filter((t) => t.category === 'fee').reduce((s, t) => s + t.amountEUR, 0);
    const deposits = transactions.filter((t) => t.category === 'deposit').reduce((s, t) => s + t.amountEUR, 0);
    const withdrawals = transactions.filter((t) => t.category === 'withdrawal').reduce((s, t) => s + t.amountEUR, 0);
    const fund = funding.reduce((s, f) => s + f.amountEUR, 0);
    const csv = toCsv([{ realized_eur: realized, funding_eur: fund, fees_eur: fees, deposits_eur: deposits, withdrawals_eur: withdrawals }]);
    res.setHeader('Content-Type', 'text/csv');
    res.setHeader('Content-Disposition', `attachment; filename=summary_eur.csv`);
    return res.status(200).send(csv);
  }

  if (type === 'xlsx') {
    const sheets = {
      Summary: [
        {
          realized_eur: transactions
            .filter((t) => t.category === 'gain' || t.category === 'loss')
            .reduce((s, t) => s + t.amountEUR, 0),
          funding_eur: funding.reduce((s, f) => s + f.amountEUR, 0),
          fees_eur: transactions.filter((t) => t.category === 'fee').reduce((s, t) => s + t.amountEUR, 0),
          deposits_eur: transactions.filter((t) => t.category === 'deposit').reduce((s, t) => s + t.amountEUR, 0),
          withdrawals_eur: transactions.filter((t) => t.category === 'withdrawal').reduce((s, t) => s + t.amountEUR, 0),
        },
      ],
      Transactions: transactions.map((t) => ({
        timestamp: t.timestamp.toISOString(),
        category: t.category,
        symbol: t.symbol,
        amountUSDC: t.amountUSDC,
        amountEUR: t.amountEUR,
        txHash: t.txHash,
      })),
      Funding: funding.map((f) => ({
        timestamp: f.timestamp.toISOString(),
        symbol: f.symbol,
        amountUSDC: f.amountUSDC,
        amountEUR: f.amountEUR,
        fundingId: f.fundingId,
      })),
      Fees: transactions.filter((t) => t.category === 'fee').map((t) => ({
        timestamp: t.timestamp.toISOString(), symbol: t.symbol, amountUSDC: t.amountUSDC, amountEUR: t.amountEUR
      })),
      Deposits: transactions.filter((t) => t.category === 'deposit').map((t) => ({
        timestamp: t.timestamp.toISOString(), amountEUR: t.amountEUR, amountUSDC: t.amountUSDC
      })),
      Withdrawals: transactions.filter((t) => t.category === 'withdrawal').map((t) => ({
        timestamp: t.timestamp.toISOString(), amountEUR: t.amountEUR, amountUSDC: t.amountUSDC
      })),
      OpenPositions: (await prisma.openPosition.findMany({ where: { walletAddress: wallet } })).map((p) => ({
        symbol: p.symbol, size: p.size, entryPrice: p.entryPrice, markPrice: p.markPrice, upnlEUR: p.unrealizedPnlEUR
      })),
    } as const;
    const bin = await toExcel(sheets as any);
    res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
    res.setHeader('Content-Disposition', `attachment; filename=report.xlsx`);
    return res.status(200).send(Buffer.from(bin));
  }

  if (type === 'pdf') {
    const totals = {
      realized: transactions
        .filter((t) => t.category === 'gain' || t.category === 'loss')
        .reduce((s, t) => s + t.amountEUR, 0),
      funding: funding.reduce((s, f) => s + f.amountEUR, 0),
      fees: transactions.filter((t) => t.category === 'fee').reduce((s, t) => s + t.amountEUR, 0),
    };
    const genAt = new Date();
    const notes = [
      `Wallet: ${wallet}`,
      `Generated: ${genAt.toISOString()}`,
      'Timezone: Europe/Vienna (day grouping)',
      'Unrealized PnL is not taxed until realized',
    ];
    const positions = await prisma.openPosition.findMany({ where: { walletAddress: wallet } });
    const bin = await toPdf({
      title: `Hyperliquid Report (${wallet})`,
      totals,
      notes,
      positions: positions.map((p) => ({
        symbol: p.symbol,
        size: p.size,
        entryPrice: p.entryPrice,
        markPrice: p.markPrice,
        upnlEUR: p.unrealizedPnlEUR,
      })),
    });
    res.setHeader('Content-Type', 'application/pdf');
    res.setHeader('Content-Disposition', `attachment; filename=report.pdf`);
    return res.status(200).send(Buffer.from(bin));
  }

  return res.status(400).json({ error: 'unknown export type' });
}
