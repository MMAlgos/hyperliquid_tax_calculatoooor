import type { NextApiRequest, NextApiResponse } from 'next';
import { simulateTax } from '@/lib/tax';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const year = Number(req.query.year || new Date().getFullYear());
  const baseIncome = Number(req.query.baseIncome || 0);
  const tradingProfit = Number(req.query.tradingProfit || 0);
  if (Number.isNaN(year)) return res.status(400).json({ error: 'invalid year' });
  const data = await simulateTax(year, baseIncome, tradingProfit);
  res.status(200).json(data);
}

