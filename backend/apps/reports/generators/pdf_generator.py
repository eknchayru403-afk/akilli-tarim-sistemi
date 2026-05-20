"""
PDF Rapor Üretici — ReportLab ve Matplotlib ile tarımsal rapor oluşturma.
"""
import io
import logging
from datetime import datetime

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

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
    Image,
    KeepTogether,
)

logger = logging.getLogger(__name__)


def generate_pdf_report(report_data: dict) -> io.BytesIO:
    """
    PDF raporu oluşturur.

    Args:
        report_data: Rapor verileri dict.

    Returns:
        PDF içeren BytesIO buffer.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = getSampleStyleSheet()

    # Özel stiller
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=18,
        spaceAfter=15,
        textColor=colors.HexColor('#1b4332'),
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        spaceAfter=8,
        spaceBefore=12,
        textColor=colors.HexColor('#2d6a4f'),
    )
    normal_style = styles['Normal']

    elements = []
    charts_buffers = []  # Keep references to buffers so they aren't garbage collected early

    report_type = report_data.get('report_type', 'general')

    # ── Başlık ──
    title_tr = {
        'general': 'Genel Tarımsal Değerlendirme Raporu',
        'irrigation': 'Akıllı Sulama ve Nem Takip Raporu',
        'fertilization': 'Toprak Verimliliği ve Gübreleme Raporu',
        'yield': 'Tahmini Ürün Verimi ve Kazanç Analizi',
        'sensor': 'Tarımsal Sensör Ölçüm Raporu',
    }.get(report_type, 'Tarımsal Rapor')

    elements.append(Paragraph(
        f"Akıllı Tarım Yönetim Sistemi — {title_tr}",
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
    elements.append(Spacer(1, 15))

    # ── Grafikler ve Tablolar (Rapor Tipine Göre) ──

    # SULAMA RAPORU
    if report_type == 'irrigation':
        # Nem Grafik
        sensor_data = report_data.get('sensor_data', [])
        chart_buf = _generate_irrigation_chart(sensor_data)
        if chart_buf:
            charts_buffers.append(chart_buf)
            elements.append(Image(chart_buf, width=15 * cm, height=7 * cm))
            elements.append(Spacer(1, 10))

        # Sulama Bakım Tavsiyeleri
        care_records = report_data.get('care_records', [])
        elements.append(Paragraph('Sulama Tavsiyeleri', heading_style))
        if care_records:
            elements.append(_build_care_table(care_records))
        else:
            elements.append(Paragraph('Kayıtlı sulama tavsiyesi bulunmamaktadır.', normal_style))
        elements.append(Spacer(1, 10))

        # Sulama Uygulamaları
        logs = report_data.get('irrigation_logs', [])
        elements.append(Paragraph('Gerçekleşen Sulama İşlemleri', heading_style))
        if logs:
            elements.append(_build_logs_table(logs))
        else:
            elements.append(Paragraph('Bu dönemde yapılmış sulama kaydı bulunmamaktadır.', normal_style))

    # GÜBRELEME RAPORU
    elif report_type == 'fertilization':
        # NPK Bar Grafik
        soil_analyses = report_data.get('soil_analyses', [])
        chart_buf = _generate_fertilization_chart(soil_analyses)
        if chart_buf:
            charts_buffers.append(chart_buf)
            elements.append(Image(chart_buf, width=15 * cm, height=7 * cm))
            elements.append(Spacer(1, 10))

        # Gübreleme Tavsiyeleri
        care_records = report_data.get('care_records', [])
        elements.append(Paragraph('Gübreleme ve Toprak Düzenleme Tavsiyeleri', heading_style))
        if care_records:
            elements.append(_build_care_table(care_records))
        else:
            elements.append(Paragraph('Kayıtlı gübreleme tavsiyesi bulunmamaktadır.', normal_style))
        elements.append(Spacer(1, 10))

        # Gübreleme Uygulamaları (Log)
        logs = report_data.get('irrigation_logs', [])
        elements.append(Paragraph('Gerçekleşen Gübreleme İşlemleri', heading_style))
        if logs:
            elements.append(_build_logs_table(logs))
        else:
            elements.append(Paragraph('Bu dönemde yapılmış gübreleme kaydı bulunmamaktadır.', normal_style))
        elements.append(Spacer(1, 10))

        # Toprak Analizleri
        elements.append(Paragraph('Toprak Analizi Detayları', heading_style))
        if soil_analyses:
            elements.append(_build_soil_table(soil_analyses))
        else:
            elements.append(Paragraph('Toprak analizi bulunmamaktadır.', normal_style))

    # VERİM ANALİZİ RAPORU
    elif report_type == 'yield':
        # Verim Pasta Grafik
        recs = report_data.get('recommendations', [])
        chart_buf = _generate_yield_chart(recs)
        if chart_buf:
            charts_buffers.append(chart_buf)
            elements.append(Image(chart_buf, width=15 * cm, height=7 * cm))
            elements.append(Spacer(1, 10))

        # Ürün Önerileri ve Tahmini Verimler
        elements.append(Paragraph('Önerilen Ürünler ve Tahmini Verimler', heading_style))
        if recs:
            elements.append(_build_recommendation_table(recs))
        else:
            elements.append(Paragraph('Verim analizi ve ürün önerisi bulunmamaktadır.', normal_style))
        elements.append(Spacer(1, 10))

        # Son Toprak Analizi Referansı
        soil_analyses = report_data.get('soil_analyses', [])
        elements.append(Paragraph('Referans Alınan Toprak Analiz Değerleri', heading_style))
        if soil_analyses:
            elements.append(_build_soil_table(soil_analyses[:3]))
        else:
            elements.append(Paragraph('Referans toprak analizi bulunamadı.', normal_style))

    # SENSÖR ÖZET RAPORU
    elif report_type == 'sensor':
        # Sıcaklık Nem Dual-Axis Grafik
        sensor_data = report_data.get('sensor_data', [])
        chart_buf = _generate_sensor_trend_chart(sensor_data)
        if chart_buf:
            charts_buffers.append(chart_buf)
            elements.append(Image(chart_buf, width=15 * cm, height=7 * cm))
            elements.append(Spacer(1, 10))

        # Sensör Ölçümleri Tablosu
        elements.append(Paragraph('Sensör Ölçüm Kayıtları (Son 10 Ölçüm)', heading_style))
        if sensor_data:
            elements.append(_build_sensor_table(sensor_data))
        else:
            elements.append(Paragraph('Kayıtlı sensör verisi bulunmamaktadır.', normal_style))

    # GENEL RAPOR (Eski yapı ve her şeyin özeti)
    else:
        # Genel Rapor Özet Grafiği (Sıcaklık ve Nem Trendi)
        sensor_data = report_data.get('sensor_data', [])
        chart_buf = _generate_sensor_trend_chart(sensor_data)
        if chart_buf:
            charts_buffers.append(chart_buf)
            elements.append(Image(chart_buf, width=15 * cm, height=7 * cm))
            elements.append(Spacer(1, 10))

        # Bakım Önerileri
        care_records = report_data.get('care_records', [])
        elements.append(Paragraph('Aktif Bakım Önerileri ve Uyarılar', heading_style))
        if care_records:
            elements.append(_build_care_table(care_records))
        else:
            elements.append(Paragraph('Aktif bakım önerisi bulunmamaktadır.', normal_style))
        elements.append(Spacer(1, 10))

        # Toprak Analizleri
        soil_analyses = report_data.get('soil_analyses', [])
        elements.append(Paragraph('Toprak Analizleri', heading_style))
        if soil_analyses:
            elements.append(_build_soil_table(soil_analyses))
        else:
            elements.append(Paragraph('Toprak analizi bulunmamaktadır.', normal_style))
        elements.append(Spacer(1, 10))

        # Ürün Önerileri
        recs = report_data.get('recommendations', [])
        elements.append(Paragraph('Yapay Zeka Ürün Önerileri', heading_style))
        if recs:
            elements.append(_build_recommendation_table(recs))
        else:
            elements.append(Paragraph('Öneri bulunmamaktadır.', normal_style))

    # PDF oluştur
    doc.build(elements)
    buffer.seek(0)
    logger.info("PDF rapor oluşturuldu: %d sayfa", doc.page)

    # Clean up Matplotlib buffers
    for buf in charts_buffers:
        try:
            buf.close()
        except Exception:
            pass

    return buffer


# ── Grafikleri Üreten Matplotlib Yardımcı Fonksiyonları ──

def _generate_sensor_trend_chart(sensor_data: list) -> io.BytesIO | None:
    if not sensor_data:
        return None
    sorted_data = list(reversed(sensor_data[:12]))
    dates = [d['date'].split(' ')[1] for d in sorted_data]  # Sadece saat:dakika
    temps = [d['temperature'] for d in sorted_data]
    hums = [d['humidity'] for d in sorted_data]

    fig, ax1 = plt.subplots(figsize=(6, 3))

    color = '#e76f51'
    ax1.set_xlabel('Saat')
    ax1.set_ylabel('Sıcaklık (°C)', color=color)
    ax1.plot(dates, temps, color=color, marker='o', linewidth=2)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(True, linestyle=':', alpha=0.6)

    ax2 = ax1.twinx()
    color = '#2a9d8f'
    ax2.set_ylabel('Nem (%)', color=color)
    ax2.plot(dates, hums, color=color, marker='x', linestyle='--', linewidth=2)
    ax2.tick_params(axis='y', labelcolor=color)

    plt.title('Sıcaklık ve Nem Trendi', fontsize=10, pad=8, color='#1b4332', weight='bold')
    plt.xticks(rotation=30)
    fig.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf


def _generate_irrigation_chart(sensor_data: list) -> io.BytesIO | None:
    if not sensor_data:
        return None
    sorted_data = list(reversed(sensor_data[:12]))
    dates = [d['date'].split(' ')[1] for d in sorted_data]
    moisture = [d['soil_moisture'] for d in sorted_data]

    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(dates, moisture, color='#1d3557', marker='s', linewidth=2, label='Toprak Nemi')
    ax.axhline(30.0, color='red', linestyle=':', label='Kritik Eşik (%30)')
    ax.set_ylabel('Nem (%)')
    ax.set_xlabel('Saat')
    ax.set_title('Toprak Nemi Değişim Trendi', fontsize=10, pad=8, color='#1b4332', weight='bold')
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend(loc='lower left', fontsize=8)
    plt.xticks(rotation=30)

    fig.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf


def _generate_fertilization_chart(soil_analyses: list) -> io.BytesIO | None:
    if not soil_analyses:
        return None
    latest = soil_analyses[:5]
    n_vals = [s['nitrogen'] for s in latest]
    p_vals = [s['phosphorus'] for s in latest]
    k_vals = [s['potassium'] for s in latest]
    labels = [s['date'].split(' ')[0] for s in latest]

    x = np.arange(len(latest))
    width = 0.25

    fig, ax = plt.subplots(figsize=(6, 3))
    ax.bar(x - width, n_vals, width, label='Azot (N)', color='#2a9d8f')
    ax.bar(x, p_vals, width, label='Fosfor (P)', color='#e9c46a')
    ax.bar(x + width, k_vals, width, label='Potasyum (K)', color='#e76f51')

    ax.set_ylabel('mg/kg')
    ax.set_title('Toprak Besin Maddesi (NPK) Dağılımı', fontsize=10, pad=8, color='#1b4332', weight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=15)
    ax.legend(fontsize=8)
    ax.grid(True, axis='y', linestyle=':', alpha=0.6)

    fig.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf


def _generate_yield_chart(recommendations: list) -> io.BytesIO | None:
    if not recommendations:
        return None
    top_recs = recommendations[:5]
    labels = [r['crop_name_tr'] for r in top_recs]
    confidences = [r['confidence'] for r in top_recs]

    fig, ax = plt.subplots(figsize=(6, 3))
    colors = ['#2d6a4f', '#40916c', '#52b788', '#74c69d', '#95d5b2']
    ax.pie(
        confidences,
        labels=labels,
        autopct='%1.1f%%',
        startangle=90,
        colors=colors[:len(labels)],
        textprops={'fontsize': 8}
    )
    ax.axis('equal')
    ax.set_title('Önerilen Ürünlerin Uygunluk Dağılımı', fontsize=10, pad=8, color='#1b4332', weight='bold')

    fig.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf


# ── Tablo Oluşturma Yardımcı Fonksiyonları ──

def _build_care_table(records: list) -> Table:
    """Bakım kayıtları tablosu oluşturur."""
    data = [['Tarla', 'Tavsiye Tipi', 'Mesaj', 'Öncelik', 'Durum', 'Tarih']]
    for r in records[:8]:
        data.append([
            r.get('field_name', '-'),
            r.get('type_display', r.get('type', '-')),
            r.get('message', '-')[:50],
            r.get('priority', '-'),
            'Tamamlandı' if r.get('is_done') else 'Bekliyor',
            r.get('date', '-'),
        ])

    table = Table(data, colWidths=[2.5 * cm, 2.5 * cm, 7.5 * cm, 2 * cm, 2 * cm, 2.5 * cm])
    table.setStyle(_get_table_style())
    return table


def _build_soil_table(analyses: list) -> Table:
    """Toprak analizi tablosu oluşturur."""
    data = [['Tarla', 'N', 'P', 'K', 'pH', 'Nem%', 'Sıcaklık°C', 'Tarih']]
    for a in analyses[:8]:
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

    table = Table(data, colWidths=[3 * cm, 1.5 * cm, 1.5 * cm, 1.5 * cm, 1.5 * cm, 2 * cm, 2.5 * cm, 5 * cm])
    table.setStyle(_get_table_style())
    return table


def _build_recommendation_table(recommendations: list) -> Table:
    """Ürün önerisi tablosu oluşturur."""
    data = [['Ürün', 'Güven %', 'Tah. Verim (kg)', 'Tah. Kazanç (TL)', 'Sıra', 'Tarih']]
    for r in recommendations[:8]:
        data.append([
            r.get('crop_name_tr', '-'),
            f"%{r.get('confidence', '-')}",
            f"{r.get('yield_kg', '-'):,}",
            f"{r.get('revenue_tl', '-'):,}",
            r.get('rank', '-'),
            r.get('date', '-'),
        ])

    table = Table(data, colWidths=[3.5 * cm, 2.5 * cm, 3.5 * cm, 3.5 * cm, 1.5 * cm, 4.5 * cm])
    table.setStyle(_get_table_style())
    return table


def _build_sensor_table(sensor_data: list) -> Table:
    """Sensör verileri tablosu oluşturur."""
    data = [['Tarla', 'Sıcaklık°C', 'Nem%', 'ToprakNem%', 'SuTük.(mm)', 'pH', 'Işık(Lux)', 'Tarih']]
    for sd in sensor_data[:10]:
        data.append([
            sd.get('field_name', '-'),
            sd.get('temperature', '-'),
            sd.get('humidity', '-'),
            sd.get('soil_moisture', '-'),
            sd.get('plant_water_consumption', '-'),
            sd.get('soil_ph', '-'),
            sd.get('light_intensity', '-'),
            sd.get('date', '-'),
        ])
    table = Table(data, colWidths=[2.5 * cm, 1.8 * cm, 1.5 * cm, 2.0 * cm, 2.2 * cm, 1.2 * cm, 2.0 * cm, 5.3 * cm])
    table.setStyle(_get_table_style())
    return table


def _build_logs_table(logs: list) -> Table:
    """Uygulama kayıtları tablosu oluşturur."""
    data = [['Tarla', 'İşlem Tipi', 'Miktar', 'Notlar', 'Tarih']]
    for l in logs[:10]:
        data.append([
            l.get('field_name', '-'),
            l.get('type_display', '-'),
            f"{l.get('amount', '-')} L/kg",
            l.get('details', '-')[:40],
            l.get('date', '-'),
        ])
    table = Table(data, colWidths=[3 * cm, 2.5 * cm, 2.5 * cm, 6.5 * cm, 4 * cm])
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
