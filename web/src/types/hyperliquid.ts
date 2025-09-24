export type WalletAddress = string;

export interface UserFill {
  id: string;
  symbol: string;
  side: 'buy' | 'sell';
  size: number;
  price: number;
  fee: number;
  realizedPnl?: number;
  timestamp: number; // ms
}

export interface FundingPayment {
  id: string;
  symbol: string;
  amount: number; // USDC
  rate: number;
  positionSize: number;
  timestamp: number; // ms
}

export interface LedgerUpdate {
  id: string;
  type: 'deposit' | 'withdrawal' | 'transfer_fee' | 'other';
  amount: number; // USDC
  timestamp: number; // ms
  txHash?: string;
}

export interface OpenPositionState {
  symbol: string;
  size: number;
  entryPrice: number;
  markPrice: number;
  unrealizedPnl: number; // USDC
}

export interface InfoRequest<T extends string, P> {
  type: T;
  user?: string;
  params?: P;
}

