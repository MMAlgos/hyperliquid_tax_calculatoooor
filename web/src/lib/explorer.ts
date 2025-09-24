import { fetchJson } from '@/lib/http';

const EXPLORER_URL = process.env.HYPERLIQUID_EXPLORER_URL || '';

export async function explorerUserDetails(address: string): Promise<any> {
  if (!EXPLORER_URL) throw new Error('EXPLORER URL not configured');
  // Note: Endpoint shape may differ; adapt as needed.
  const url = `${EXPLORER_URL}/user_details?address=${encodeURIComponent(address)}`;
  return fetchJson<any>(url, { source: 'explorer', weight: 40 } as any);
}

export async function explorerTxDetails(hash: string): Promise<any> {
  if (!EXPLORER_URL) throw new Error('EXPLORER URL not configured');
  const url = `${EXPLORER_URL}/tx_details?hash=${encodeURIComponent(hash)}`;
  return fetchJson<any>(url, { source: 'explorer', weight: 40 } as any);
}

