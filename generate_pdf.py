"""
Akıllı Tarım Yönetim Sistemi - PDF Dokümantasyon Üretici
Tüm proje dokümantasyonlarını birleştirip profesyonel bir PDF dosyası oluşturur.
xhtml2pdf kullanır - Windows'ta ek bağımlılık gerektirmez.
"""
import os
import markdown
from xhtml2pdf import pisa

# Birleştirilecek dokümantasyon dosyaları (sıralı)
DOC_FILES = [
    ("Proje Özeti", "README.md"),
    ("Proje Kapanış Raporu", "PROJECT_CLOSURE_REPORT.md"),
    ("Sistem Mimarisi ve Gereksinimler", "SYSTEM_ARCHITECTURE_WIKI.md"),
    ("Mobil Mimari Tasarımı", "ARCHITECTURE.md"),
    ("MQTT Haberleşme Mimarisi", "docs/MQTT_ARCHITECTURE.md"),
    ("Tahminleme Algoritması Tasarımı", "docs/PREDICTION_ALGORITHM_DESIGN.md"),
    ("TensorFlow Model Dokümantasyonu", "docs/TENSORFLOW_MODEL_DOCUMENTATION.md"),
    ("Hiperparametre Optimizasyonu", "docs/HYPERPARAMETER_OPTIMIZATION_REPORT.md"),
    ("Algoritma Performans Raporu", "docs/ALGORITHM_PERFORMANCE_REPORT.md"),
    ("Sensör Veri Analitikleri", "docs/SENSOR_READING_ANALYTICS.md"),
    ("Sensör Verileri Bölümleme", "docs/SENSOR_READINGS_PARTITIONING.md"),
    ("REST API Endpoint Referansı", "docs/api_endpoints.md"),
    ("Veri Toplama Kapanış Raporu", "docs/VERI_TOPLAMA_KAPANMA_RAPORU.md"),
    ("UI/UX Kapanış Raporu", "docs/UX_CLOSING_REPORT.md"),
    ("Wireframe İncelemesi", "docs/UI_WIREFRAMES_REVIEW.md"),
    ("Mobil Test Raporu", "docs/MOBIL_TEST_RAPORU.md"),
    ("Mobil Kullanıcı Kılavuzu", "docs/MOBIL_KULLANICI_KILAVUZU.md"),
]

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<style>
  @page {{
    size: A4;
    margin: 2cm 2.5cm;
    @frame footer {{
      -pdf-frame-content: footerContent;
      bottom: 0.5cm;
      margin-left: 2.5cm;
      margin-right: 2.5cm;
      height: 1cm;
    }}
  }}

  body {{
    font-family: Helvetica, Arial, sans-serif;
    font-size: 10pt;
    line-height: 1.5;
    color: #222222;
  }}

  /* ---- Cover Page ---- */
  .cover {{
    text-align: center;
    padding-top: 160px;
    page-break-after: always;
  }}
  .cover h1 {{
    font-size: 26pt;
    color: #2E7D32;
    margin-bottom: 8px;
  }}
  .cover .subtitle {{
    font-size: 13pt;
    color: #555555;
    margin-bottom: 30px;
  }}
  .cover .divider {{
    width: 200px;
    height: 3px;
    background-color: #4CAF50;
    margin: 25px auto;
  }}
  .cover .meta {{
    font-size: 10pt;
    color: #777777;
  }}
  .cover .meta p {{
    margin: 4px 0;
  }}

  /* ---- TOC ---- */
  .toc {{
    page-break-after: always;
  }}
  .toc h2 {{
    color: #2E7D32;
    font-size: 16pt;
    border-bottom: 2px solid #2E7D32;
    padding-bottom: 6px;
  }}
  .toc-item {{
    padding: 5px 0;
    border-bottom: 1px dotted #cccccc;
    font-size: 10pt;
  }}
  .toc-num {{
    font-weight: bold;
    color: #2E7D32;
    display: inline;
    width: 30px;
  }}

  /* ---- Section ---- */
  .section {{
    page-break-before: always;
  }}
  .section-header {{
    background-color: #2E7D32;
    color: #ffffff;
    padding: 12px 18px;
    margin-bottom: 16px;
    font-size: 14pt;
    font-weight: bold;
  }}

  h1 {{
    color: #2E7D32;
    font-size: 16pt;
    border-bottom: 2px solid #2E7D32;
    padding-bottom: 5px;
    margin-top: 20px;
  }}
  h2 {{
    color: #388E3C;
    font-size: 13pt;
    border-bottom: 1px solid #dddddd;
    padding-bottom: 4px;
    margin-top: 18px;
  }}
  h3 {{
    color: #4CAF50;
    font-size: 11pt;
    margin-top: 14px;
  }}
  h4 {{
    color: #666666;
    font-size: 10pt;
  }}

  table {{
    border-collapse: collapse;
    width: 100%;
    margin: 10px 0;
    font-size: 9pt;
  }}
  th, td {{
    border: 1px solid #cccccc;
    padding: 6px 8px;
    text-align: left;
  }}
  th {{
    background-color: #E8F5E9;
    color: #2E7D32;
    font-weight: bold;
  }}

  pre {{
    background-color: #F5F5F5;
    border: 1px solid #E0E0E0;
    border-left: 3px solid #4CAF50;
    padding: 10px;
    font-size: 8pt;
    line-height: 1.3;
    white-space: pre-wrap;
    word-wrap: break-word;
    font-family: Courier, monospace;
  }}
  code {{
    background-color: #F0F0F0;
    padding: 1px 3px;
    font-size: 8.5pt;
    font-family: Courier, monospace;
  }}

  blockquote {{
    border-left: 3px solid #4CAF50;
    margin: 10px 0;
    padding: 6px 14px;
    background-color: #F9FBE7;
    color: #555555;
  }}

  ul, ol {{
    margin: 6px 0;
    padding-left: 22px;
  }}
  li {{
    margin-bottom: 3px;
  }}

  hr {{
    border: none;
    border-top: 1px solid #dddddd;
    margin: 20px 0;
  }}
