import { consume } from '@/lib/rateLimit';

export async function fetchJson<T>(url: string, init: RequestInit & { weight?: number; source?: 'info' | 'explorer' | 'rates' } = {}): Promise<T> {
  const { weight = 1, source = 'info', ...rest } = init as any;
  let attempt = 0;
  for (;;) {
    await consume(weight, source);
    const res = await fetch(url, rest);
    if (res.ok) return (await res.json()) as T;
    if (res.status === 429 || res.status >= 500) {
      attempt++;
      const backoff = Math.min(2000, 200 * Math.pow(2, attempt));
      await new Promise((r) => setTimeout(r, backoff));
      continue;
    }
    const text = await res.text().catch(() => '');
    throw new Error(`HTTP ${res.status} ${text}`);
  }
}

export async function postJson<T>(url: string, body: unknown, init: { weight?: number; source?: 'info' | 'explorer' | 'rates' } = {}) {
  return fetchJson<T>(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
    weight: init.weight,
    source: init.source,
  } as any);
}

