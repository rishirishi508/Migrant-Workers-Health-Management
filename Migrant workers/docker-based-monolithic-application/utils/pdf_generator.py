import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
import base64
from datetime import datetime

def generate_health_card_pdf(worker_data, qr_code_base64):
    """
    Generate a PDF health card for a worker
    
    Args:
        worker_data (dict): Worker information from database
        qr_code_base64 (str): Base64 encoded QR code image
    
    Returns:
        io.BytesIO: PDF file buffer
    """
    buffer = io.BytesIO()
    
    # Create the PDF document
    doc = SimpleDocTemplate(buffer, 
                           pagesize=A4,
                           rightMargin=72,
                           leftMargin=72,
                           topMargin=72,
                           bottomMargin=18)
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#2563eb')
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.HexColor('#374151')
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=6,
        textColor=colors.HexColor('#4b5563')
    )
    
    emergency_style = ParagraphStyle(
        'Emergency',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=6,
        textColor=colors.HexColor('#dc2626'),
        backColor=colors.HexColor('#fef2f2'),
        borderColor=colors.HexColor('#dc2626'),
        borderWidth=1,
        borderPadding=10
    )
    
    # Build the document content
    story = []
    
    # Title
    story.append(Paragraph("DIGITAL HEALTH CARD", title_style))
    story.append(Spacer(1, 20))
    
    # Header information table
    header_data = [
        ['Worker ID:', worker_data.get('worker_id', 'N/A'), 'Issue Date:', datetime.now().strftime('%Y-%m-%d')],
        ['Blood Group:', worker_data.get('blood_group', 'N/A'), 'Card Version:', '1.0']
    ]
    
    header_table = Table(header_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 1.5*inch])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#374151')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb'))
    ]))
    
    story.append(header_table)
    story.append(Spacer(1, 20))
    
    # Personal Information Section
    story.append(Paragraph("PERSONAL INFORMATION", header_style))
    
    personal_data = [
        ['Full Name:', worker_data.get('name', 'N/A')],
        ['Age:', f"{worker_data.get('age', 'N/A')} years"],
        ['Gender:', worker_data.get('gender', 'N/A')],
        ['Occupation:', worker_data.get('occupation', 'N/A')],
        ['Contact:', worker_data.get('contact', 'N/A')],
        ['Height:', f"{worker_data.get('height', 'N/A')} cm"],
        ['Weight:', f"{worker_data.get('weight', 'N/A')} kg"]
    ]
    
    personal_table = Table(personal_data, colWidths=[2*inch, 4*inch])
    personal_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1f5f9')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#374151')),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb'))
    ]))
    
    story.append(personal_table)
    story.append(Spacer(1, 20))
    
    # Emergency Contact Section
    story.append(Paragraph("EMERGENCY CONTACT", header_style))
    
    emergency_data = [
        ['Contact Name:', worker_data.get('relation_name', 'N/A')],
        ['Relationship:', worker_data.get('relation_type', 'N/A')],
        ['Phone Number:', worker_data.get('relation_phone', 'N/A')]
    ]
    
    emergency_table = Table(emergency_data, colWidths=[2*inch, 4*inch])
    emergency_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fef2f2')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#dc2626')),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 2, colors.HexColor('#dc2626'))
    ]))
    
    story.append(emergency_table)
    story.append(Spacer(1, 20))
    
    # QR Code Section
    if qr_code_base64:
        story.append(Paragraph("DIGITAL IDENTIFICATION", header_style))
        
        # Decode base64 QR code
        qr_code_data = base64.b64decode(qr_code_base64)
        qr_buffer = io.BytesIO(qr_code_data)
        
        # Create QR code image
        qr_image = Image(qr_buffer, width=2*inch, height=2*inch)
        
        # QR code table for centering
        qr_data = [[qr_image, 'Scan this QR code for quick access to health records.\n\nPresent this card to healthcare providers for identification.']]
        qr_table = Table(qr_data, colWidths=[2.5*inch, 3.5*inch])
        qr_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (1, 0), (1, 0), 10),
            ('TEXTCOLOR', (1, 0), (1, 0), colors.HexColor('#6b7280'))
        ]))
        
        story.append(qr_table)
        story.append(Spacer(1, 20))
    
    # Medical Information Notice
    story.append(Paragraph("MEDICAL INFORMATION NOTICE", header_style))
    
    notice_text = """
    <b>Privacy Protection:</b> This health card contains basic identification information only. 
    Complete medical records are securely stored in our digital system and require proper 
    authorization to access.<br/><br/>
    
    <b>Healthcare Provider Instructions:</b><br/>
    • Scan QR code to verify worker identity<br/>
    • Request patient consent for medical record access<br/>
    • Use emergency protocols only when patient cannot provide consent<br/>
    • All access is logged and audited for compliance<br/><br/>
    
    <b>For Emergencies:</b> Healthcare providers may access records using break-glass 
    protocols. Emergency access will trigger notifications to patient and regulatory bodies.
    """
    
    story.append(Paragraph(notice_text, body_style))
    story.append(Spacer(1, 20))
    
    # Footer information
    footer_data = [
        ['System:', 'Digital Health Records for Migrant Workers'],
        ['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        ['Valid Until:', 'Card does not expire (subject to system updates)'],
        ['Support:', 'support@healthcare-plus.com | +1 (555) 123-4567']
    ]
    
    footer_table = Table(footer_data, colWidths=[1.5*inch, 4.5*inch])
    footer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f9fafb')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#6b7280')),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb'))
    ]))
    
    story.append(footer_table)
    
    # Build the PDF
    doc.build(story)
    
    # Return the buffer
    buffer.seek(0)
    return buffer

