import os
import zipfile
import markdown

# 1. Dokümantasyon Dosyaları
DOC_FILES = [
    "README.md",
    "PROJECT_CLOSURE_REPORT.md",
    "SYSTEM_ARCHITECTURE_WIKI.md",
    "ARCHITECTURE.md",
    "docs/PREDICTION_ALGORITHM_DESIGN.md",
    "docs/ALGORITHM_PERFORMANCE_REPORT.md",
    "docs/api_endpoints.md",
    "docs/MOBIL_KULLANICI_KILAVUZU.md"
]

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Akıllı Tarım Yönetim Sistemi - Genel Dokümantasyon</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 1200px; margin: 0 auto; padding: 20px; }
        h1 { color: #2E7D32; border-bottom: 2px solid #2E7D32; padding-bottom: 10px; }
        h2 { color: #388E3C; border-bottom: 1px solid #ccc; padding-bottom: 5px; margin-top: 30px; }
        h3 { color: #4CAF50; }
        pre { background-color: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }
        code { background-color: #f4f4f4; padding: 2px 5px; border-radius: 3px; font-family: 'Courier New', Courier, monospace; }
        table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #f2f2f2; color: #333; }
        blockquote { border-left: 4px solid #4CAF50; padding-left: 15px; margin-left: 0; color: #555; background-color: #f9f9f9; padding: 10px 15px; }
        .page-break { page-break-before: always; }
        .file-separator { text-align: center; margin: 50px 0; color: #ccc; }
    </style>
</head>
<body>
    <h1>Akıllı Tarım Yönetim Sistemi (ATYS) - Genel Proje Dokümantasyonu</h1>
    <p><em>Tarih: 20 Mayıs 2026</em></p>
    <hr>
    <div class="content">
        {content}
    </div>
</body>
</html>
"""

def generate_html():
    print("Markdown dosyaları okunuyor ve birleştiriliyor...")
    combined_md = ""
    for file_path in DOC_FILES:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                combined_md += f"\n\n<!-- FILE: {file_path} -->\n"
                combined_md += f"<div class='page-break'></div>\n\n"
                combined_md += content
        else:
            print(f"UYARI: {file_path} bulunamadı.")
            
    print("Markdown HTML'e dönüştürülüyor...")
    # Convert markdown to HTML (enabling tables and codehilite extensions)
    html_content = markdown.markdown(combined_md, extensions=['tables', 'fenced_code', 'nl2br'])
    
    final_html = HTML_TEMPLATE.replace("{content}", html_content)
    
    output_file = "Akilli_Tarim_Proje_Dokumantasyonu.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_html)
    print(f"BAŞARILI: {output_file} oluşturuldu.")

def create_archive():
    print("Proje arşivi (ZIP) oluşturuluyor...")
    archive_name = "Akilli_Tarim_Sistemi_Arsiv.zip"
    
    exclude_dirs = {'.git', '__pycache__', 'venv', 'env', '.venv', '.gemini', 'node_modules', '.idea', '.vscode'}
    exclude_extensions = {'.pyc', '.pyo', '.pyd', '.zip'}
    
    with zipfile.ZipFile(archive_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk("."):
            # Exclude directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                # Exclude specific extensions and the archive itself
                if any(file.endswith(ext) for ext in exclude_extensions):
                    continue
                if file == archive_name:
                    continue
                    
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, ".")
                zipf.write(file_path, arcname)
                
    print(f"BAŞARILI: {archive_name} oluşturuldu.")

if __name__ == "__main__":
    generate_html()
    create_archive()
    print("Tüm işlemler tamamlandı.")
