import { useEffect, useMemo, useState } from 'react';
import dayjs from 'dayjs';
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, Legend } from 'recharts';
import { useQuery } from '@tanstack/react-query';

export default function Home() {
  const [wallet, setWallet] = useState('');
  const [saveWallet, setSaveWallet] = useState(true);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<null | { ok: boolean; txCreated: number; fundingCreated: number; error?: string }>(null);
  const [summary, setSummary] = useState<any | null>(null);
  const [tx, setTx] = useState<any[]>([]);
  const [funds, setFunds] = useState<any[]>([]);
  const [positions, setPositions] = useState<any[]>([]);
  const [show, setShow] = useState({ realized: true, feesFunding: true, positions: true, equity: true, tax: true, benchmark: false });
  const [manualDate, setManualDate] = useState<string>('');
  const [manualAmount, setManualAmount] = useState<string>('');
  const [manualType, setManualType] = useState<'deposit' | 'withdrawal'>('deposit');
  const [benchDaily, setBenchDaily] = useState<string>('0');
  const [baseIncome, setBaseIncome] = useState<string>('0');
  const [tax, setTax] = useState<any | null>(null);

  const onSync = async () => {
    setLoading(true);
    setResult(null);
    try {
      const res = await fetch('/api/sync-wallet', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ walletAddress: wallet.trim(), saveWallet }),
      });
      const data = await res.json();
      setResult(data);
    } catch (e: any) {
      setResult({ ok: false, txCreated: 0, fundingCreated: 0, error: e?.message || 'Request failed' });
    } finally {
      setLoading(false);
    }
  };

  const enabled = Boolean(wallet?.trim());
  const { data: summaryData } = useQuery({
    queryKey: ['summary', wallet, result?.ok],
    queryFn: async () => (await fetch(`/api/summary?wallet=${encodeURIComponent(wallet.trim())}`)).json(),
    enabled,
  });
  const { data: txData } = useQuery({
    queryKey: ['tx', wallet, result?.ok],
    queryFn: async () => (await fetch(`/api/transactions?wallet=${encodeURIComponent(wallet.trim())}`)).json(),
    enabled,
  });
  const { data: fundData } = useQuery({
    queryKey: ['fund', wallet, result?.ok],
    queryFn: async () => (await fetch(`/api/funding?wallet=${encodeURIComponent(wallet.trim())}`)).json(),
    enabled,
  });
  useEffect(() => {
    if (summaryData) {
      setSummary(summaryData);
      setPositions(summaryData.openPositions || []);
    }
    if (txData?.items) setTx(txData.items);
    if (fundData?.items) setFunds(fundData.items);
  }, [summaryData, txData, fundData]);

  const realizedProfit = useMemo(() => summary?.totals?.realized_eur ?? 0, [summary]);

  const onSimulate = async () => {
    const res = await fetch(`/api/tax?year=${new Date().getFullYear()}&baseIncome=${Number(baseIncome) || 0}&tradingProfit=${realizedProfit}`);
    setTax(await res.json());
  };

  return (
    <main className="max-w-4xl mx-auto p-4 font-sans">
      <h1 className="text-2xl font-semibold">Hyperliquid Tax Toolkit</h1>
      <p className="text-gray-700">Gib deine Wallet-Adresse ein, sync neue Daten und speichere sie optional in der lokalen DB (SQLite).</p>

      <div className="flex gap-3 items-center mt-4">
        <input className="flex-1 border border-gray-300 rounded px-2 py-2" placeholder="Wallet-Adresse" value={wallet} onChange={(e) => setWallet(e.target.value)} />
        <label className="flex gap-2 items-center text-sm text-gray-700">
          <input type="checkbox" checked={saveWallet} onChange={(e) => setSaveWallet(e.target.checked)} /> Wallet speichern
        </label>
        <button onClick={onSync} disabled={!wallet || loading} className="px-3 py-2 rounded bg-blue-600 text-white disabled:opacity-50">
          {loading ? 'Synchronisiere…' : 'Sync'}
        </button>
      </div>

      <div className="flex gap-4 flex-wrap mt-2 text-sm">
        <label><input type="checkbox" checked={show.realized} onChange={(e) => setShow({ ...show, realized: e.target.checked })} /> Realisierte PnL</label>
        <label><input type="checkbox" checked={show.feesFunding} onChange={(e) => setShow({ ...show, feesFunding: e.target.checked })} /> Fees & Funding</label>
        <label><input type="checkbox" checked={show.positions} onChange={(e) => setShow({ ...show, positions: e.target.checked })} /> Offene Positionen</label>
        <label><input type="checkbox" checked={show.equity} onChange={(e) => setShow({ ...show, equity: e.target.checked })} /> Equity vs. Invested</label>
        <label><input type="checkbox" checked={show.tax} onChange={(e) => setShow({ ...show, tax: e.target.checked })} /> Steuersimulation</label>
        <label><input type="checkbox" checked={show.benchmark} onChange={(e) => setShow({ ...show, benchmark: e.target.checked })} /> Benchmark</label>
      </div>

      {result && (
        <div style={{ marginTop: 20 }}>
          {result.error ? (
            <p style={{ color: 'crimson' }}>Fehler: {result.error}</p>
          ) : (
            <>
              <p>Transaktionen gespeichert: {result.txCreated}</p>
              <p>Funding-Zahlungen gespeichert: {result.fundingCreated}</p>
            </>
          )}
        </div>
      )}

      <section style={{ marginTop: 32 }}>
        <h2>Hinweise</h2>
        <ul>
          <li>EUR-Umrechnung nutzt historische Tageskurse und wird in der DB gecached.</li>
          <li>Nur neue Daten seit dem letzten Abruf werden geladen (wenn Wallet gespeichert wird).</li>
        </ul>
      </section>

      {summary && show.realized && (
        <section className="mt-8">
          <h2 className="text-xl font-semibold">Übersicht</h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-2">
            <div className="border border-gray-200 p-3 rounded"><div>Realisierter PnL (EUR)</div><strong>{summary.totals.realized_eur.toFixed(2)}</strong></div>
            <div className="border border-gray-200 p-3 rounded"><div>Funding (EUR)</div><strong>{summary.totals.funding_eur.toFixed(2)}</strong></div>
            <div className="border border-gray-200 p-3 rounded"><div>Fees (EUR)</div><strong>{summary.totals.fees_eur.toFixed(2)}</strong></div>
          </div>
          <div className="h-80 mt-4">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={summary.pnlSeries} margin={{ left: 8, right: 8, top: 10, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tickFormatter={(d) => dayjs(d).format('MM-DD')} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="realized" stroke="#22c55e" dot={false} name="Realisiert" />
                <Line type="monotone" dataKey="funding" stroke="#2563eb" dot={false} name="Funding" />
                <Line type="monotone" dataKey="fees" stroke="#ef4444" dot={false} name="Fees" />
                <Line type="monotone" dataKey="cumulative" stroke="#0ea5e9" dot={false} name="Kumuliert" />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-3 space-x-2">
            <a href={`/api/export?wallet=${encodeURIComponent(wallet)}&type=transactions_csv`}><button className="px-3 py-2 border rounded">Transaktionen CSV</button></a>
            <a href={`/api/export?wallet=${encodeURIComponent(wallet)}&type=funding_csv`}><button className="px-3 py-2 border rounded">Funding CSV</button></a>
            <a href={`/api/export?wallet=${encodeURIComponent(wallet)}&type=fees_csv`}><button className="px-3 py-2 border rounded">Fees CSV</button></a>
            <a href={`/api/export?wallet=${encodeURIComponent(wallet)}&type=summary_csv`}><button className="px-3 py-2 border rounded">Summary CSV</button></a>
            <a href={`/api/export?wallet=${encodeURIComponent(wallet)}&type=xlsx`}><button className="px-3 py-2 border rounded">Excel</button></a>
            <a href={`/api/export?wallet=${encodeURIComponent(wallet)}&type=pdf`}><button className="px-3 py-2 border rounded">PDF</button></a>
          </div>
        </section>
      )}

      {summary && show.tax && (
        <section className="mt-8">
          <h2 className="text-xl font-semibold">Steuersimulation</h2>
          <div className="flex gap-2 items-center">
            <label>Brutto-Jahreseinkommen (ohne Trading, EUR)</label>
            <input className="w-40 border rounded px-2 py-1" value={baseIncome} onChange={(e) => setBaseIncome(e.target.value)} />
            <button className="px-3 py-2 border rounded" onClick={onSimulate}>Simulieren</button>
            <a href={`/api/checklist?wallet=${encodeURIComponent(wallet)}&year=${new Date().getFullYear()}&baseIncome=${Number(baseIncome) || 0}`}><button className="px-3 py-2 border rounded">Steuer-Checkliste PDF</button></a>
          </div>
          {tax && (
            <div className="mt-3">
              <div>Steuer ohne Trading: <strong>{tax.withoutTrading.totalTax.toFixed(2)} EUR</strong></div>
              <div>Steuer mit Trading: <strong>{tax.withTrading.totalTax.toFixed(2)} EUR</strong></div>
              <div>Steuerlast auf Trading-Gewinn: <strong>{tax.tradingDelta.toFixed(2)} EUR</strong></div>
            </div>
          )}
        </section>
      )}

      {positions.length > 0 && show.positions && (
        <section className="mt-8">
          <h2 className="text-xl font-semibold">Offene Positionen</h2>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr>
                  <th className="text-left">Symbol</th>
                  <th className="text-right">Size</th>
                  <th className="text-right">Entry</th>
                  <th className="text-right">Mark</th>
                  <th className="text-right">uPnL EUR</th>
                </tr>
              </thead>
              <tbody>
                {positions.map((p) => (
                  <tr key={p.id}>
                    <td>{p.symbol}</td>
                    <td className="text-right">{p.size}</td>
                    <td className="text-right">{p.entryPrice.toFixed(2)}</td>
                    <td className="text-right">{p.markPrice.toFixed(2)}</td>
                    <td className="text-right">{p.unrealizedPnlEUR.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {summary?.equitySeries && show.equity && (
        <section className="mt-8">
          <h2 className="text-xl font-semibold">Equity vs. Invested</h2>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={summary.equitySeries} margin={{ left: 8, right: 8, top: 10, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tickFormatter={(d) => dayjs(d).format('MM-DD')} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="equity" stroke="#0ea5e9" dot={false} name="Equity" />
                <Line type="monotone" dataKey="invested" stroke="#a855f7" dot={false} name="Invested" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </section>
      )}

      {summary?.drawdownSeries && show.equity && (
        <section className="mt-8">
          <h2 className="text-xl font-semibold">Drawdown</h2>
          <div className="h-60">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={summary.drawdownSeries} margin={{ left: 8, right: 8, top: 10, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tickFormatter={(d) => dayjs(d).format('MM-DD')} />
                <YAxis tickFormatter={(v) => (v * 100).toFixed(0) + '%'} />
                <Tooltip formatter={(v: any) => [(v * 100).toFixed(2) + '%', 'Drawdown']} />
                <Line type="monotone" dataKey="drawdown" stroke="#ef4444" dot={false} name="Drawdown" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </section>
      )}

      {show.benchmark && (
        <section className="mt-8">
          <h2 className="text-xl font-semibold">Benchmark-Vergleich (einfach)</h2>
          <div className="flex gap-2 items-center">
            <label>Tägliche Benchmark-Rendite (%)</label>
            <input className="w-28 border rounded px-2 py-1" value={benchDaily} onChange={(e) => setBenchDaily(e.target.value)} />
          </div>
          {summary?.equitySeries && (
            <div className="h-60 mt-3">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={summary.equitySeries.map((p: any, i: number) => ({ ...p, bench: Math.pow(1 + (Number(benchDaily) || 0) / 100, i) }))}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" tickFormatter={(d) => dayjs(d).format('MM-DD')} />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="equity" stroke="#0ea5e9" dot={false} name="Equity" />
                  <Line type="monotone" dataKey="bench" stroke="#16a34a" dot={false} name="Benchmark (normiert)" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </section>
      )}

      <section style={{ marginTop: 32 }}>
        <h2>Manuelle Einzahlungen</h2>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
          <select value={manualType} onChange={(e) => setManualType(e.target.value as any)}>
            <option value="deposit">Deposit</option>
            <option value="withdrawal">Withdrawal</option>
          </select>
          <input type="date" value={manualDate} onChange={(e) => setManualDate(e.target.value)} />
          <input type="number" placeholder="Betrag (EUR)" value={manualAmount} onChange={(e) => setManualAmount(e.target.value)} />
          <button disabled={!wallet || !manualDate || !manualAmount} onClick={async () => {
            const res = await fetch('/api/manual-entry', {
              method: 'POST', headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ walletAddress: wallet.trim(), date: manualDate, category: manualType, amountEUR: Number(manualAmount) })
            });
            if (res.ok) setResult({ ok: true, txCreated: 1, fundingCreated: 0 });
          }}>Speichern</button>
        </div>
      </section>

      {tx.length > 0 && (
        <section className="mt-8">
          <h2 className="text-xl font-semibold">Transaktionen</h2>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr>
                  <th className="text-left">Zeit</th>
                  <th className="text-left">Kategorie</th>
                  <th className="text-left">Symbol</th>
                  <th className="text-right">USDC</th>
                  <th className="text-right">EUR</th>
                </tr>
              </thead>
              <tbody>
                {tx.slice(-500).map((r) => (
                  <tr key={r.id}>
                    <td>{dayjs(r.timestamp).format('YYYY-MM-DD HH:mm')}</td>
                    <td>{r.category}</td>
                    <td>{r.symbol}</td>
                    <td className="text-right">{r.amountUSDC.toFixed(2)}</td>
                    <td className="text-right">{r.amountEUR.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {funds.length > 0 && (
        <section className="mt-8">
          <h2 className="text-xl font-semibold">Funding</h2>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr>
                  <th className="text-left">Zeit</th>
                  <th className="text-left">Symbol</th>
                  <th className="text-right">USDC</th>
                  <th className="text-right">EUR</th>
                </tr>
              </thead>
              <tbody>
                {funds.slice(-500).map((r) => (
                  <tr key={r.id}>
                    <td>{dayjs(r.timestamp).format('YYYY-MM-DD HH:mm')}</td>
                    <td>{r.symbol}</td>
                    <td className="text-right">{r.amountUSDC.toFixed(2)}</td>
                    <td className="text-right">{r.amountEUR.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      <section className="mt-8">
        <h2 className="text-xl font-semibold">Rates CSV Upload (Fallback)</h2>
        <p className="text-gray-600 text-sm">CSV Format: date,usd_eur (e.g., 2025-09-24,0.92)</p>
        <textarea id="ratesCsv" className="w-full border rounded p-2 mt-2" rows={5} placeholder="date,usd_eur"></textarea>
        <button className="mt-2 px-3 py-2 border rounded" onClick={async () => {
          const csv = (document.getElementById('ratesCsv') as HTMLTextAreaElement)?.value || '';
          await fetch('/api/rates-upload', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ csv }) });
        }}>Upload</button>
      </section>
    </main>
  );
}
