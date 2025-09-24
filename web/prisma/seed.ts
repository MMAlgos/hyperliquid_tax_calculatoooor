import { PrismaClient } from '@prisma/client';
const prisma = new PrismaClient();

async function main() {
  const year = 2025;
  const exists = await prisma.taxBracket.findFirst({ where: { year } });
  if (exists) {
    console.log('Tax brackets already seeded for', year);
    return;
  }
  const rows = [
    { incomeLimit: 13308, ratePercent: 0 },
    { incomeLimit: 21617, ratePercent: 20 },
    { incomeLimit: 35836, ratePercent: 30 },
    { incomeLimit: 69166, ratePercent: 40 },
    { incomeLimit: 103072, ratePercent: 48 },
    { incomeLimit: 1000000, ratePercent: 50 },
    { incomeLimit: Number.POSITIVE_INFINITY, ratePercent: 55 },
  ];
  // Use a large number to represent Infinity for storage
  await prisma.taxBracket.createMany({
    data: rows.map((r) => ({ year, incomeLimit: r.incomeLimit === Infinity ? 1e12 : r.incomeLimit, ratePercent: r.ratePercent })),
  });
  console.log('Seeded Austrian tax brackets for', year);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
}).finally(async () => {
  await prisma.$disconnect();
});

