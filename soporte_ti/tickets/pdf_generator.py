from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime
from django.utils import timezone
import os
from django.conf import settings

class TicketPDFGenerator:
    def __init__(self, ticket):
        self.ticket = ticket
        self.buffer = BytesIO()
        self.pagesize = letter
        self.width, self.height = self.pagesize

    def generate_header_footer(self, canvas_obj, doc):
        """Genera el encabezado y pie de página con logo"""
        canvas_obj.saveState()

        # === LOGO EN HEADER ===
        logo_path = os.path.join(settings.BASE_DIR, "tickets/static/tickets/images/logo_calvas.png")
        logo_width = 70
        logo_height = 70
        canvas_obj.drawImage(
            logo_path,
            50, self.height - 90,  # posición (x, y)
            width=logo_width,
            height=logo_height,
            mask='auto'
        )

        # === TEXTO DEL HEADER (a la derecha del logo) ===
        canvas_obj.setFont('Helvetica-Bold', 16)
        canvas_obj.drawCentredString(self.width / 2, self.height - 50, "Requerimiento de Soporte - GAD Calvas")

        canvas_obj.setFont('Helvetica-Bold', 12)
        canvas_obj.drawString(140, self.height - 75, "ÁREA ENCARGADA")
        canvas_obj.setFont('Helvetica', 11)
        canvas_obj.drawString(140, self.height - 90, "Tecnologías de la Información y Comunicación (TICS)")

        # Número de Ticket
        canvas_obj.setFont('Helvetica-Bold', 12)
        canvas_obj.drawString(self.width - 200, self.height - 75, "TICKET NRO:")
        canvas_obj.setFont('Helvetica-Bold', 14)
        canvas_obj.setFillColor(colors.HexColor('#2563eb'))
        canvas_obj.drawString(self.width - 200, self.height - 90, self.ticket.ticket_number)
        canvas_obj.setFillColor(colors.black)

        # Línea divisoria
        canvas_obj.setStrokeColor(colors.HexColor('#2563eb'))
        canvas_obj.setLineWidth(2)
        canvas_obj.line(50, self.height - 100, self.width - 50, self.height - 100)

        # === FOOTER ===
        canvas_obj.setFont('Helvetica', 9)

        fecha_ticket = self.ticket.created_at.strftime('%d de %B del %Y')
        canvas_obj.drawString(50, 50, f"Fecha del Ticket: {fecha_ticket}")

        fecha_reporte = datetime.now().strftime('%d de %B del %Y %H:%M')
        canvas_obj.drawString(50, 35, f"Fecha del Reporte: {fecha_reporte}")

        page_num = canvas_obj.getPageNumber()
        text = f"Página {page_num}"
        canvas_obj.drawRightString(self.width - 50, 50, text)

        canvas_obj.restoreState()
    
    def generate_pdf(self):
        """Genera el PDF completo"""
        doc = SimpleDocTemplate(
            self.buffer,
            pagesize=self.pagesize,
            rightMargin=50,
            leftMargin=50,
            topMargin=120,
            bottomMargin=80,
        )
        
        # Estilos
        styles = getSampleStyleSheet()
        
        # Estilo personalizado para títulos
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2563eb'),
            spaceAfter=12,
            spaceBefore=12,
        )
        
        # Estilo para subtítulos
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading3'],
            fontSize=11,
            textColor=colors.HexColor('#64748b'),
            spaceAfter=8,
        )
        
        # Estilo para contenido
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
        )
        
        # Contenedor de elementos
        elements = []
        
        # === INFORMACIÓN DEL TICKET ===
        elements.append(Paragraph("INFORMACIÓN DEL TICKET", title_style))
        
        # Tabla de información básica
        info_data = [
            ['Usuario:', self.ticket.user.get_full_name() or self.ticket.user.username],
            ['Fecha de Creación:', self.ticket.created_at.strftime('%d/%m/%Y %H:%M')],
            ['Estado:', self.ticket.get_status_display()],
            ['Prioridad:', self.ticket.get_priority_display()],
            ['Categoría:', self.ticket.get_category_display()],
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1f5f9')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(info_table)
        elements.append(Spacer(1, 10))
        
        # === INFORMACIÓN DEL SOLICITANTE ===
        elements.append(Paragraph("INFORMACIÓN DEL SOLICITANTE", title_style))
        
        solicitante_data = [
            ['Nombre Completo:', self.ticket.user.get_full_name() or self.ticket.user.username],
            ['Usuario:', self.ticket.user.username],
        ]
        
        if hasattr(self.ticket.user, 'profile'):
            if self.ticket.user.profile.cargo:
                solicitante_data.append(['Cargo:', self.ticket.user.profile.cargo])
            if self.ticket.user.profile.departamento:
                solicitante_data.append(['Departamento:', self.ticket.user.profile.departamento])
            if self.ticket.user.email:
                solicitante_data.append(['Email:', self.ticket.user.email])
            if self.ticket.user.profile.telefono:
                telefono = self.ticket.user.profile.telefono
                if self.ticket.user.profile.extension:
                    telefono += f" Ext. {self.ticket.user.profile.extension}"
                solicitante_data.append(['Teléfono:', telefono])
        
        solicitante_table = Table(solicitante_data, colWidths=[2*inch, 4*inch])
        solicitante_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f9ff')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(solicitante_table)
        elements.append(Spacer(1, 10))
        
        # === DESCRIPCIÓN DEL PROBLEMA ===
        elements.append(Paragraph("DESCRIPCIÓN DEL PROBLEMA", title_style))
        elements.append(Paragraph(f"<b>Título:</b> {self.ticket.title}", normal_style))
        elements.append(Spacer(1, 10))
        
        # Descripción en un cuadro
        desc_data = [[Paragraph(self.ticket.description, normal_style)]]
        desc_table = Table(desc_data, colWidths=[6*inch])
        desc_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fef3c7')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#f59e0b')),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ]))
        
        elements.append(desc_table)
        elements.append(Spacer(1, 20))
        elements.append(Spacer(1, 20))
        elements.append(Spacer(1, 20))
        # === ASIGNACIÓN ===
        if self.ticket.assigned_to:
            elements.append(Paragraph("\nASIGNADO A", title_style))
            
            asignado_data = [
                ['Técnico:', self.ticket.assigned_to.get_full_name() or self.ticket.assigned_to.username],
            ]
            
            if hasattr(self.ticket.assigned_to, 'profile'):
                if self.ticket.assigned_to.profile.cargo:
                    asignado_data.append(['Cargo:', self.ticket.assigned_to.profile.cargo])
                if self.ticket.assigned_to.profile.departamento:
                    asignado_data.append(['Departamento:', self.ticket.assigned_to.profile.departamento])
                if self.ticket.assigned_to.email:
                    asignado_data.append(['Correo Electrónico: ', self.ticket.assigned_to.email])
                if self.ticket.assigned_to.profile.celular:
                    asignado_data.append(['Celular: ', self.ticket.assigned_to.profile.celular])
                    
            asignado_table = Table(asignado_data, colWidths=[2*inch, 4*inch])
            asignado_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#d1fae5')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            
            elements.append(asignado_table)
            elements.append(Spacer(1, 20))
        
        # === COMENTARIOS ===
        comments = self.ticket.comments.all()
        if comments.exists():
            elements.append(Paragraph(f"COMENTARIOS ({comments.count()})", title_style))
            
            for comment in comments:
                # Encabezado del comentario
                comment_header = f"<b>{comment.user.get_full_name() or comment.user.username}</b> - {comment.created_at.strftime('%d/%m/%Y %H:%M')}"
                elements.append(Paragraph(comment_header, subtitle_style))
                
                # Contenido del comentario
                comment_data = [[Paragraph(comment.text, normal_style)]]
                comment_table = Table(comment_data, colWidths=[6*inch])
                comment_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
                    ('BOX', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('TOPPADDING', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                    ('LEFTPADDING', (0, 0), (-1, -1), 10),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ]))
                
                elements.append(comment_table)
                elements.append(Spacer(1, 15))
        
        # === FIRMAS ===
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("FIRMAS", title_style))
        elements.append(Spacer(1, 20))

        
        firmas_data = [
            ['', ''],
            ['_' * 30, '_' * 30],
            ['Solicitante', 'Técnico de Soporte'],
            [self.ticket.user.get_full_name() or self.ticket.user.username, 
             self.ticket.assigned_to.get_full_name() if self.ticket.assigned_to else ''],
        ]
        
        firmas_table = Table(firmas_data, colWidths=[3*inch, 3*inch])
        firmas_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, 1), 20),
        ]))
        
        elements.append(firmas_table)
        
        # Construir PDF
        doc.build(elements, onFirstPage=self.generate_header_footer, 
                 onLaterPages=self.generate_header_footer)
        
        # Obtener el PDF
        pdf = self.buffer.getvalue()
        self.buffer.close()
        return pdf