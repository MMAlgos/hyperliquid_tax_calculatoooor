# Hyperliquid Tax Web (MVP)

Quickstart (after installing deps):

- Copy `.env.example` to `.env` and adjust if needed.
- Run `npm install` then `npm run prisma:migrate` then `npm run dev`.
- Open http://localhost:5173 and enter a wallet address.

Notes
- Uses SQLite via Prisma for caching: wallet fetch logs, transactions, funding, rates, open positions, tax brackets.
- Sync endpoint: `POST /api/sync-wallet` with `{ walletAddress: string, saveWallet: boolean }`.
- EUR conversion: cached by day using exchangerate.host timeseries.
- Next steps: add charts, tables, reports (CSV/Excel/PDF), and tax simulation UI.

