Master Prompt: Hyperliquid Wallet Tracker & Tax CSV Generator
Role

You are a senior full-stack engineer (TypeScript/React + Node/Next.js + PostgreSQL). Build a production-ready web app that tracks a Hyperliquid futures/perps wallet, displays portfolio/trade analytics, and exports a tax-ready CSV with fees/funding separated as deductible expenses.

Objectives

Track a single Hyperliquid wallet (user-supplied): ingest trades, funding, fees, transfers/deposits/withdrawals, liquidations, and PnL.

Compute:

Total value deposited (cash in) and withdrawn (cash out).

Account PnL (realized), unrealized PnL, equity, balance.

All-time high (ATH) account value and date.

Cumulative paid trading fees and cumulative net funding (paid/received).

Account PnL + paid fees + funding fees (for tax).

Tax CSV exporter with columns suitable for filing:

Separate deductible expenses: trading fees and funding fees.

Tax is applied only on profit (realized PnL), after deducting fees/funding.

User inputs tax %; show after-tax profit and what’s left.

Web UI: wallet overview, charts, filters, date ranges, CSV export, and a tax calculator panel.

Treat Hyperliquid as the execution venue. If multiple APIs exist, create a clean Data Access Layer that can be swapped. If an official API is unavailable for a data type, provide a pluggable “adapter” with mock + docstring on how to wire it once keys/endpoints are known.

Functional Requirements
Inputs / Settings

WALLET_ADDRESS (string, required)

BASE_CCY (default: USD)

TIMEZONE (default: Europe/Vienna)

DATE_RANGE (default: all time; allow custom)

TAX_RATE_PERCENT (user input at runtime)

Toggle: include unrealized PnL in dashboard (never in tax CSV)

Historical FX (optional later; keep infra ready but default off)

Data Ingestion

Create data/HyperliquidClient with functions (return typed DTOs):

getAccountSummary(wallet)

getFills(wallet, start?, end?) — all fills (entry/exit), quantities, prices.

getFundingPayments(wallet, start?, end?) — signed amounts per period.

getFees(wallet, start?, end?) — trading fees per fill (or derive from fills).

getTransfers(wallet, start?, end?) — deposits/withdrawals.

getLiquidations(wallet, start?, end?) — if applicable.

getOpenPositions(wallet) — for unrealized PnL & equity.

If the upstream returns “events”, implement a normalizer mapping each event to one of: TRADE_FILL, FUNDING, FEE, DEPOSIT, WITHDRAWAL, LIQUIDATION, REBATE.

Core Calculations (Server side)

Implement deterministic, unit-tested functions:

Cost basis & realized PnL: FIFO by market (symbol).
realized_pnl = (exit_price - avg_entry_cost) * signed_size minus trading fee for that fill (fee is expense, not reducing proceeds directly in CSV; keep both).

Unrealized PnL: from open positions vs. last price.

Funding: sum signed cash flows; treat positive=received, negative=paid.

Fees: sum of trading fees (and any exchange fees) as expenses.

Deposits/Withdrawals: aggregate to get Net Deposited = sum(deposits) - sum(withdrawals).

Equity over time: reconstruct time-series equity = prior_equity + realized_pnl + funding + rebates − fees ± deposits/withdrawals (ignore unrealized for tax).

ATH: max of equity curve; record timestamp.

Taxable profit:

taxable_profit = max(0, realized_pnl_total - trading_fees_paid_total - funding_fees_paid_total)
tax_due = taxable_profit * tax_rate
after_tax_profit = realized_pnl_total - tax_due


Note: Only paid funding is deductible; funding received increases profit. Keep both columns and a net_funding.

Persistence

PostgreSQL with Prisma (or Drizzle).

Tables:

accounts(id, wallet, base_ccy, created_at)

events(id, wallet, ts, txid, market, type, side, qty, price, notional, fee, fee_ccy, funding, funding_ccy, deposit, withdrawal, liquidation_pnl, raw jsonb, unique(txid,type,index))

positions(wallet, market, size, avg_entry, last_price, upnl, updated_at)

metrics_daily(wallet, date, realized_pnl, fees_paid, funding_paid, funding_received, deposits, withdrawals, equity_close)

Idempotent upserts; dedupe by (txid,type,index).

CSV Export (Tax-ready)

One row per event with normalized columns:

Column
timestamp (ISO 8601, TZ aware)
tx_id
type (TRADE_FILL/FEE/FUNDING/DEPOSIT/WITHDRAWAL/LIQUIDATION/REBATE)
market
side (BUY/SELL for fills)
size
price
notional_usd
trading_fee_paid_usd
funding_paid_usd
funding_received_usd
realized_pnl_usd (per fill; 0 if N/A)
balance_change_usd (signed cash-flow view)
notes

Add a summary footer (separate CSV or on UI):
realized_pnl_total, fees_paid_total, funding_paid_total, funding_received_total, net_funding, taxable_profit, tax_rate, tax_due, after_tax_profit.

Ensure locale-safe (dot decimal, UTF-8), deterministically sorted by timestamp asc.

UI/UX (Next.js + React)

Pages:

Dashboard

Wallet & date picker

KPI cards: Net Deposited, Realized PnL, Unrealized PnL, Equity, ATH (value/date), Fees Paid, Funding Paid/Received, Net Funding, Taxable Profit, Tax Due (input tax %), After-Tax Profit.

Charts: Equity over time; PnL by day; Fees vs Funding stacked bars.

Trades & Funding

Table with filters (market, side, type, date range)

Sticky totals row

Tax Calculator

Input tax %; show calculation with breakdown.

CSV Export

Buttons: “Export Events CSV”, “Export Summary CSV”, “Export By Year”.

