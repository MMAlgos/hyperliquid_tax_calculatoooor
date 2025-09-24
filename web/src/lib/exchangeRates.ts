import { prisma } from '@/server/db';
import { fetchJson } from '@/lib/http';

const EX_URL = process.env.EXCHANGERATE_HOST_URL || 'https://api.exchangerate.host';
const ECB_URL = 'https://sdw-wsrest.ecb.europa.eu/service/data';

function toDateOnlyUTC(d: Date) {
  return new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate()));
}

export async function getUsdEurRateForDate(date: Date): Promise<number> {
  const day = toDateOnlyUTC(date);
  const cached = await prisma.rate.findUnique({ where: { date: day } });
  if (cached) return cached.usdEur;

  const iso = day.toISOString().slice(0, 10);

  // Try ECB SDW API first: EXR/D.USD.EUR.SP00.A
  try {
    const json: any = await fetchJson(`${ECB_URL}/EXR/D.USD.EUR.SP00.A?time=${iso}`, { headers: { Accept: 'application/json' }, source: 'rates', weight: 1 } as any);
    const series = json?.dataSets?.[0]?.series?.['0:0:0:0:0']?.observations;
    const firstKey = series ? Object.keys(series)[0] : undefined;
    const value = firstKey ? series[firstKey]?.[0] : undefined;
    if (typeof value === 'number') {
      await prisma.rate.create({ data: { date: day, usdEur: value } });
      return value;
    }
  } catch {}

  // Fallback: exchangerate.host timeseries
  try {
    const url = `${EX_URL}/timeseries?base=USD&symbols=EUR&start_date=${iso}&end_date=${iso}`;
    const data = (await fetchJson(url, { source: 'rates', weight: 1 } as any)) as any;
    const rate = data?.rates?.[iso]?.EUR;
    if (typeof rate === 'number') {
      await prisma.rate.create({ data: { date: day, usdEur: rate } });
      return rate;
    }
  } catch {}

  throw new Error('Rate not found');
}

export function parseRatesCsv(csv: string): Array<{ date: Date; usdEur: number }> {
  const out: Array<{ date: Date; usdEur: number }> = [];
  const lines = csv.split(/\r?\n/).map((l) => l.trim()).filter(Boolean);
  for (const line of lines) {
    if (/^date\s*,/i.test(line)) continue; // header
    const [d, r] = line.split(',');
    const rate = Number(r);
    if (!d || !Number.isFinite(rate)) continue;
    const dt = new Date(d);
    if (!isNaN(dt.getTime())) out.push({ date: toDateOnlyUTC(dt), usdEur: rate });
  }
  return out;
}
