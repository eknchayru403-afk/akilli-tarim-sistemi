"""
PDF Rapor Üretici — ReportLab ile tarımsal rapor oluşturma.

Sulama, gübreleme ve ilaçlama geçmişini içeren PDF raporu üretir.
"""

import io
import logging
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

logger = logging.getLogger(__name__)


def generate_pdf_report(report_data: dict) -> io.BytesIO:
    """
    PDF raporu oluşturur.

    Args:
        report_data: Rapor verileri dict:
            - user_name: Kullanıcı adı
            - field_name: Tarla adı (veya 'Tüm Tarlalar')
            - date_from: Başlangıç tarihi
            - date_to: Bitiş tarihi
            - care_records: Bakım kayıtları listesi
            - soil_analyses: Toprak analizleri listesi
            - recommendations: Ürün önerileri listesi

    Returns:
        PDF içeren BytesIO buffer.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()

    # Özel stiller
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=18,
        spaceAfter=20,
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=10,
        spaceBefore=15,
        textColor=colors.HexColor('#2d6a4f'),
    )
    normal_style = styles['Normal']

    elements = []

    # ── Başlık ──
    elements.append(Paragraph(
        'Akıllı Tarım Yönetim Sistemi — Tarımsal Rapor',
        title_style,
    ))

    # Meta bilgiler
    meta_info = [
        f"<b>Çiftçi:</b> {report_data.get('user_name', '-')}",
        f"<b>Tarla:</b> {report_data.get('field_name', 'Tüm Tarlalar')}",
        f"<b>Tarih Aralığı:</b> {report_data.get('date_from', '-')} — {report_data.get('date_to', '-')}",
        f"<b>Rapor Tarihi:</b> {datetime.now():%d.%m.%Y %H:%M}",
    ]
    for info in meta_info:
        elements.append(Paragraph(info, normal_style))
    elements.append(Spacer(1, 20))

    # ── 1) Bakım Geçmişi (Sulama, Gübreleme, İlaçlama) ──
    care_records = report_data.get('care_records', [])

    # Sulama kayıtları
    irrigation_records = [r for r in care_records if r['type'] == 'irrigation']
    elements.append(Paragraph('1. Sulama Geçmişi', heading_style))
    if irrigation_records:
        elements.append(_build_care_table(irrigation_records))
    else:
        elements.append(Paragraph('Bu dönemde sulama kaydı bulunmamaktadır.', normal_style))
    elements.append(Spacer(1, 10))

    # Gübreleme kayıtları
    fertilization_records = [r for r in care_records if r['type'] == 'fertilization']
    elements.append(Paragraph('2. Gübreleme Geçmişi', heading_style))
    if fertilization_records:
        elements.append(_build_care_table(fertilization_records))
    else:
        elements.append(Paragraph('Bu dönemde gübreleme kaydı bulunmamaktadır.', normal_style))
    elements.append(Spacer(1, 10))

    # İlaçlama kayıtları
    pesticide_records = [r for r in care_records if r['type'] == 'pesticide']
    elements.append(Paragraph('3. İlaçlama Geçmişi', heading_style))
    if pesticide_records:
        elements.append(_build_care_table(pesticide_records))
    else:
        elements.append(Paragraph('Bu dönemde ilaçlama kaydı bulunmamaktadır.', normal_style))
    elements.append(Spacer(1, 10))

    # ── 2) Toprak Analizleri ──
    soil_analyses = report_data.get('soil_analyses', [])
    elements.append(Paragraph('4. Toprak Analizi Özeti', heading_style))
    if soil_analyses:
        elements.append(_build_soil_table(soil_analyses))
    else:
        elements.append(Paragraph('Bu dönemde toprak analizi bulunmamaktadır.', normal_style))
    elements.append(Spacer(1, 10))

    # ── 3) Ürün Önerileri ──
    recommendations = report_data.get('recommendations', [])
    elements.append(Paragraph('5. Ürün Önerileri', heading_style))
    if recommendations:
        elements.append(_build_recommendation_table(recommendations))
    else:
        elements.append(Paragraph('Bu dönemde ürün önerisi bulunmamaktadır.', normal_style))

    # PDF oluştur
    doc.build(elements)
    buffer.seek(0)
    logger.info("PDF rapor oluşturuldu: %d sayfa", doc.page)
    return buffer


def _build_care_table(records: list) -> Table:
    """Bakım kayıtları tablosu oluşturur."""
    data = [['Tarla', 'Mesaj', 'Öncelik', 'Durum', 'Tarih']]
    for r in records:
        data.append([
            r.get('field_name', '-'),
            r.get('message', '-')[:60],
            r.get('priority', '-'),
            'Tamamlandı' if r.get('is_done') else 'Bekliyor',
            r.get('date', '-'),
        ])

    table = Table(data, colWidths=[3 * cm, 7 * cm, 2.5 * cm, 2.5 * cm, 2.5 * cm])
    table.setStyle(_get_table_style())
    return table


def _build_soil_table(analyses: list) -> Table:
    """Toprak analizi tablosu oluşturur."""
    data = [['Tarla', 'N', 'P', 'K', 'pH', 'Nem%', 'Sıcaklık°C', 'Tarih']]
    for a in analyses:
        data.append([
            a.get('field_name', '-'),
            a.get('nitrogen', '-'),
            a.get('phosphorus', '-'),
            a.get('potassium', '-'),
            a.get('ph', '-'),
            a.get('humidity', '-'),
            a.get('temperature', '-'),
            a.get('date', '-'),
        ])

    table = Table(data, colWidths=[3 * cm, 1.5 * cm, 1.5 * cm, 1.5 * cm,
                                    1.5 * cm, 2 * cm, 2.5 * cm, 3 * cm])
    table.setStyle(_get_table_style())
    return table


def _build_recommendation_table(recommendations: list) -> Table:
    """Ürün önerisi tablosu oluşturur."""
    data = [['Ürün', 'Güven %', 'Tah. Verim (kg)', 'Tah. Kazanç (TL)', 'Tarih']]
    for r in recommendations:
        data.append([
            r.get('crop_name_tr', '-'),
            r.get('confidence', '-'),
            r.get('yield_kg', '-'),
            r.get('revenue_tl', '-'),
            r.get('date', '-'),
        ])

    table = Table(data, colWidths=[3.5 * cm, 2.5 * cm, 3.5 * cm, 3.5 * cm, 3.5 * cm])
    table.setStyle(_get_table_style())
    return table


def _get_table_style() -> TableStyle:
    """Ortak tablo stili döndürür."""
    return TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d6a4f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f7f4')]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ])
