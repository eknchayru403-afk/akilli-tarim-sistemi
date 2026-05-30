"""
CSV Rapor Üretici.
"""
import io
import csv


def generate_csv_report(report_data: dict) -> io.BytesIO:
    """
    Rapor verisini CSV formatına dönüştürür.
    Excel uyumluluğu için UTF-8 BOM ile ';' ayırıcı kullanır.
    """
    buffer = io.BytesIO()
    # Write BOM for Excel UTF-8 support
    buffer.write(b'\xef\xbb\xbf')

    stream = io.StringIO()
    writer = csv.writer(stream, delimiter=';', lineterminator='\n')

    # Başlık ve Meta Bilgiler
    writer.writerow(['AKILLI TARIM YÖNETİM SİSTEMİ - TARIMSAL RAPOR'])
    writer.writerow([])
    writer.writerow(['Çiftçi', report_data.get('user_name', '-')])
    writer.writerow(['Tarla', report_data.get('field_name', 'Tüm Tarlalar')])
    writer.writerow(['Tarih Aralığı', f"{report_data.get('date_from', '-')} - {report_data.get('date_to', '-')}"])
    writer.writerow(['Rapor Tipi', report_data.get('report_type', 'general').upper()])
    writer.writerow([])

    # 1. Bakım Kayıtları (Tavsiyeler/Uyarılar)
    care_records = report_data.get('care_records', [])
    if care_records:
        writer.writerow(['--- BAKIM TAVSİYELERİ VE UYARILAR ---'])
        writer.writerow(['Tarla', 'Tip', 'Mesaj', 'Öncelik', 'Durum', 'Tarih'])
        for r in care_records:
            writer.writerow([
                r.get('field_name', '-'),
                r.get('type_display', r.get('type', '-')),
                r.get('message', '-'),
                r.get('priority', '-'),
                'Tamamlandı' if r.get('is_done') else 'Bekliyor',
                r.get('date', '-'),
            ])
        writer.writerow([])

    # 2. Sulama / Gübreleme Uygulamaları
    irrigation_logs = report_data.get('irrigation_logs', [])
    if irrigation_logs:
        writer.writerow(['--- SULAMA VE GÜBRELEME UYGULAMALARI ---'])
        writer.writerow(['Tarla', 'İşlem Tipi', 'Miktar (L/kg)', 'Detaylar', 'Tarih'])
        for l in irrigation_logs:
            writer.writerow([
                l.get('field_name', '-'),
                l.get('type_display', '-'),
                l.get('amount', 0.0),
                l.get('details', '-'),
                l.get('date', '-'),
            ])
        writer.writerow([])

    # 3. Toprak Analizleri
    soil_analyses = report_data.get('soil_analyses', [])
    if soil_analyses:
        writer.writerow(['--- TOPRAK ANALİZLERİ ---'])
        writer.writerow(['Tarla', 'Azot (N)', 'Fosfor (P)', 'Potasyum (K)', 'pH', 'Nem (%)', 'Sıcaklık (°C)', 'Yağış (mm)', 'Tarih'])
        for s in soil_analyses:
            writer.writerow([
                s.get('field_name', '-'),
                s.get('nitrogen', 0.0),
                s.get('phosphorus', 0.0),
                s.get('potassium', 0.0),
                s.get('ph', 0.0),
                s.get('humidity', 0.0),
                s.get('temperature', 0.0),
                s.get('rainfall', 0.0),
                s.get('date', '-'),
            ])
        writer.writerow([])

    # 4. Sensör Verileri
    sensor_data = report_data.get('sensor_data', [])
    if sensor_data:
        writer.writerow(['--- SENSÖR VERİLERİ ---'])
        writer.writerow(['Tarla', 'Sıcaklık (°C)', 'Nem (%)', 'Toprak Nemi (%)', 'Su Tüketimi (mm/gün)', 'pH', 'Işık Yoğunluğu (Lux)', 'Tarih'])
        for sd in sensor_data:
            writer.writerow([
                sd.get('field_name', '-'),
                sd.get('temperature', 0.0),
                sd.get('humidity', 0.0),
                sd.get('soil_moisture', 0.0),
                sd.get('plant_water_consumption', 0.0),
                sd.get('soil_ph', 0.0),
                sd.get('light_intensity', 0.0),
                sd.get('date', '-'),
            ])
        writer.writerow([])

    # 5. Ürün Önerileri
    recommendations = report_data.get('recommendations', [])
    if recommendations:
        writer.writerow(['--- ÜRÜN ÖNERİLERİ (VERİM ANALİZİ) ---'])
        writer.writerow(['Tarla', 'Ürün', 'Güven Skoru (%)', 'Tahmini Verim (kg)', 'Tahmini Kazanç (TL)', 'Sıralama', 'Tarih'])
        for r in recommendations:
            writer.writerow([
                r.get('field_name', '-'),
                r.get('crop_name_tr', '-'),
                r.get('confidence', 0.0),
                r.get('yield_kg', 0.0),
                r.get('revenue_tl', 0.0),
                r.get('rank', 1),
                r.get('date', '-'),
            ])
        writer.writerow([])

    buffer.write(stream.getvalue().encode('utf-8'))
    buffer.seek(0)
    return buffer
