-- CreateTable
CREATE TABLE "WalletFetchLog" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "walletAddress" TEXT NOT NULL,
    "lastFetchedAt" DATETIME NOT NULL,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" DATETIME NOT NULL
);

-- CreateTable
CREATE TABLE "Transaction" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "walletAddress" TEXT NOT NULL,
    "txHash" TEXT NOT NULL,
    "category" TEXT NOT NULL,
    "symbol" TEXT,
    "amountUSDC" REAL NOT NULL,
    "amountEUR" REAL NOT NULL,
    "timestamp" DATETIME NOT NULL,
    "meta" TEXT,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- CreateTable
CREATE TABLE "Funding" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "walletAddress" TEXT NOT NULL,
    "fundingId" TEXT NOT NULL,
    "amountUSDC" REAL NOT NULL,
    "amountEUR" REAL NOT NULL,
    "symbol" TEXT,
    "timestamp" DATETIME NOT NULL,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- CreateTable
CREATE TABLE "Rate" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "date" DATETIME NOT NULL,
    "usdEur" REAL NOT NULL,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- CreateTable
CREATE TABLE "OpenPosition" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "walletAddress" TEXT NOT NULL,
    "symbol" TEXT NOT NULL,
    "size" REAL NOT NULL,
    "entryPrice" REAL NOT NULL,
    "markPrice" REAL NOT NULL,
    "unrealizedPnlUSDC" REAL NOT NULL,
    "unrealizedPnlEUR" REAL NOT NULL,
    "updatedAt" DATETIME NOT NULL,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- CreateTable
CREATE TABLE "TaxBracket" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "year" INTEGER NOT NULL,
    "incomeLimit" REAL NOT NULL,
    "ratePercent" REAL NOT NULL
);

-- CreateIndex
CREATE INDEX "WalletFetchLog_walletAddress_idx" ON "WalletFetchLog"("walletAddress");

-- CreateIndex
CREATE INDEX "Transaction_walletAddress_timestamp_idx" ON "Transaction"("walletAddress", "timestamp");

-- CreateIndex
CREATE UNIQUE INDEX "Transaction_walletAddress_txHash_key" ON "Transaction"("walletAddress", "txHash");

-- CreateIndex
CREATE INDEX "Funding_walletAddress_timestamp_idx" ON "Funding"("walletAddress", "timestamp");

-- CreateIndex
CREATE UNIQUE INDEX "Funding_walletAddress_fundingId_key" ON "Funding"("walletAddress", "fundingId");

-- CreateIndex
CREATE UNIQUE INDEX "Rate_date_key" ON "Rate"("date");

-- CreateIndex
CREATE INDEX "OpenPosition_walletAddress_symbol_idx" ON "OpenPosition"("walletAddress", "symbol");

-- CreateIndex
CREATE INDEX "TaxBracket_year_idx" ON "TaxBracket"("year");
