import type { NextApiRequest, NextApiResponse } from 'next';
import { prisma } from '@/server/db';
import { toPdf } from '@/lib/exports';
import { simulateTax } from '@/lib/tax';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const wallet = String(req.query.wallet || '').trim();
  const baseIncome = Number(req.query.baseIncome || 0);
  const year = Number(req.query.year || new Date().getFullYear());
  if (!wallet) return res.status(400).json({ error: 'wallet required' });

  const tx = await prisma.transaction.findMany({ where: { walletAddress: wallet }, orderBy: { timestamp: 'asc' } });
  const funding = await prisma.funding.findMany({ where: { walletAddress: wallet }, orderBy: { timestamp: 'asc' } });
  const positions = await prisma.openPosition.findMany({ where: { walletAddress: wallet } });

  const realized = tx.filter((t) => t.category === 'gain' || t.category === 'loss').reduce((s, t) => s + t.amountEUR, 0);
  const fees = tx.filter((t) => t.category === 'fee').reduce((s, t) => s + t.amountEUR, 0);
  const deposits = tx.filter((t) => t.category === 'deposit').reduce((s, t) => s + t.amountEUR, 0);
  const withdrawals = tx.filter((t) => t.category === 'withdrawal').reduce((s, t) => s + t.amountEUR, 0);
  const fund = funding.reduce((s, f) => s + f.amountEUR, 0);

  const tax = await simulateTax(year, baseIncome, realized + fund - fees);

  const pdf = await toPdf({
    title: `Steuer-Checkliste (${wallet})`,
    totals: {
      realized_eur: realized,
      funding_eur: fund,
      fees_eur: fees,
      deposits_eur: deposits,
      withdrawals_eur: withdrawals,
      trades_count: tx.filter((t) => t.category === 'gain' || t.category === 'loss').length,
    } as any,
    notes: [
      `Year: ${year}`,
      `Base income (EUR): ${baseIncome.toFixed(2)}`,
      `Tax without trading: ${tax.withoutTrading.totalTax.toFixed(2)} EUR`,
      `Tax with trading: ${tax.withTrading.totalTax.toFixed(2)} EUR`,
      `Delta (trading tax): ${tax.tradingDelta.toFixed(2)} EUR`,
      'Include CSV/Excel detailed report if needed.',
    ],
    positions: positions.map((p) => ({
      symbol: p.symbol,
      size: p.size,
      entryPrice: p.entryPrice,
      markPrice: p.markPrice,
      upnlEUR: p.unrealizedPnlEUR,
    })),
  });

  res.setHeader('Content-Type', 'application/pdf');
  res.setHeader('Content-Disposition', `attachment; filename=steuer_checkliste_${year}.pdf`);
  return res.status(200).send(Buffer.from(pdf));
}