</style>
</head>
<body>

<!-- FOOTER -->
<div id="footerContent" style="text-align: center; font-size: 8pt; color: #999999;">
  ATYS - Akıllı Tarım Yönetim Sistemi | Sayfa <pdf:pagenumber>
</div>

<!-- COVER PAGE -->
<div class="cover">
  <h1>Akıllı Tarım Yönetim Sistemi</h1>
  <div class="subtitle">Genel Proje Dokümantasyonu</div>
  <div class="divider">&nbsp;</div>
  <div class="meta">
    <p><b>Proje:</b> ATYS</p>
    <p><b>Tarih:</b> 20 Mayıs 2026</p>
    <p><b>Versiyon:</b> 1.0 (Final)</p>
    <p><b>Teknolojiler:</b> Python - Django - TensorFlow - Flutter - PostgreSQL - MQTT</p>
  </div>
</div>

<!-- TABLE OF CONTENTS -->
<div class="toc">
  <h2>İçindekiler</h2>
  {toc}
</div>

<!-- CONTENT SECTIONS -->
{sections}

</body>
</html>
"""


def main():
    print("=" * 60)
    print("  ATYS Proje Dokümantasyonu PDF Üretici")
    print("=" * 60)

    toc_items = []
    section_html_parts = []

    for idx, (title, filepath) in enumerate(DOC_FILES, 1):
        if not os.path.exists(filepath):
            print(f"  ATLANILDI: {filepath} bulunamadi.")
            continue

        print(f"  [{idx:02d}] {title} ({filepath})")

        with open(filepath, "r", encoding="utf-8") as f:
            md_content = f.read()

        # Mermaid bloklarini kaldiriyoruz (xhtml2pdf desteklemiyor)
        import re
        md_content = re.sub(
            r'```mermaid\s*\n.*?```',
            '\n*(Mermaid diyagrami - HTML versiyonunda goruntulenebilir)*\n',
            md_content,
            flags=re.DOTALL
        )

        html_content = markdown.markdown(
            md_content,
            extensions=["tables", "fenced_code", "sane_lists"],
        )

        toc_items.append(
            f'<div class="toc-item"><span class="toc-num">{idx}.</span> {title}</div>'
        )
        section_html_parts.append(
            f'<div class="section">'
            f'<div class="section-header">Bolum {idx} - {title}</div>'
            f'{html_content}'
            f'</div>'
        )

    toc_str = "\n".join(toc_items)
    sections_str = "\n".join(section_html_parts)

    final_html = HTML_TEMPLATE.format(toc=toc_str, sections=sections_str)

    # Write HTML too
    html_path = "Akilli_Tarim_Proje_Dokumantasyonu.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(final_html)
    print(f"\n  HTML olusturuldu: {html_path}")

    # Generate PDF
    pdf_path = "Akilli_Tarim_Proje_Dokumantasyonu.pdf"
    print(f"  PDF olusturuluyor: {pdf_path} ...")

    with open(pdf_path, "w+b") as pdf_file:
        pisa_status = pisa.CreatePDF(final_html, dest=pdf_file, encoding="utf-8")

    if pisa_status.err:
        print(f"  HATA: PDF olusturulurken {pisa_status.err} hata olustu.")
    else:
        size_kb = os.path.getsize(pdf_path) / 1024
        print(f"  PDF BASARILI: {pdf_path} ({size_kb:.0f} KB)")

    print("=" * 60)


if __name__ == "__main__":
    main()
