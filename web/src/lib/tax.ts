import { prisma } from '@/server/db';

export interface TaxBreakdown {
  brackets: Array<{ upTo: number; rate: number; tax: number }>;
  totalTax: number;
}

export async function simulateTax(year: number, baseIncomeEUR: number, tradingProfitEUR: number): Promise<{
  withoutTrading: TaxBreakdown;
  withTrading: TaxBreakdown;
  tradingDelta: number;
}> {
  const brackets = await prisma.taxBracket.findMany({
    where: { year },
    orderBy: { incomeLimit: 'asc' },
  });
  const calc = (income: number): TaxBreakdown => {
    let remaining = income;
    let prev = 0;
    let total = 0;
    const applied: TaxBreakdown['brackets'] = [];
    for (const b of brackets) {
      const span = Math.max(0, Math.min(remaining, b.incomeLimit - prev));
      const tax = span * (b.ratePercent / 100);
      applied.push({ upTo: b.incomeLimit, rate: b.ratePercent, tax });
      total += tax;
      remaining -= span;
      prev = b.incomeLimit;
      if (remaining <= 0) break;
    }
    if (remaining > 0) {
      const top = brackets[brackets.length - 1];
      const tax = remaining * (top.ratePercent / 100);
      applied.push({ upTo: Infinity, rate: top.ratePercent, tax });
      total += tax;
    }
    return { brackets: applied, totalTax: Math.max(0, total) };
  };
  const without = calc(baseIncomeEUR);
  const withT = calc(baseIncomeEUR + tradingProfitEUR);
  return { withoutTrading: without, withTrading: withT, tradingDelta: withT.totalTax - without.totalTax };
}

