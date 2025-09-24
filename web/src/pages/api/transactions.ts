import type { NextApiRequest, NextApiResponse } from 'next';
import { prisma } from '@/server/db';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const wallet = String(req.query.wallet || '').trim();
  if (!wallet) return res.status(400).json({ error: 'wallet required' });
  const list = await prisma.transaction.findMany({
    where: { walletAddress: wallet },
    orderBy: { timestamp: 'asc' },
  });
  res.status(200).json({ items: list });
}

