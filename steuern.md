Updated Prompt neue Feautures die Wichtig sind steuern:
Erweitere die Analyse meiner Hyperliquid-Daten um folgende Punkte:

1. Behandle USDC als USD (1:1 Bindung).  
2. Verwende den offiziellen EZB-Tageskurs USD→EUR für das jeweilige Transaktionsdatum.  
3. Rechne ALLE Beträge (Gewinne, Verluste, Einzahlungen, normale Fees, Funding Fees) in EUR um.  
4. Erstelle am Ende eine Zusammenfassung mit den folgenden Gesamtsummen in EUR:  
   - Gesamtgewinn / -verlust  
   - Gesamte Einzahlungen  
   - Gesamt-Fees (normal)  
   - Gesamt-Funding Fees  
   - Endsaldo = Gewinn – Fees – Funding Fees  

Output:  
- Detaillierte Tabelle pro Transaktion mit: Datum, Kategorie (Gewinn, Einzahlung, Fee, Funding Fee), Betrag in USDC, EZB-Kurs, Betrag in EUR.  
- Am Ende eine kompakte Summenübersicht mit allen Kategorien.  
