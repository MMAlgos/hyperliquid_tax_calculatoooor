type Source = 'info' | 'explorer' | 'rates';

const limits: Record<Source, { capacity: number; refillPerSec: number; tokens: number; last: number }> = {
  info: { capacity: 1200, refillPerSec: 20, tokens: 1200, last: Date.now() },
  explorer: { capacity: 1200, refillPerSec: 20, tokens: 1200, last: Date.now() },
  rates: { capacity: 60, refillPerSec: 1, tokens: 60, last: Date.now() },
};

export async function consume(weight: number, source: Source) {
  const b = limits[source];
  const now = Date.now();
  const elapsed = (now - b.last) / 1000;
  b.last = now;
  b.tokens = Math.min(b.capacity, b.tokens + elapsed * b.refillPerSec);
  while (b.tokens < weight) {
    const waitMs = Math.ceil(((weight - b.tokens) / b.refillPerSec) * 1000);
    await new Promise((r) => setTimeout(r, Math.min(1000, waitMs)));
    const n = Date.now();
    const e = (n - b.last) / 1000;
    b.last = n;
    b.tokens = Math.min(b.capacity, b.tokens + e * b.refillPerSec);
  }
  b.tokens -= weight;
}

