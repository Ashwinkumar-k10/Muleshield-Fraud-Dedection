from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io
from datetime import datetime

def generate_pdf_report(case_data):
    """
    Generates a professional PDF report for a given MuleShield case
    using ReportLab.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1e3a8a')
    )
    section_style = ParagraphStyle(
        'SecTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1e3a8a'),
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155')
    )
    bold_body_style = ParagraphStyle(
        'BoldBodyText',
        parent=body_style,
        fontName='Helvetica-Bold'
    )
    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Code'],
        fontName='Courier',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#0f172a')
    )
    footer_style = ParagraphStyle(
        'FooterText',
        parent=body_style,
        fontSize=8,
        textColor=colors.HexColor('#64748b'),
        alignment=1 # Center
    )

    # 1. Header (Logo Text and Title)
    story.append(Paragraph("MULESHIELD PRO", ParagraphStyle('Sub', fontName='Helvetica-Bold', fontSize=10, leading=12, textColor=colors.HexColor('#2563eb'))))
    story.append(Paragraph("Enterprise Fraud Risk & Investigation Report", title_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')} | Security Classification: RESTRICTED", body_style))
    story.append(Spacer(1, 15))

    # 2. Case Information Summary Table
    story.append(Paragraph("CASE PROFILE SUMMARY", section_style))
    summary_data = [
        [Paragraph("Case Identification", bold_body_style), Paragraph(f"CASE-{case_data['account_id']}", body_style),
         Paragraph("Assigned Analyst", bold_body_style), Paragraph(case_data.get('assigned_analyst', 'System'), body_style)],
        [Paragraph("Account ID Reference", bold_body_style), Paragraph(f"#{case_data['account_id']}", body_style),
         Paragraph("Lifecycle Status", bold_body_style), Paragraph(case_data.get('status', 'NEW').upper(), bold_body_style)],
        [Paragraph("System Risk Score", bold_body_style), Paragraph(f"{case_data['risk_score']:.4f}", bold_body_style),
         Paragraph("Operational Action", bold_body_style), Paragraph(case_data['action'], body_style)],
        [Paragraph("Calibrated Decision Boundary", bold_body_style), Paragraph("0.9899", body_style),
         Paragraph("Inference Engine Status", bold_body_style), Paragraph("ACTIVE / ONLINE", body_style)]
    ]
    t_summary = Table(summary_data, colWidths=[130, 130, 130, 130])
    t_summary.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f8fafc')),
        ('BACKGROUND', (2,0), (2,-1), colors.HexColor('#f8fafc')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_summary)
    story.append(Spacer(1, 15))

    # 3. Model & Preprocessing Integrity Metrics
    story.append(Paragraph("TECHNICAL INTEGRITY METRICS & PIPELINE PATHWAY", section_style))
    metrics_data = [
        [Paragraph("Metric Dimension", bold_body_style), Paragraph("Canonical Baseline Value", bold_body_style), Paragraph("Validation Context / Methodology", bold_body_style)],
        [Paragraph("Stratified Group-Aware CV PR-AUC", body_style), Paragraph("0.8807 ± 0.0403", body_style), Paragraph("5-Fold cross-validation on 6,118 similarity clusters", body_style)],
        [Paragraph("Model Precision (Validation)", body_style), Paragraph("100.00% (1.0000)", body_style), Paragraph("Calibrated operating point boundary at 0.9899 threshold", body_style)],
        [Paragraph("Model Recall (Validation)", body_style), Paragraph("61.64% (0.6164)", body_style), Paragraph("Fraud interception rate at selected zero-false-freeze threshold", body_style)],
        [Paragraph("Model F1-Score (Validation)", body_style), Paragraph("0.7586", body_style), Paragraph("Harmonic mean of precision and recall", body_style)],
        [Paragraph("Robustness Stress-Test PR-AUC", body_style), Paragraph("0.8383", body_style), Paragraph("Under synthetic 10% random null-cell corruption", body_style)]
    ]
    t_metrics = Table(metrics_data, colWidths=[150, 140, 230])
    t_metrics.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    # Quick fix for text color in header row
    for col in range(3):
        metrics_data[0][col].style.textColor = colors.white
    story.append(t_metrics)
    story.append(Spacer(1, 15))

    # 4. TreeSHAP Attribution Drivers
    story.append(Paragraph("MODEL EXPLAINABILITY - TREESHAP ATTRIBUTION DRIVERS", section_style))
    story.append(Paragraph("The following features provided the highest positive contribution to the risk probability score:", body_style))
    story.append(Spacer(1, 5))
    
    domain_map = {
        'F994': 'Max UPI Transaction Velocity (Last 7D High-Volume Inflow)',
        'F3598': 'Customer-Induced Transaction Deviation (14D Velocity Anomaly)',
        'F3348_ismissing': 'Uninterpretable Anonymised Feature (Systemic Field Omission)',
        'F1319': 'Possible Fund-Flow-Ratio-like Signal (Outflow / Inflow Balance)',
        'F1216': 'Time-of-Day / Channel Anomaly (Non-Standard Channel)',
        'F3805': 'Transaction Volume / Balance Cap (Micro-Cap Account Anomaly)',
        'F3922': 'Uninterpretable Anonymised Feature (Activity Sub-Count)',
        'F2289_ismissing': 'Behavioural Deviation (Forced Onboarding Field)',
        'F3240_ismissing': 'Uninterpretable Anonymised Feature (Systemic Field Omission)',
        'F1813': 'Transaction Velocity / Turnover Band (Low Cumulative Turnover)'
    }
    
    drivers_data = [[Paragraph("Feature Key", bold_body_style), Paragraph("Business / Behavioral Interpretation", bold_body_style), Paragraph("Attribution Weight", bold_body_style)]]
    for idx, f in enumerate(case_data['top_shap_drivers']):
        label = domain_map.get(f, 'Behavioral Feature Signal')
        drivers_data.append([
            Paragraph(f, code_style),
            Paragraph(label, body_style),
            Paragraph("High Positive", bold_body_style)
        ])
    
    t_drivers = Table(drivers_data, colWidths=[120, 280, 120])
    t_drivers.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_drivers)
    story.append(Spacer(1, 15))

    # 5. Watchlist & Network Evidence
    story.append(Paragraph("REGULATORY & NETWORK EVIDENCE PROFILE (SIMULATED)", section_style))
    reg_flags = case_data.get('regulatory_flags', {})
    evidence_data = [
        [Paragraph("Intelligence Feed Source", bold_body_style), Paragraph("Intersection Status / Result", bold_body_style)],
        [Paragraph("I4C National Cyber Crime Reporting Portal", body_style), Paragraph(reg_flags.get('i4c_db', 'CLEAR'), bold_body_style)],
        [Paragraph("CERT-In Botnet / Malicious IP List", body_style), Paragraph(reg_flags.get('cert_in_botnet', 'CLEAR'), bold_body_style)],
        [Paragraph("RBI Caution List / blacklisted entities", body_style), Paragraph(reg_flags.get('rbi_caution_list', 'CLEAR'), bold_body_style)],
        [Paragraph("Mule Ring Association (Topology Graph)", body_style), Paragraph("MULE RING #MULE-2026-ALPHA Association (Simulated Link)", body_style)]
    ]
    t_evidence = Table(evidence_data, colWidths=[250, 270])
    t_evidence.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f8fafc')),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_evidence)
    story.append(Spacer(1, 15))

    # 6. Notes & Timeline
    story.append(Paragraph("CASE NOTES & TIMELINE", section_style))
    notes_list = case_data.get('notes', [])
    if not notes_list:
        notes_list = [{"timestamp": "2026-08-23 12:00 UTC", "analyst": "System", "text": "Initial ingestion risk evaluation completed. Risk score generated."}]
    
    notes_formatted = []
    for note in notes_list:
        notes_formatted.append(f"[{note.get('timestamp', 'UTC')}] {note.get('analyst', 'System')}: {note.get('text', '')}")
    
    notes_block = "\n".join(notes_formatted)
    story.append(Paragraph(notes_block.replace('\n', '<br/>'), code_style))
    story.append(Spacer(1, 20))

    # 7. Disclaimer
    story.append(Paragraph("<b>DEMONSTRATION & BOUNDARY DISCLAIMER:</b> MuleShield PRO is an explainable AI/ML prototype. Watchlist matches, network topologies, and CBS debit freezes are simulated demonstration interfaces. Core ML inference, target leakage controls, and Group-Aware validation metrics are fully implemented and technically verified against the project dataset.", ParagraphStyle('Disc', parent=body_style, fontSize=7, leading=9, textColor=colors.HexColor('#94a3b8'))))
    story.append(Spacer(1, 20))

    # Build Document
    doc.build(story)
    return buffer.getvalue()
