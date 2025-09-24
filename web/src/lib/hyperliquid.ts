import { z } from 'zod';
import type { WalletAddress } from '@/types/hyperliquid';
import { postJson } from '@/lib/http';

const INFO_URL = process.env.HYPERLIQUID_INFO_URL || 'https://api.hyperliquid.xyz/info';

export async function fetchUserFills(address: WalletAddress, since?: number) {
  const schema = z.object({ fills: z.array(z.any()) });
  const data = await postJson<{ fills: unknown[] }>(INFO_URL, {
    type: 'userFills',
    user: address,
    params: since ? { startTime: since } : undefined,
  }, { source: 'info', weight: 1 });
  return schema.parse(data).fills as any[];
}

export async function fetchUserFunding(address: WalletAddress, since?: number) {
  const schema = z.object({ funding: z.array(z.any()) });
  const data = await postJson<{ funding: unknown[] }>(INFO_URL, {
    type: 'userFunding',
    user: address,
    params: since ? { startTime: since } : undefined,
  }, { source: 'info', weight: 1 });
  return schema.parse(data).funding as any[];
}

export async function fetchUserNonFundingLedger(address: WalletAddress, since?: number) {
  const schema = z.object({ ledger: z.array(z.any()) });
  const data = await postJson<{ ledger: unknown[] }>(INFO_URL, {
    type: 'userNonFundingLedgerUpdates',
    user: address,
    params: since ? { startTime: since } : undefined,
  }, { source: 'info', weight: 1 });
  return schema.parse(data).ledger as any[];
}

export async function fetchClearinghouseState(address: WalletAddress) {
  const data = await postJson<unknown>(INFO_URL, { type: 'clearinghouseState', user: address }, { source: 'info', weight: 1 });
  return data as any;
}

// Placeholder for Explorer API integration
export async function fetchExplorerUserDetails(_address: WalletAddress) {
  return { txs: [] as any[] };
}