Settings

Wallet address, base currency, timezone.

Use Tailwind + shadcn/ui; all tables are virtualized; export via streaming.

Edge Cases & Rules

Partial fills / multiple fills per order — handle individually.

Funding can be negative (paid) or positive (received). Keep both; only paid is deductible.

Rebates: treat as income (increase profit) unless local rules say otherwise (keep as a separate type).

Liquidations: record realized PnL and any extra fees.

Missing fee fields: derive using fee_rate * notional if provided; otherwise set fee=null and flag in UI.

Rollover across date boundaries — use event timestamps; never batch away time granularity.

If any amounts are in non-USD, convert to USD using provided market quotes; centralize conversion in Money.ts.

Non-Functional

Type-safe end-to-end (TypeScript). Zod schemas for API responses.

Deterministic calculations with snapshot tests.

Background job (cron/queue) to refresh wallet data and recompute metrics for selected date ranges.

Environment-first design: .env for API keys; never log secrets.

Privacy: no third-party analytics by default.

Deliverables

Next.js app with:

/api/ingest?wallet=… (server actions ok) to fetch+normalize+persist.

/api/export/events.csv?wallet=…&from=…&to=…

/api/export/summary.csv?wallet=…&from=…&to=…

Core libs: lib/pnl.ts, lib/funding.ts, lib/fees.ts, lib/csv.ts, lib/money.ts

Data layer: data/HyperliquidClient.ts with typed methods + adapters.

Tests: Jest unit tests for PnL (FIFO), funding math, fee aggregation, and taxable profit. Include fixtures for:

Long/short round trips

Partial fills

Funding paid/received mix

Liquidation case

Zero-fee venue (to verify fee=0 behavior)

Calculation Specs (explicit)
type Fill = {
  ts: string;           // ISO
  txid: string;
  market: string;       // e.g., BTC-PERP
  side: 'BUY'|'SELL';
  size: number;         // contracts or base units
  price: number;        // quote/base
  notional: number;     // abs(size)*price
  feePaid: number;      // positive number (expense)
};

type Funding = {
  ts: string;
  txid: string;
  market: string;
  amount: number;       // positive=received, negative=paid
};

type Transfer = {
  ts: string;
  txid: string;
  amount: number;       // +deposit, -withdrawal
};

type RealizedFillPnL = {
  realizedPnL: number;  // excludes fees by convention
  realizedPnLAfterFees: number; // realizedPnL - feePaid
};


FIFO PnL per market

Maintain a queue of open lots {qty, cost}.

On BUY: push a lot.

On SELL: consume from lots; for each matched slice:
slicePnL = (sellPrice - avgEntry) * qty with sign conventions for shorts mirrored (implement generic signed math). Sum slices = realizedPnL.

Totals

realized_pnl_total = sum(realizedPnL across fills)
fees_paid_total    = sum(max(0, feePaid))
funding_paid_total = sum(max(0, -min(0, funding.amount)))
funding_recv_total = sum(max(0,  max(0, funding.amount)))
net_funding        = funding_recv_total - funding_paid_total

taxable_profit     = max(0, realized_pnl_total - fees_paid_total - funding_paid_total)
tax_due            = taxable_profit * tax_rate
after_tax_profit   = realized_pnl_total - tax_due


Equity curve (discrete by event ts)

equity_t = equity_{t-1}
         + realizedPnL(event)
         - feePaid(event)
         + funding.amount(event)
         + deposit(event)
         - withdrawal(event)

CSV Schema (headers)
timestamp,tx_id,type,market,side,size,price,notional_usd,trading_fee_paid_usd,funding_paid_usd,funding_received_usd,realized_pnl_usd,balance_change_usd,notes


Row examples (conceptual):

Trade fill: realized_pnl_usd computed; balance_change_usd = -trading_fee_paid_usd

Funding paid: funding_paid_usd > 0, balance_change_usd = -funding_paid_usd

Funding received: funding_received_usd > 0, balance_change_usd = +funding_received_usd

Deposit: type=DEPOSIT, balance_change_usd=+amount

Withdrawal: type=WITHDRAWAL, balance_change_usd=-amount

UI Details

KPI cards with exact labels:

“Net Deposited”

“Realized PnL”

“Unrealized PnL”

“Equity (Current)”

“ATH Equity” (value + date)

“Fees Paid (Trading)”

“Funding Paid / Received”

“Net Funding”

“Taxable Profit”

“Tax Due @ X%”

“After-Tax Profit”

Controls: wallet input, date range, timezone, tax %, export buttons.

Tables: infinite scroll, CSV download from server endpoints.

Quality & Testing

100% type coverage on calculation modules.

Snapshot test of CSV export for a fixed fixture set (stable hashes).

Numeric precision: use decimal.js to avoid FP drift; format only at UI/CSV boundaries.

Documentation

README.md with:

How to wire Hyperliquid API keys (if needed).

Event mapping table (venue field → normalized fields).

Tax assumptions: profit = realized PnL, deductible = trading fees + funding paid; fees/funding received are income.

How to add another venue (adapter pattern).

Acceptance Criteria

For a given wallet + fixture, totals must match:

Deposits/Withdrawals totals

Realized PnL

Fees Paid

Funding Paid/Received

Net Funding

Taxable Profit, Tax Due, After-Tax Profit

CSV opens cleanly in Excel/Numbers and imports into tax tools.

UI shows correct ATH value/date within the selected range.

Implementation Hint (optional scaffolding)

Stack: Next.js App Router, Prisma + Postgres, Tailwind + shadcn/ui, TanStack Table, Zod, decimal.js.

Background refresh: cron route or queue worker.

Money/FX: centralize in lib/money.ts.
