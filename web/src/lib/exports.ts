export function toCsv(rows: Array<Record<string, any>>): string {
  if (!rows.length) return '';
  const headers = Array.from(
    rows.reduce<Set<string>>((s, r) => {
      Object.keys(r).forEach((k) => s.add(k));
      return s;
    }, new Set())
  );
  const esc = (v: any) => {
    const s = String(v ?? '');
    return /[",\n]/.test(s) ? '"' + s.replaceAll('"', '""') + '"' : s;
  };
  const lines = [headers.join(',')];
  for (const r of rows) {
    lines.push(headers.map((h) => esc(r[h])).join(','));
  }
  return lines.join('\n');
}

export async function toExcel(sheets: Record<string, Array<Record<string, any>>>): Promise<Uint8Array> {
  const XLSX = await import('xlsx');
  const wb = XLSX.utils.book_new();
  for (const [name, rows] of Object.entries(sheets)) {
    const ws = XLSX.utils.json_to_sheet(rows);
    XLSX.utils.book_append_sheet(wb, ws, name.slice(0, 31));
  }
  const out = XLSX.write(wb, { type: 'array', bookType: 'xlsx' });
  return new Uint8Array(out);
}

export async function toPdf(summary: {
  title: string;
  totals: Record<string, number>;
  notes?: string[];
  positions?: Array<{ symbol: string; size: number; entryPrice: number; markPrice: number; upnlEUR?: number }>;
}): Promise<Uint8Array> {
  const PDFDocument = (await import('pdfkit')).default || (await import('pdfkit'));
  const doc: any = new (PDFDocument as any)({ size: 'A4', margin: 40 });
  const chunks: Uint8Array[] = [] as any;
  return await new Promise<Uint8Array>((resolve, reject) => {
    doc.on('data', (d: Buffer) => chunks.push(new Uint8Array(d)));
    doc.on('end', () => {
      const len = chunks.reduce((a, b) => a + b.byteLength, 0);
      const out = new Uint8Array(len);
      let off = 0;
      for (const c of chunks) {
        out.set(c, off);
        off += c.byteLength;
      }
      resolve(out);
    });
    doc.on('error', reject);

    // Header
    doc.rect(40, 40, 8, 8).fill('#0ea5e9').stroke();
    doc.fillColor('#000');
    doc.fontSize(18).text(summary.title, 56, 36, { underline: true });
    doc.moveDown();
    doc.fontSize(12).text('Totals (EUR):');
    doc.moveDown(0.5);
    for (const [k, v] of Object.entries(summary.totals)) {
      doc.text(`${k}: ${v.toFixed(2)}`);
    }
    if (summary.positions?.length) {
      doc.moveDown();
      doc.text('Open Positions (snapshot):');
      doc.moveDown(0.3);
      const cols = [
        { key: 'symbol', w: 100 },
        { key: 'size', w: 80 },
        { key: 'entry', w: 80 },
        { key: 'mark', w: 80 },
        { key: 'upnl', w: 100 },
      ];
      const startX = 40;
      let x = startX;
      const y0 = doc.y;
      const header = ['Symbol', 'Size', 'Entry', 'Mark', 'uPnL EUR'];
      header.forEach((h, i) => {
        doc.text(h, x, y0);
        x += cols[i].w;
      });
      doc.moveDown(0.2);
      summary.positions.slice(0, 20).forEach((p) => {
        let xx = startX;
        const row = [
          p.symbol,
          String(p.size),
          p.entryPrice.toFixed(2),
          p.markPrice.toFixed(2),
          (p.upnlEUR ?? (p.size * (p.markPrice - p.entryPrice))).toFixed(2),
        ];
        const yy = doc.y;
        row.forEach((cell, i) => {
          doc.text(cell, xx, yy);
          xx += cols[i].w;
        });
        doc.moveDown(0.2);
      });
    }
    if (summary.notes?.length) {
      doc.moveDown();
      doc.text('Notes:');
      for (const n of summary.notes) doc.text(`• ${n}`);
    }
    doc.end();
  });
}
