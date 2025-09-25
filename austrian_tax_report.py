"""
Austrian Tax Report Generator for Hyperliquid Trading Data
Generates PDF report and CSV files according to Austrian tax law 2025
"""

import os
import json
import zipfile
import hashlib
import shutil
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Any
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak

class AustrianTaxCalculator:
    """Austrian tax calculator with 2025 tax brackets"""
    
    # Austrian tax brackets 2025
    TAX_BRACKETS_2025 = [
        (13_308, 0.00),    # bis 13.308 € → 0%
        (21_617, 0.20),    # bis 21.617 € → 20%
        (35_836, 0.30),    # bis 35.836 € → 30%
        (69_166, 0.40),    # bis 69.166 € → 40%
        (103_072, 0.48),   # bis 103.072 € → 48%
        (1_000_000, 0.50), # bis 1.000.000 € → 50%
        (float('inf'), 0.55) # über 1.000.000 € → 55%
    ]
    
    @classmethod
    def calculate_progressive_tax(cls, income_eur: float) -> Tuple[float, List[Dict]]:
        """
        Calculate progressive Austrian income tax for 2025
        Returns: (total_tax, breakdown_list)
        """
        if income_eur <= 0:
            return 0.0, []
        
        total_tax = 0.0
        breakdown = []
        remaining_income = income_eur
        previous_threshold = 0
        
        for threshold, rate in cls.TAX_BRACKETS_2025:
            if remaining_income <= 0:
                break
                
            bracket_size = min(remaining_income, threshold - previous_threshold)
            bracket_tax = bracket_size * rate
            total_tax += bracket_tax
            
            if bracket_size > 0:
                breakdown.append({
                    'bracket_min': previous_threshold,
                    'bracket_max': min(threshold, income_eur),
                    'bracket_income': bracket_size,
                    'rate': rate,
                    'bracket_tax': bracket_tax
                })
            
            remaining_income -= bracket_size
            previous_threshold = threshold
            
            if threshold == float('inf'):
                break
        
        return total_tax, breakdown

