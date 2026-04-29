# Günlükleme (Logging) Sistemi Optimizasyon Raporu

## 1. Giriş
Bu rapor, Akıllı Tarım Yönetim Sistemi (ATYS) projesindeki günlükleme (logging) altyapısında gerçekleştirilen performans odaklı iyileştirmeleri ve yapılandırma değişikliklerini özetlemektedir. Temel amaç, sistemin yüksek trafik altında (çoklu sensör verisi, ML tahminleri vb.) loglama yaparken darboğaza (bottleneck) girmesini önlemektir.

## 2. Yapılan Değişiklikler ve Yenilikler

### 2.1 Asenkron (Kuyruk Tabanlı) Loglama Entegrasyonu
- **Önceki Durum:** Sistem, logları senkron olarak doğrudan konsola yazıyordu. Disk veya ekran I/O işlemleri sırasında ana web sunucusu (Django) bekletiliyordu (blocking I/O).
- **Yeni Durum:** Python 3.12 ile gelen yerleşik asenkron `QueueHandler` ve `QueueListener` yapılandırması entegre edildi. 
- **Sonuç:** Django uygulaması log mesajını sadece bir kuyruğa (Queue) bırakıp işine devam eder. Arka planda çalışan ayrı bir thread (iş parçacığı) bu mesajları kuyruktan alıp diske veya konsola yazar. Bu sayede uygulamanın yanıt süreleri (latency) loglama işleminden bağımsız hale gelerek ciddi oranda düşürülmüştür.

### 2.2 RotatingFileHandler (Dosyaya Yazma ve Rotasyon)
- **Yenilik:** Sadece geçici konsol logları yerine kalıcı izleme (monitoring) için `logs/atys.log` adlı bir dosyaya yazma özelliği (`RotatingFileHandler`) eklendi.
- **Güvenlik ve Boyut Kontrolü:** Dosya boyutu 5 MB'a ulaştığında otomatik olarak yeni bir dosyaya geçilir ve en fazla 5 adet eski dosya (yedek) tutulur. Bu sayede sunucu diskinin gereksiz yere loglarla dolması (No Space Left on Device hatası) engellenir.

### 2.3 Gürültü Azaltma (Noise Reduction) ve Filtreleme
Geliştirme veya canlı ortamda konsolu / log dosyasını gereksiz yere meşgul eden ve asıl hataların bulunmasını zorlaştıran Django çekirdek logları kısıtlandırılmıştır.
- **`django.server`:** HTTP 200 OK mesajları filtrelendi. Sadece `WARNING` ve `ERROR` seviyelerindeki mesajlar kaydedilecek.
- **`django.db.backends`:** Django ORM'nin ürettiği ve performansı maskeleyen binlerce satırlık SQL sorgu günlükleri engellendi. Sadece kritik veritabanı uyarıları işlenecek.
- **`apps` ve `ml` Modülleri:** Projenin asıl bileşenleri olan bu modüller `INFO` seviyesinde loglanmaya devam edilecek, böylece iş mantığı (business logic) temiz bir şekilde takip edilebilecek.

### 2.4 Zenginleştirilmiş Log Formatı
Sorun gidermeyi (troubleshooting) hızlandırmak amacıyla log mesajı içerisine işlem süreciyle ilgili ek bilgiler eklendi.
- **Eski Format:** `{levelname} {asctime} {module} {message}`
- **Yeni Format:** `[{asctime}] {levelname} [{name}:{lineno}] [PID:{process} TID:{thread}] - {message}`
- **Faydası:** Özellikle asenkron worker'lar (Celery vb.) veya çoklu thread kullanan WSGI/ASGI sunucularında (Gunicorn, Uvicorn) hatanın tam olarak hangi thread'de (`TID`) ve hangi dosyanın kaçıncı satırında (`lineno`) meydana geldiği kolayca tespit edilebilecek.

## 3. Sonuç ve Etki
Bu iyileştirmeler sayesinde Akıllı Tarım Yönetim Sistemi (ATYS), çok sayıda eşzamanlı cihaz bağlantısını karşılayabilecek ve büyük veri işlemleri sırasında disk I/O beklemelerinden dolayı yaşanabilecek "Timeout" hatalarını minimize edecek kurumsal bir loglama mimarisine kavuşmuştur.
