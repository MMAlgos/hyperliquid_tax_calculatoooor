-- Add unique composite index for open positions
CREATE UNIQUE INDEX IF NOT EXISTS "OpenPosition_walletAddress_symbol_key" ON "OpenPosition" ("walletAddress", "symbol");

