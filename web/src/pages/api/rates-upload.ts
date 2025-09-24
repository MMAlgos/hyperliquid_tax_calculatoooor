import type { NextApiRequest, NextApiResponse } from 'next';
import { prisma } from '@/server/db';
import { parseRatesCsv } from '@/lib/exchangeRates';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });
  const csv = typeof req.body === 'string' ? req.body : req.body?.csv;
  if (!csv || typeof csv !== 'string') return res.status(400).json({ error: 'csv required' });
  const rows = parseRatesCsv(csv);
  for (const r of rows) {
    await prisma.rate.upsert({
      where: { date: r.date },
      update: { usdEur: r.usdEur },
      create: { date: r.date, usdEur: r.usdEur },
    });
  }
  res.status(200).json({ inserted: rows.length });
}

