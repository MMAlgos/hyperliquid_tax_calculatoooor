import type { NextApiRequest, NextApiResponse } from 'next';
import { prisma } from '@/server/db';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const wallet = String(req.query.wallet || '').trim();
  if (!wallet) return res.status(400).json({ error: 'wallet required' });

  const tx = await prisma.transaction.findMany({ where: { walletAddress: wallet }, orderBy: { timestamp: 'asc' } });
  const funding = await prisma.funding.findMany({ where: { walletAddress: wallet }, orderBy: { timestamp: 'asc' } });
  const openPositions = await prisma.openPosition.findMany({ where: { walletAddress: wallet } });

  const totals = {
    realized_eur: 0,
    fees_eur: 0,
    funding_eur: 0,
    deposits_eur: 0,
    withdrawals_eur: 0,
  };

  const byDay = new Map<string, { realized: number; fees: number; funding: number; deposits: number; withdrawals: number }>();
  const viennaDayKey = (d: Date) => {
    const parts = new Intl.DateTimeFormat('de-AT', {
      timeZone: 'Europe/Vienna',
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    }).formatToParts(d);
    const y = parts.find((p) => p.type === 'year')?.value;
    const m = parts.find((p) => p.type === 'month')?.value;
    const day = parts.find((p) => p.type === 'day')?.value;
    return `${y}-${m}-${day}`;
  };

  for (const t of tx) {
    const key = viennaDayKey(t.timestamp);
    const slot = byDay.get(key) || { realized: 0, fees: 0, funding: 0, deposits: 0, withdrawals: 0 };
    if (t.category === 'gain') {
      totals.realized_eur += t.amountEUR;
      slot.realized += t.amountEUR;
    } else if (t.category === 'loss') {
      totals.realized_eur += t.amountEUR; // negative
      slot.realized += t.amountEUR;
    } else if (t.category === 'fee') {
      totals.fees_eur += t.amountEUR;
      slot.fees += t.amountEUR;
    } else if (t.category === 'deposit') {
      totals.deposits_eur += t.amountEUR;
      slot.deposits += t.amountEUR;
    } else if (t.category === 'withdrawal') {
      totals.withdrawals_eur += t.amountEUR;
      slot.withdrawals += t.amountEUR;
    }
    byDay.set(key, slot);
  }

  for (const f of funding) {
    totals.funding_eur += f.amountEUR;
    const key = viennaDayKey(f.timestamp);
    const slot = byDay.get(key) || { realized: 0, fees: 0, funding: 0, deposits: 0, withdrawals: 0 };
    slot.funding += f.amountEUR;
    byDay.set(key, slot);
  }

  const daily = Array.from(byDay.entries())
    .sort((a, b) => (a[0] < b[0] ? -1 : 1))
    .map(([date, v]) => ({ date, ...v }));

  let cumRealized = 0;
  let cumFunding = 0;
  let cumFees = 0;
  let cumInvested = 0; // deposits(+), withdrawals(+)
  const pnlSeries = daily.map((v) => {
    cumRealized += v.realized;
    cumFunding += v.funding;
    cumFees += v.fees;
    cumInvested += v.deposits + v.withdrawals;
    const cumulative = cumRealized + cumFunding - cumFees;
    return { date: v.date, realized: v.realized, funding: v.funding, fees: v.fees, cumulative };
  });

  let investedCum = 0;
  const equitySeries = daily.map((v, i) => {
    investedCum += v.deposits + v.withdrawals;
    const eq = pnlSeries[i].cumulative + investedCum;
    return { date: v.date, invested: investedCum, equity: eq };
  });

  // Drawdown from equity curve
  let peak = -Infinity;
  const drawdownSeries = equitySeries.map((p) => {
    peak = Math.max(peak, p.equity);
    const dd = peak > 0 ? (p.equity - peak) / peak : 0;
    return { date: p.date, drawdown: dd };
  });

  const invested = totals.deposits_eur + totals.withdrawals_eur; // withdrawals likely negative; keep as net invested
  const upnlEUR = openPositions.reduce((s, p) => s + p.unrealizedPnlEUR, 0);
  const equityNow = invested + totals.realized_eur + totals.funding_eur - totals.fees_eur + upnlEUR;

  // Simple stats
  const tradePnls = tx.filter((t) => t.category === 'gain' || t.category === 'loss').map((t) => t.amountEUR);
  const wins = tradePnls.filter((v) => v > 0);
  const losses = tradePnls.filter((v) => v < 0);
  const stats = {
    trades: tradePnls.length,
    winrate: tradePnls.length ? (wins.length / tradePnls.length) * 100 : 0,
    avg_win: wins.length ? wins.reduce((a, b) => a + b, 0) / wins.length : 0,
    avg_loss: losses.length ? losses.reduce((a, b) => a + b, 0) / losses.length : 0,
  };

  res.status(200).json({ totals, pnlSeries, equity: { invested, equityNow, upnlEUR }, equitySeries, drawdownSeries, openPositions, stats });
}
