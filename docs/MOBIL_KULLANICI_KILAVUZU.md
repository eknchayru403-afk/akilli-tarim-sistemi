# ATYS — Mobil Kullanıcı Kılavuzu

**Akıllı Tarım Yönetim Sistemi**  
Bu kılavuz, telefon veya tabletten **mobil tarayıcı** ile ATYS web uygulamasını kullanmanız içindir.

> **Not:** App Store veya Google Play’de ayrı bir “ATYS” uygulaması bulunmamaktadır. Tüm özellikler tarayıcınız üzerinden çalışır. Masaüstünde Chrome, Safari veya Edge; mobilde Safari (iOS) veya Chrome (Android) önerilir.

---

## İçindekiler

1. [Sistem gereksinimleri](#1-sistem-gereksinimleri)
2. [İlk kurulum ve giriş](#2-ilk-kurulum-ve-giriş)
3. [Ana ekran ve menü](#3-ana-ekran-ve-menü)
4. [Tarla yönetimi](#4-tarla-yönetimi)
5. [Toprak analizi ve simülasyon](#5-toprak-analizi-ve-simülasyon)
6. [Sonuçları ve önerileri görüntüleme](#6-sonuçları-ve-önerileri-görüntüleme)
7. [Fiyatlar ve hava durumu](#7-fiyatlar-ve-hava-durumu)
8. [Profil ve çıkış](#8-profil-ve-çıkış)
9. [Ana ekrana kısayol ekleme](#9-ana-ekrana-kısayol-ekleme)
10. [Sık karşılaşılan sorunlar](#10-sık-karşılaşılan-sorunlar)

---

## 1. Sistem gereksinimleri

| Gereksinim | Minimum |
|------------|---------|
| İnternet | Aktif bağlantı (çevrimdışı mod desteklenmez) |
| iOS | 15 ve üzeri, Safari |
| Android | 10 ve üzeri, Chrome |
| Ekran | 320 px genişlik ve üzeri (telefon uyumlu) |
| Sunucu adresi | Kurulumunuza göre örn. `http://localhost:8000` veya üretim URL’si |

---

## 2. İlk kurulum ve giriş

### Adım 1 — Adrese gidin

1. Mobil tarayıcınızı açın.
2. Adres çubuğuna sistem yöneticinizin verdiği URL’yi yazın (ör. `https://tarim.sizin-domain.com`).
3. Giriş sayfası açılmazsa sonuna `/accounts/login/` ekleyin.

### Adım 2 — Hesap oluşturun (ilk kez kullanıyorsanız)

1. **Kayıt Ol** bağlantısına dokunun.
2. Kullanıcı adı, e-posta ve parolanızı girin.
3. **Kayıt Ol** düğmesine basın.
4. Başarılı kayıttan sonra giriş sayfasına yönlendirilirsiniz.

### Adım 3 — Giriş yapın

1. Kullanıcı adı ve parolanızı girin.
2. **Giriş Yap**’a dokunun.
3. Dashboard (özet ekran) görünür.

**İpucu:** Tarayıcı “Parolayı kaydet” önerirse kabul edebilirsiniz; paylaşımlı cihazlarda kaydetmeyin.

---

## 3. Ana ekran ve menü

### Mobil menüyü açma

Dar ekranda sol menü varsayılan olarak gizlidir.

1. Sol üstteki **☰ (üç çizgi)** simgesine dokunun.
2. Menü soldan kayarak açılır: Dashboard, Tarlalarım, Analizler, Fiyatlar, Hava Durumu.
3. Menü dışındaki gri alana dokunarak menüyü kapatabilirsiniz.

### Dashboard’da neler var?

- Toplam tarla sayısı
- Boş / ekili tarla özeti
- Son analizlere hızlı erişim (varsa)

Veriler sunucudan çekilir; tarla ekledikten veya sildikten sonra özet birkaç saniye içinde güncellenir.

---

## 4. Tarla yönetimi

### Yeni tarla ekleme

1. Üst çubuktaki **+ Tarla Ekle** düğmesine dokunun (veya menüden **Tarlalarım** → ekleme).
2. Formu doldurun:
   - **Tarla adı** (zorunlu)
   - **Konum** (isteğe bağlı)
   - **Alan (dekar)**
   - **Toprak tipi**
   - **Durum:** Boş veya Ekili
3. **Kaydet**’e basın.
4. Tarla listesine yönlendirilirsiniz; yeni tarlanız listede görünür.

### Tarla detayı ve düzenleme

1. **Tarlalarım** menüsüne girin.
2. İlgili tarla kartına dokunun.
3. **Düzenle** ile bilgileri güncelleyin.
4. **Kaydet** — değişiklikler anında sunucuya yazılır.

### Tarla silme

1. Tarla detay sayfasında **Sil** seçeneğini kullanın.
2. Onaylayın. Bu işlem geri alınamaz; bağlı analizler de silinir.

---

## 5. Toprak analizi ve simülasyon

### Manuel analiz (ölçüm değerlerini siz giriyorsanız)

1. Tarla detayına gidin.
2. **Analiz Yap** / benzeri bağlantıya dokunun.
3. N, P, K, sıcaklık, nem, pH, yağış değerlerini girin.
4. **Gönder** — sistem ML modeli ile ürün önerisi üretir (model eğitilmiş olmalıdır).

### Simülasyon (hazır veri setinden otomatik)

Gerçek sensörünüz yoksa veya hızlı deneme için:

1. Tarla detayında **Simülasyon** / **Simüle Et** düğmesine basın.
2. Sistem rastgele örnek veri seçer ve analiz oluşturur.
3. Başarı mesajından sonra sonuç sayfasına yönlendirilirsiniz.

**Veri senkronizasyonu:** Analiz kaydı sunucuda saklanır; **Analizler** menüsünden geçmişe her cihazdan aynı hesapla erişirsiniz.

---

## 6. Sonuçları ve önerileri görüntüleme

1. Analiz tamamlandıktan sonra **ürün önerisi** kartlarını görürsünüz (Türkçe ürün adı, güven yüzdesi).
2. **Analizler** menüsünden geçmiş tüm analizlere bakın.
3. Ekili bir tarla için önerilen ürünü **ek** olarak işaretleyebilirsiniz (tarla durumu “Ekili” olur).

Kartlar mobilde alt alta sıralanır; yatay kaydırma gerekmez.

---

## 7. Fiyatlar ve hava durumu

### Ürün fiyatları

- Menüden **Fiyatlar**’a girin.
- Ürün başına TL/kg ve ortalama verim bilgisi listelenir.
- Veriler sunucuda önbelleğe alınır; günde birkaç kez güncellenmesi yeterlidir.

### Hava durumu

- **Hava Durumu** sayfası örnek / statik içerik gösterebilir (kuruluma bağlı).
- Canlı API entegrasyonu planlanıyorsa sayfa otomatik güncellenecektir.

---

## 8. Profil ve çıkış

1. Sol menünün altındaki **kullanıcı adınıza** dokunun → **Profil**.
2. Ad, soyad, şehir, telefon bilgilerinizi güncelleyebilirsiniz.
3. Çıkış için menü altındaki **çıkış** simgesine (kutu ok) dokunun.

Oturum kapanınca tekrar giriş yapmanız gerekir.

---

## 9. Ana ekrana kısayol ekleme

Uygulama mağazası paketi olmadığı için tarayıcı kısayolu kullanılır.

### iPhone (Safari)

1. ATYS sitesinde giriş yapın.
2. **Paylaş** simgesi → **Ana Ekrana Ekle**.
3. İsim verin (ör. “ATYS”) → **Ekle**.

### Android (Chrome)

1. Siteyi açın.
2. Menü (⋮) → **Ana ekrana ekle** veya **Yükle**.
3. Onaylayın.

Kısayol tam ekran açmaz; tarayıcı çerçevesi kalabilir (PWA henüz desteklenmiyor).

---

## 10. Sık karşılaşılan sorunlar

### “Sayfa açılmıyor” / beyaz ekran

| Olası neden | Çözüm |
|-------------|--------|
| İnternet yok | Wi‑Fi veya mobil veriyi kontrol edin |
| Yanlış URL | `https://` ve domain yazımını doğrulayın |
| Sunucu kapalı | Yöneticinize danışın; geliştirmede `runserver` çalışıyor olmalı |

### Giriş yapamıyorum

| Olası neden | Çözüm |
|-------------|--------|
| Yanlış parola | Büyük/küçük harf; Caps Lock |
| Hesap yok | Önce **Kayıt Ol** |
| Oturum süresi | Tekrar giriş yapın |

### Menü görünmüyor / ekran sıkışık

1. Sayfayı **yenileyin** (aşağı çekerek yenileme veya tarayıcı yenile).
2. **Yatay mod** deneyin (tablet).
3. Tarayıcı yakınlaştırmasını sıfırlayın (çift dokunma ile %100).

### Tarla ekledim ama dashboard sayısı eski

1. 10–15 saniye bekleyin ve sayfayı yenileyin.
2. Hâlâ eskiyse çıkış yapıp tekrar giriş yapın.
3. Sorun sürerse önbellek sorunu olabilir — farklı sekme veya gizli mod deneyin.

### Simülasyon / analiz “ML modeli eğitilmemiş” uyarısı

| Çözüm |
|--------|
| Sistem yöneticisi sunucuda `python manage.py train_model` çalıştırmalıdır |
| Model dosyası: `backend/ml/saved_models/crop_model.pkl` |

### Mobilde tablo taşıyor

- Tabloları **yatay kaydırarak** görüntüleyin (parmakla sağa sola).
- Mümkünse telefonu yatay çevirin.

### Canlı sensör verisi görünmüyor

MQTT sensör entegrasyonu şu an **yönetici paneli ve arka plan servisi** üzerinden çalışır. Mobil web arayüzünde canlı sensör grafiği henüz yoktur; simülasyon veya manuel analiz kullanın.

### Parola / güvenlik

- Ortak telefonlarda parola kaydetmeyin.
- Halka açık Wi‑Fi’de mümkünse VPN kullanın.
- Üretim ortamında adres `https://` ile başlamalıdır.

---

## Destek ve geri bildirim

Teknik sorunlar için proje yöneticinize veya geliştirici ekibe şu bilgileri iletin:

- Cihaz modeli ve işletim sistemi sürümü
- Tarayıcı adı ve sürümü
- Hata anında yapılan işlem (ekran görüntüsü faydalıdır)
- Yaklaşık saat ve kullanıcı adı (parola göndermeyin)

---

*Son güncelleme: 18 Mayıs 2026 — ATYS mobil web sürümü*