class AustrianTaxReportGenerator:
    """Generates Austrian tax reports for Hyperliquid trading data"""
    
    def __init__(self, wallet_address: str, yearly_income: float = 0.0, tax_year: int = 2025):
        self.wallet_address = wallet_address
        self.yearly_income = yearly_income
        self.tax_year = tax_year
        self.tax_calc = AustrianTaxCalculator()
        self.report_data = {}
        
    def prepare_csv_data(self, trades_df: pd.DataFrame, funding_df: pd.DataFrame, 
                        transfers_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Prepare structured CSV data according to Austrian requirements"""
        
        csv_data = {}
        
        # 1. Trades CSV - Realized P&L and fees
        if not trades_df.empty:
            trades_csv = trades_df.copy()
            trades_csv = trades_csv.rename(columns={
                'timestamp': 'closing_date',
                'closed_pnl': 'realized_pnl_usd',
                'closed_pnl_eur': 'realized_pnl_eur',
                'fee': 'fee_usd',
                'fee_eur': 'fee_eur'
            })
            
            # Add fallback indicator
            trades_csv['ecb_rate_source'] = trades_csv.apply(
                lambda row: 'ECB_DAILY' if pd.notna(row.get('usd_eur_rate')) else 'FALLBACK', axis=1
            )
            
            csv_data['trades'] = trades_csv[['closing_date', 'coin', 'side', 'size', 'price', 
                                           'realized_pnl_usd', 'realized_pnl_eur', 
                                           'fee_usd', 'fee_eur', 'usd_eur_rate', 'ecb_rate_source']]
        
        # 2. Fees CSV - All trading fees
        if not trades_df.empty:
            fees_csv = trades_df[trades_df['fee'] != 0].copy()
            fees_csv = fees_csv.rename(columns={
                'timestamp': 'date',
                'fee': 'fee_usd',
                'fee_eur': 'fee_eur'
            })
            fees_csv['fee_type'] = 'TRADING_FEE'
            fees_csv['ecb_rate_source'] = fees_csv.apply(
                lambda row: 'ECB_DAILY' if pd.notna(row.get('usd_eur_rate')) else 'FALLBACK', axis=1
            )
            
            csv_data['fees'] = fees_csv[['date', 'coin', 'fee_type', 'fee_usd', 'fee_eur', 
                                       'usd_eur_rate', 'ecb_rate_source']]
        
        # 3. Funding CSV
        if not funding_df.empty:
            funding_csv = funding_df.copy()
            funding_csv = funding_csv.rename(columns={
                'timestamp': 'date',
                'funding_payment': 'funding_usd',
                'funding_payment_eur': 'funding_eur'
            })
            
            # Format funding rate as percentage
            funding_csv['funding_rate_percent'] = (funding_csv['funding_rate'] * 100).round(4)
            funding_csv['funding_rate_formatted'] = funding_csv['funding_rate_percent'].apply(lambda x: f"{x:.4f}%")
            
            funding_csv['funding_type'] = funding_csv['funding_usd'].apply(
                lambda x: 'FUNDING_PAID' if x < 0 else 'FUNDING_RECEIVED'
            )
            funding_csv['ecb_rate_source'] = funding_csv.apply(
                lambda row: 'ECB_DAILY' if pd.notna(row.get('usd_eur_rate')) else 'FALLBACK', axis=1
            )
            
            csv_data['funding'] = funding_csv[['date', 'coin', 'funding_type', 'funding_rate_formatted',
                                             'funding_usd', 'funding_eur', 'usd_eur_rate', 'ecb_rate_source']]
        
        # 4. Deposits/Withdrawals CSV
        if not transfers_df.empty:
            transfers_csv = transfers_df.copy()
            transfers_csv = transfers_csv.rename(columns={
                'timestamp': 'date',
                'amount': 'amount_usd',
                'amount_eur': 'amount_eur'
            })
            transfers_csv['transfer_type'] = transfers_csv['amount_usd'].apply(
                lambda x: 'DEPOSIT' if x > 0 else 'WITHDRAWAL'
            )
            transfers_csv['ecb_rate_source'] = transfers_csv.apply(
                lambda row: 'ECB_DAILY' if pd.notna(row.get('usd_eur_rate')) else 'FALLBACK', axis=1
            )
            
            csv_data['deposits_withdrawals'] = transfers_csv[['date', 'type', 'transfer_type', 
                                                           'amount_usd', 'amount_eur', 
                                                           'usd_eur_rate', 'ecb_rate_source']]
        
        return csv_data
    
    def calculate_austrian_tax_summary(self, trades_df: pd.DataFrame, funding_df: pd.DataFrame) -> Dict:
        """Calculate Austrian tax summary including user's other income"""
        
        # Calculate totals in EUR
        total_realized_pnl_eur = trades_df['closed_pnl_eur'].sum() if not trades_df.empty and 'closed_pnl_eur' in trades_df.columns else 0
        total_fees_eur = abs(trades_df['fee_eur'].sum()) if not trades_df.empty and 'fee_eur' in trades_df.columns else 0
        
        funding_paid_eur = abs(funding_df[funding_df['funding_payment_eur'] < 0]['funding_payment_eur'].sum()) if not funding_df.empty and 'funding_payment_eur' in funding_df.columns else 0
        funding_received_eur = funding_df[funding_df['funding_payment_eur'] > 0]['funding_payment_eur'].sum() if not funding_df.empty and 'funding_payment_eur' in funding_df.columns else 0
        
        # Calculate raw trading result (can be negative)
        raw_trading_result_eur = total_realized_pnl_eur + funding_received_eur - total_fees_eur - funding_paid_eur
        
        # CRITICAL: Austrian tax law - only profits are taxable, losses don't reduce other income
        taxable_trading_profit_eur = max(0, raw_trading_result_eur)
        
        # Total taxable income (base income + only positive trading profits)
        total_taxable_income_eur = self.yearly_income + taxable_trading_profit_eur
        
        # Calculate taxes correctly - separate calculations
        tax_lohn_only, _ = self.tax_calc.calculate_progressive_tax(max(0, self.yearly_income))
        tax_with_trading, tax_breakdown = self.tax_calc.calculate_progressive_tax(max(0, total_taxable_income_eur))
        trading_tax = max(0, tax_with_trading - tax_lohn_only)  # Never negative
        
        return {
            'yearly_income_eur': self.yearly_income,
            'raw_trading_result_eur': raw_trading_result_eur,
            'taxable_trading_profit_eur': taxable_trading_profit_eur,
            'total_taxable_income_eur': total_taxable_income_eur,
            'total_realized_pnl_eur': total_realized_pnl_eur,
            'total_fees_eur': total_fees_eur,
            'funding_paid_eur': funding_paid_eur,
            'funding_received_eur': funding_received_eur,
            'tax_lohn_only': tax_lohn_only,
            'trading_tax': trading_tax,
            'tax_with_trading': tax_with_trading,
            'tax_breakdown': tax_breakdown
        }
    
    def create_summary_csv(self, tax_summary: Dict, trades_df: pd.DataFrame, 
                          funding_df: pd.DataFrame, transfers_df: pd.DataFrame) -> pd.DataFrame:
        """Create summary CSV with KPIs"""
        
        summary_data = {
            'metric': [
                'Tax Year',
                'Lohn-Einkommen (EUR)',
                'Raw Trading Result (EUR)',
                'Taxable Trading Profit (EUR)', 
                'Total Taxable Income (EUR)',
                'Total Trades Count',
                'Total Realized P&L (EUR)',
                'Total Trading Fees (EUR)', 
                'Total Funding Paid (EUR)',
                'Total Funding Received (EUR)',
                'Total Deposits (EUR)',
                'Total Withdrawals (EUR)',
                'Tax Lohn Only (EUR)',
                'Trading Tax (EUR)',
                'Total Tax (EUR)',
                'Effective Tax Rate (%)'
            ],
            'value': [
                str(self.tax_year),
                f"{tax_summary['yearly_income_eur']:.4f}",
                f"{tax_summary['raw_trading_result_eur']:.4f}",
                f"{tax_summary['taxable_trading_profit_eur']:.4f}",
                f"{tax_summary['total_taxable_income_eur']:.4f}",
                len(trades_df) if not trades_df.empty else 0,
                f"{tax_summary['total_realized_pnl_eur']:.4f}",
                f"{tax_summary['total_fees_eur']:.4f}",
                f"{tax_summary['funding_paid_eur']:.4f}",
                f"{tax_summary['funding_received_eur']:.4f}",
                f"{transfers_df[transfers_df['amount_eur'] > 0]['amount_eur'].sum():.4f}" if not transfers_df.empty and 'amount_eur' in transfers_df.columns else "0.0000",
                f"{abs(transfers_df[transfers_df['amount_eur'] < 0]['amount_eur'].sum()):.4f}" if not transfers_df.empty and 'amount_eur' in transfers_df.columns else "0.0000",
                f"{tax_summary['tax_lohn_only']:.4f}",
                f"{tax_summary['trading_tax']:.4f}",
                f"{tax_summary['tax_with_trading']:.4f}",
                f"{(tax_summary['trading_tax'] / max(tax_summary['taxable_trading_profit_eur'], 1) * 100):.2f}" if tax_summary['taxable_trading_profit_eur'] > 0 else "0.00"
            ]
        }
        
        return pd.DataFrame(summary_data)
    
    def perform_plausibility_check(self, trades_df: pd.DataFrame, funding_df: pd.DataFrame, 
                                  account_state: Dict) -> Dict:
        """Perform plausibility checks on the data"""
        
        checks = {}
        
        if not trades_df.empty and not funding_df.empty:
            # Calculate expected equity change
            realized_pnl = trades_df['closed_pnl'].sum() if 'closed_pnl' in trades_df.columns else 0
            funding_total = funding_df['funding_payment'].sum() if 'funding_payment' in funding_df.columns else 0
            fees_total = trades_df['fee'].sum() if 'fee' in trades_df.columns else 0
            
            expected_change = realized_pnl + funding_total - abs(fees_total)
            
            checks['calculated_pnl_change'] = expected_change
            checks['plausibility_note'] = f"Expected equity Δ: ${expected_change:.2f}"
            
        return checks
    
    def generate_tax_form_guidance_pdf(self, tax_summary, filename):
        """Generate a PDF with specific Austrian tax form guidance for Steuererklärung."""
        doc = SimpleDocTemplate(filename, pagesize=letter, topMargin=50, bottomMargin=50)
        styles = getSampleStyleSheet()
        story = []
        
        # Custom styles
        title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=16, spaceAfter=20)
        heading_style = ParagraphStyle('Heading', parent=styles['Heading1'], fontSize=12, spaceAfter=10)
        section_style = ParagraphStyle('SectionHeading', parent=styles['Heading2'], fontSize=10, spaceAfter=8, textColor=colors.darkblue)
        normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=9, spaceAfter=6)
        highlight_style = ParagraphStyle('Highlight', parent=styles['Normal'], fontSize=10, spaceAfter=6, 
                                       textColor=colors.darkgreen, fontName='Helvetica-Bold')
        
        # Header
        story.append(Paragraph("🇦🇹 ÖSTERREICHISCHE STEUERERKLÄRUNG - ANLEITUNG", title_style))
        story.append(Paragraph(f"Hyperliquid Trading Report für {self.tax_year}", heading_style))
        story.append(Paragraph(f"Wallet: {self.wallet_address}", normal_style))
        story.append(Spacer(1, 20))
        
        # Tax amounts summary
        trading_result = tax_summary.get('trading_result', 0)
        taxable_profit = max(0, trading_result)  # Only positive results are taxable
        tax_with_trading = tax_summary.get('tax_with_trading', 0)
        tax_lohn_only = tax_summary.get('tax_lohn_only', 0)
        additional_tax = tax_with_trading - tax_lohn_only
        
        story.append(Paragraph("📊 BESTEUERUNGSGRUNDLAGE", section_style))
        story.append(Paragraph(f"• Trading-Ergebnis gesamt: €{trading_result:,.2f}", normal_style))
        story.append(Paragraph(f"• Zu versteuernder Gewinn: €{taxable_profit:,.2f}", highlight_style))
        story.append(Paragraph(f"• Zusätzliche Steuer: €{additional_tax:,.2f}", highlight_style))
        story.append(Spacer(1, 15))
        
        # Form E1 - Main income declaration
        story.append(Paragraph("📋 FORMULAR E1 - EINKOMMENSTEUERERKLÄRUNG", section_style))
        story.append(Paragraph("Das Formular E1 ist Ihre Hauptsteuererklärung für Einkommen:", normal_style))
        story.append(Paragraph("• Lohn-Einkommen bereits durch Arbeitgeber versteuert", normal_style))
        story.append(Paragraph("• Trading-Gewinne sind zusätzlich anzugeben", normal_style))
        story.append(Spacer(1, 10))
        
        # Form E1kv - Capital gains supplement
        story.append(Paragraph("💰 FORMULAR E1kv - KAPITALERTRÄGE", section_style))
        story.append(Paragraph("Das Formular E1kv ist speziell für Kapitalerträge und Trading-Gewinne:", normal_style))
        story.append(Paragraph(f"• Eintrag erforderlich: €{taxable_profit:,.2f}", highlight_style))
        story.append(Paragraph("• Kategorie: Sonstige Kapitalerträge", normal_style))
        story.append(Paragraph("• Quellensteuer: 0€ (da internationaler Broker)", normal_style))
        story.append(Spacer(1, 15))
        
        # Step-by-step instructions
        story.append(Paragraph("📝 SCHRITT-FÜR-SCHRITT ANLEITUNG", section_style))
        
        # Step 1
        story.append(Paragraph("1. FINANZONLINE EINLOGGEN", heading_style))
        story.append(Paragraph("• Gehen Sie zu finanzonline.bmf.gv.at", normal_style))
        story.append(Paragraph("• Loggen Sie sich mit Ihren Zugangsdaten ein", normal_style))
        story.append(Spacer(1, 8))
        
        # Step 2
        story.append(Paragraph("2. STEUERERKLÄRUNG ÖFFNEN", heading_style))
        story.append(Paragraph(f"• Wählen Sie 'Steuererklärung {self.tax_year}'", normal_style))
        story.append(Paragraph("• Öffnen Sie das Formular E1", normal_style))
        story.append(Spacer(1, 8))
        
        # Step 3
        story.append(Paragraph("3. TRADING-GEWINNE EINTRAGEN", heading_style))
        story.append(Paragraph("• Navigieren Sie zu 'Sonstige Einkünfte'", normal_style))
        story.append(Paragraph("• Wählen Sie 'Kapitalerträge (E1kv)'", normal_style))
        story.append(Paragraph(f"• Tragen Sie ein: €{taxable_profit:,.2f}", highlight_style))
        story.append(Spacer(1, 8))
        
        # Step 4
        story.append(Paragraph("4. BERECHNUNG PRÜFEN", heading_style))
        story.append(Paragraph("• Das System berechnet automatisch die zusätzliche Steuer", normal_style))
        story.append(Paragraph(f"• Erwartete zusätzliche Steuer: €{additional_tax:,.2f}", highlight_style))
        story.append(Spacer(1, 8))
        
        # Payment instructions
        story.append(Paragraph("💳 ÜBERWEISUNG AN FINANZAMT", section_style))
        if additional_tax > 0:
            story.append(Paragraph(f"BETRAG: €{additional_tax:,.2f}", highlight_style))
            story.append(Paragraph("• Empfänger: Finanzamt für Ihren Wohnbezirk", normal_style))
            story.append(Paragraph("• Verwendungszweck: Steuernummer + 'Nachzahlung EST 2024'", normal_style))
            story.append(Paragraph("• Zahlbar bis: 30. September des Folgejahres", normal_style))
        else:
            story.append(Paragraph("Keine Nachzahlung erforderlich", normal_style))
        story.append(Spacer(1, 15))
        
        # Important notes
        story.append(Paragraph("⚠️ WICHTIGE HINWEISE", section_style))
        story.append(Paragraph("• Verluste können das Lohn-Einkommen NICHT reduzieren", normal_style))
        story.append(Paragraph("• Nur positive Trading-Ergebnisse sind steuerpflichtig", normal_style))
        story.append(Paragraph("• FIFO-Methode wurde für die Berechnung verwendet", normal_style))
        story.append(Paragraph("• Bei Fragen wenden Sie sich an Ihren Steuerberater", normal_style))
        story.append(Spacer(1, 15))
        
        # Footer
        story.append(Paragraph("Generiert am: " + datetime.now().strftime("%d.%m.%Y %H:%M:%S"), 
                             ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey)))
        
        # Build PDF
        doc.build(story)
        return filename
    
    def generate_pdf_report(self, csv_data: Dict[str, pd.DataFrame], tax_summary: Dict,
                           plausibility: Dict, account_state: Dict, output_file: str):
        """Generate comprehensive PDF tax report for Austria"""
        
        doc = SimpleDocTemplate(output_file, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Custom styles
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'],
                                   fontSize=16, spaceAfter=30, alignment=1)
        heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'],
                                     fontSize=12, spaceAfter=12)
        
        # Title
        story.append(Paragraph(f"Österreichischer Steuerreport {self.tax_year}", title_style))
        story.append(Paragraph(f"Hyperliquid Trading - Wallet: {self.wallet_address[:10]}...{self.wallet_address[-8:]}", styles['Normal']))
        story.append(Paragraph(f"Lohn-Einkommen: € {self.yearly_income:,.2f}", styles['Normal']))
        story.append(Paragraph(f"Erstellt am: {datetime.now(timezone.utc).strftime('%d.%m.%Y %H:%M')} UTC", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Executive Summary
        story.append(Paragraph("1. Steuerliche Zusammenfassung", heading_style))
        
        summary_data = [
            ['Kennzahl', 'Betrag (EUR)'],
            ['Lohn-Einkommen', f"€ {tax_summary['yearly_income_eur']:,.2f}"],
            ['Trading-Ergebnis (roh)', f"€ {tax_summary['raw_trading_result_eur']:,.2f}"],
            ['Trading-Gewinn (steuerlich)', f"€ {tax_summary['taxable_trading_profit_eur']:,.2f}"],
            ['Gesamteinkommen (steuerpflichtig)', f"€ {tax_summary['total_taxable_income_eur']:,.2f}"],
            ['Realisierte Gewinne/Verluste', f"€ {tax_summary['total_realized_pnl_eur']:,.2f}"],
            ['Trading-Gebühren (abzugsfähig)', f"€ {tax_summary['total_fees_eur']:,.2f}"],
            ['Funding Paid (abzugsfähig)', f"€ {tax_summary['funding_paid_eur']:,.2f}"],
            ['Funding Received (Ertrag)', f"€ {tax_summary['funding_received_eur']:,.2f}"],
            ['', ''],  # Separator
            ['Steuer nur auf Lohn', f"€ {tax_summary['tax_lohn_only']:,.2f}"],
            ['Zusatzsteuer durch Trading', f"€ {tax_summary['trading_tax']:,.2f}"],
            ['Steuer gesamt (Lohn + Trading)', f"€ {tax_summary['tax_with_trading']:,.2f}"]
        ]
        
        # Add note for losses if applicable
        if tax_summary['raw_trading_result_eur'] < 0:
            summary_data.append(['Hinweis', f"Trading-Verlust mindert Lohn-Einkommen nicht"])
        
        summary_table = Table(summary_data)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Tax Calculation Details
        story.append(Paragraph("2. Österreichische Steuertabelle 2025", heading_style))
        
        tax_table_data = [['Steuerstufe (EUR)', 'Steuersatz (%)', 'Einkommen in Stufe', 'Steuer']]
        
        for bracket in tax_summary['tax_breakdown']:
            tax_table_data.append([
                f"€ {bracket['bracket_min']:,.0f} - € {bracket['bracket_max']:,.0f}",
                f"{bracket['rate']*100:.0f}%",
                f"€ {bracket['bracket_income']:,.2f}",
                f"€ {bracket['bracket_tax']:,.2f}"
            ])
        
        if tax_table_data:
            tax_table = Table(tax_table_data)
            tax_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(tax_table)
        story.append(Spacer(1, 20))
        
        # Methodology
        story.append(Paragraph("3. Methodik & Annahmen", heading_style))
        methodology_text = """
        • FIFO-Methode für Positionsschließungen
        • Trading-Gebühren sind steuerlich abzugsfähig
        • Funding Paid ist abzugsfähig, Funding Received ist steuerpflichtiger Ertrag
        • EZB-Tageskurse für USD/EUR Umrechnung (EXR/D.USD.EUR.SP00.A)
        • Zeitzone: Europe/Vienna für alle Berechnungen
        • Realisierte Gewinne/Verluste bei Positionsschließung
        • Keine Haltefristen - alle Gewinne als Einkommen steuerpflichtig
        • Progressive österreichische Einkommensteuer 2025
        """
        story.append(Paragraph(methodology_text, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Austrian Tax Treatment Notes
        story.append(Paragraph("4. Österreichische Steuerbehandlung", heading_style))
        tax_treatment_text = """
        Seit der Steuerreform sind Kryptowährungsgewinne aus Trading als Einkommen zu versteuern:
        
        • Keine Behaltefrist mehr - alle realisierten Gewinne sind sofort steuerpflichtig
        • Progressive Einkommensteuer (0% bis 55% je nach Gesamteinkommen)
        • Trading-Verluste können mit anderen Einkünften verrechnet werden
        • Trading Fees und Funding Paid = abzugsfähig; Funding Received = steuerpflichtiger Ertrag
        • Deposits sind nicht steuerpflichtig; Withdrawals sind kein Einkommen
        • Nur realisierte PnL ist steuerpflichtig (unrealisierte PnL = Info)
        """
        story.append(Paragraph(tax_treatment_text, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Account Overview
        if account_state:
            story.append(Paragraph("5. Account-Übersicht", heading_style))
            account_data = [
                ['Account Value', f"$ {account_state.get('account_value', 0):,.2f}"],
                ['Offene Positionen', str(len(account_state.get('positions', [])))],
                ['Verfügbar zum Abheben', f"$ {account_state.get('withdrawable', 0):,.2f}"],
                ['Letztes Update', account_state.get('timestamp', 'N/A')]
            ]
            
            account_table = Table(account_data)
            account_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(account_table)
            story.append(Spacer(1, 20))
        
        # Data Samples (10-20 rows from each CSV)
        for csv_name, df in csv_data.items():
            if not df.empty:
                story.append(Paragraph(f"6.{list(csv_data.keys()).index(csv_name)+1} {csv_name.title()} (Auszug - erste 10 Zeilen)", heading_style))
                
                # Show first 10 rows
                sample_df = df.head(10)
                table_data = [list(sample_df.columns)]
                
                for _, row in sample_df.iterrows():
                    table_data.append([str(val)[:20] + '...' if len(str(val)) > 20 else str(val) for val in row])
                
                sample_table = Table(table_data)
                sample_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(sample_table)
                story.append(Spacer(1, 15))
        
        # Plausibility Check
        if plausibility:
            story.append(Paragraph("7. Plausibilitätsprüfung", heading_style))
            plausibility_text = f"""
            {plausibility.get('plausibility_note', 'Keine Anmerkungen')}
            
            Hinweis: Vollständige CSV-Dateien sind im beigefügten ZIP-Archiv enthalten.
            """
            story.append(Paragraph(plausibility_text, styles['Normal']))
        
        # Build PDF
        doc.build(story)
        print(f"📄 PDF Report erstellt: {output_file}")
    
    def generate_report_package(self, trades_df: pd.DataFrame, funding_df: pd.DataFrame,
                               transfers_df: pd.DataFrame, account_state: Dict, 
                               base_filename: str) -> str:
        """Generate complete Austrian tax report package with organized folders"""
        
        print(f"🇦🇹 Generiere österreichischen Steuerreport {self.tax_year}...")
        
        # Prepare CSV data
        csv_data = self.prepare_csv_data(trades_df, funding_df, transfers_df)
        
        # Calculate tax summary
        tax_summary = self.calculate_austrian_tax_summary(trades_df, funding_df)
        
        # Create summary CSV
        summary_csv = self.create_summary_csv(tax_summary, trades_df, funding_df, transfers_df)
        csv_data['summary'] = summary_csv
        
        # Perform plausibility checks
        plausibility = self.perform_plausibility_check(trades_df, funding_df, account_state)
        
        # Generate timestamp
        vienna_time = datetime.now().strftime("%Y%m%d_%H%M")
        
        # Create main folder structure
        main_folder = f"HL_AT_{self.tax_year}_{self.wallet_address[:8]}_{vienna_time}"
        
        # Create folders
        folders = {
            'summary': os.path.join(main_folder, '01_Summary'),
            'trades': os.path.join(main_folder, '02_Trades'), 
            'funding': os.path.join(main_folder, '03_Funding'),
            'transfers': os.path.join(main_folder, '04_Transfers'),
            'pdf': os.path.join(main_folder, '05_PDF_Report')
        }
        
        # Create all folders
        for folder_path in folders.values():
            os.makedirs(folder_path, exist_ok=True)
        
        # File names
        pdf_filename = os.path.join(folders['pdf'], f"HL_tax_report_AT_{self.wallet_address[:8]}_{self.tax_year}_{vienna_time}_EuropeVienna.pdf")
        zip_filename = f"{main_folder}.zip"
        
        # Save CSV files in their respective folders
        csv_files = []
        
        # Summary folder
        if 'summary' in csv_data:
            summary_file = os.path.join(folders['summary'], "summary.csv")
            csv_data['summary'].to_csv(summary_file, index=False, encoding='utf-8')
            csv_files.append(summary_file)
            print(f"💾 Summary CSV: {summary_file}")
        
        # Trades folder  
        if 'trades' in csv_data:
            trades_file = os.path.join(folders['trades'], "trades.csv")
            csv_data['trades'].to_csv(trades_file, index=False, encoding='utf-8')
            csv_files.append(trades_file)
            print(f"💾 Trades CSV: {trades_file}")
        
        if 'fees' in csv_data:
            fees_file = os.path.join(folders['trades'], "fees.csv")
            csv_data['fees'].to_csv(fees_file, index=False, encoding='utf-8')
            csv_files.append(fees_file)
            print(f"💾 Fees CSV: {fees_file}")
        
        # Funding folder
        if 'funding' in csv_data:
            funding_file = os.path.join(folders['funding'], "funding.csv")
            csv_data['funding'].to_csv(funding_file, index=False, encoding='utf-8')
            csv_files.append(funding_file)
            print(f"💾 Funding CSV: {funding_file}")
        
        # Transfers folder
        if 'deposits_withdrawals' in csv_data:
            transfers_file = os.path.join(folders['transfers'], "deposits_withdrawals.csv")
            csv_data['deposits_withdrawals'].to_csv(transfers_file, index=False, encoding='utf-8')
            csv_files.append(transfers_file)
            print(f"💾 Transfers CSV: {transfers_file}")
        
        # Generate PDF in PDF folder
        self.generate_pdf_report(csv_data, tax_summary, plausibility, account_state, pdf_filename)
        
        # Generate Tax Form Guidance PDF
        tax_form_pdf = os.path.join(folders['pdf'], f"Ueberweisung_Finanzamt_AT_{self.wallet_address[:8]}_{self.tax_year}_{vienna_time}.pdf")
        self.generate_tax_form_guidance_pdf(tax_summary, tax_form_pdf)
        
        # Create ZIP package
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add entire folder structure
            for root, dirs, files in os.walk(main_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    archive_name = os.path.relpath(file_path, os.path.dirname(main_folder))
                    zipf.write(file_path, archive_name)
            
            # Create checksums
            checksums = {}
            for csv_file in csv_files + [pdf_filename]:
                with open(csv_file, 'rb') as f:
                    checksums[os.path.relpath(csv_file, os.path.dirname(main_folder))] = hashlib.md5(f.read()).hexdigest()
            
            # Add checksums file to main folder
            checksums_file = os.path.join(main_folder, 'checksums.txt')
            with open(checksums_file, 'w') as f:
                for file, checksum in checksums.items():
                    f.write(f"{checksum}  {file}\n")
            
            # Add checksums to zip
            zipf.write(checksums_file, os.path.relpath(checksums_file, os.path.dirname(main_folder)))
        
        print(f"📦 ZIP-Paket erstellt: {zip_filename}")
        print(f"🇦🇹 Österreichischer Steuerreport komplett!")
        
        # Clean up folder structure (keep only ZIP)
        import shutil
        try:
            shutil.rmtree(main_folder)
        except:
            pass
        
        return zip_filename