def generate_medical_report_pdf(worker_data, medical_records, doctor_data=None):
    """
    Generate a comprehensive medical report PDF
    
    Args:
        worker_data (dict): Worker information
        medical_records (list): List of medical record dictionaries
        doctor_data (dict): Doctor information (optional)
    
    Returns:
        io.BytesIO: PDF file buffer
    """
    buffer = io.BytesIO()
    
    doc = SimpleDocTemplate(buffer, 
                           pagesize=A4,
                           rightMargin=72,
                           leftMargin=72,
                           topMargin=72,
                           bottomMargin=72)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1f2937')
    )
    
    story = []
    
    # Title
    story.append(Paragraph("MEDICAL HISTORY REPORT", title_style))
    story.append(Spacer(1, 20))
    
    # Patient Information
    patient_info = f"""
    <b>Patient:</b> {worker_data.get('name', 'N/A')}<br/>
    <b>Worker ID:</b> {worker_data.get('worker_id', 'N/A')}<br/>
    <b>Age:</b> {worker_data.get('age', 'N/A')} years<br/>
    <b>Gender:</b> {worker_data.get('gender', 'N/A')}<br/>
    <b>Blood Group:</b> {worker_data.get('blood_group', 'N/A')}<br/>
    <b>Report Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    if doctor_data:
        patient_info += f"""<br/>
        <b>Attending Physician:</b> Dr. {doctor_data.get('name', 'N/A')}<br/>
        <b>Specialization:</b> {doctor_data.get('specialization', 'N/A')}
        """
    
    story.append(Paragraph(patient_info, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Medical Records Table
    if medical_records:
        story.append(Paragraph("MEDICAL HISTORY", styles['Heading2']))
        
        # Table headers
        table_data = [['Date', 'Type', 'Diagnosis', 'Treatment', 'Risk Level']]
        
        # Add medical records
        for record in medical_records:
            table_data.append([
                record.get('created_at', 'N/A'),
                record.get('record_type', 'N/A'),
                record.get('diagnosis', 'N/A')[:50] + '...' if len(record.get('diagnosis', '')) > 50 else record.get('diagnosis', 'N/A'),
                record.get('treatment', 'N/A')[:50] + '...' if len(record.get('treatment', '')) > 50 else record.get('treatment', 'N/A'),
                record.get('risk_level', 'N/A')
            ])
        
        medical_table = Table(table_data, colWidths=[1*inch, 1.2*inch, 1.8*inch, 1.8*inch, 0.8*inch])
        medical_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#374151')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9fafb')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb'))
        ]))
        
        story.append(medical_table)
    else:
        story.append(Paragraph("No medical records found.", styles['Normal']))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_system_report_pdf(stats_data, break_glass_events=None):
    """
    Generate system statistics report PDF for administrators
    
    Args:
        stats_data (dict): System statistics
        break_glass_events (list): List of emergency access events
    
    Returns:
        io.BytesIO: PDF file buffer
    """
    buffer = io.BytesIO()
    
    doc = SimpleDocTemplate(buffer, 
                           pagesize=A4,
                           rightMargin=72,
                           leftMargin=72,
                           topMargin=72,
                           bottomMargin=72)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1f2937')
    )
    
    story.append(Paragraph("SYSTEM ADMINISTRATION REPORT", title_style))
    story.append(Spacer(1, 20))
    
    # System Statistics
    stats_info = f"""
    <b>Report Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
    <b>Total Workers:</b> {stats_data.get('total_workers', 0)}<br/>
    <b>Workers Treated:</b> {stats_data.get('treated_workers', 0)}<br/>
    <b>Active Doctors:</b> {stats_data.get('total_doctors', 0)}<br/>
    <b>Emergency Access Events:</b> {len(break_glass_events) if break_glass_events else 0}
    """
    
    story.append(Paragraph(stats_info, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Emergency Access Events
    if break_glass_events:
        story.append(Paragraph("EMERGENCY ACCESS EVENTS", styles['Heading2']))
        
        table_data = [['Date/Time', 'Doctor', 'Worker ID', 'Reason']]
        
        for event in break_glass_events[:20]:  # Limit to 20 most recent
            table_data.append([
                event.get('access_time', 'N/A'),
                event.get('doctor_name', 'N/A'),
                event.get('worker_id', 'N/A'),
                event.get('reason', 'N/A')[:100] + '...' if len(event.get('reason', '')) > 100 else event.get('reason', 'N/A')
            ])
        
        events_table = Table(table_data, colWidths=[1.2*inch, 1.5*inch, 1*inch, 2.8*inch])
        events_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fef2f2')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#fecaca'))
        ]))
        
        story.append(events_table)
    
    doc.build(story)
    buffer.seek(0)
    return buffer