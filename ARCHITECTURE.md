# ARCHITECTURE.md — Akıllı Tarım Yönetim Sistemi (Mobil)

> **Bu dosya, tüm AI agent'lar (Windsurf, Cursor, Claude) için zorunlu referanstır.**
> Her değişiklik sonrası bu dosyanın sonundaki CHANGELOG bölümü güncellenmelidir.

---

## 1. Proje Özeti

Simülasyon tabanlı akıllı tarım platformu. Fiziksel sensör/IoT donanımı YOK.
Veri kaynakları: Kaggle veri seti (toprak NPK/pH), OpenWeatherMap API (hava durumu), TMO statik fiyat tablosu.

**İki ana senaryo:**
- **Senaryo A — Boş Tarla:** Toprak analizi (manuel veya Kaggle sim) → Scikit-learn ürün önerisi → Verim + kazanç hesaplama
- **Senaryo B — Ekili Tarla:** Hava durumu + toprak verisi → AI bakım tavsiyeleri (sulama, gübreleme vb.)

---

## 2. Tech Stack

| Katman | Teknoloji | Versiyon |
|--------|-----------|----------|
| Mobil | Flutter | 3.x (stable) |
| State Management | Riverpod + flutter_riverpod | ^2.x |
| HTTP Client | Dio | ^5.x |
| Routing | GoRouter | ^14.x |
| Backend | Python + FastAPI | 3.11+ |
| Veritabanı | PostgreSQL | 15+ |
| ML | Scikit-learn | Backend tarafında |
| Hava Durumu | OpenWeatherMap API | Free tier |

---

## 3. Klasör Yapısı

```
lib/
├── main.dart                      # Uygulama giriş noktası
├── app.dart                       # MaterialApp + GoRouter + Theme
│
├── core/                          # Paylaşılan altyapı
│   ├── constants/
│   │   ├── app_colors.dart        # Renk paleti (wireframe'den)
│   │   ├── app_text_styles.dart   # Tipografi
│   │   └── api_endpoints.dart     # Backend + OpenWeatherMap URL'leri
│   ├── theme/
│   │   └── app_theme.dart         # ThemeData (light + dark)
│   ├── network/
│   │   └── dio_client.dart        # Dio instance + interceptor'lar
│   └── utils/
│       └── formatters.dart        # Para, tarih, birim formatlama
│
├── features/                      # Ekran bazlı modüller
│   ├── auth/                      # Ekran 1: Giriş + Kayıt
│   │   ├── data/
│   │   │   ├── auth_repository.dart
│   │   │   └── models/user_model.dart
│   │   ├── providers/
│   │   │   └── auth_provider.dart
│   │   └── screens/
│   │       ├── login_screen.dart
│   │       └── register_screen.dart
│   │
│   ├── dashboard/                 # Ekran 2: Ana Sayfa
│   │   ├── data/
│   │   │   └── models/tarla_ozet_model.dart
│   │   ├── providers/
│   │   │   └── dashboard_provider.dart
│   │   ├── screens/
│   │   │   └── dashboard_screen.dart
│   │   └── widgets/
│   │       ├── tarla_card.dart
│   │       ├── hava_durumu_banner.dart
│   │       └── aksiyon_uyari_card.dart
│   │
│   ├── tarla_detay/               # Ekran 3: Tarla Detay + AI Aksiyon
│   │   ├── data/
│   │   │   ├── models/hava_durumu_model.dart
│   │   │   └── models/bakim_tavsiye_model.dart
│   │   ├── providers/
│   │   │   └── tarla_detay_provider.dart
│   │   ├── screens/
│   │   │   └── tarla_detay_screen.dart
│   │   └── widgets/
│   │       ├── saglik_skoru_widget.dart
│   │       ├── hava_tahmin_card.dart
│   │       └── ai_aksiyon_card.dart
│   │
│   ├── analiz/                    # Ekran 4-5: Toprak Analizi + Sonuç
│   │   ├── data/
│   │   │   ├── analiz_repository.dart
│   │   │   ├── models/toprak_analiz_model.dart
│   │   │   └── models/urun_oneri_model.dart
│   │   ├── providers/
│   │   │   └── analiz_provider.dart
│   │   ├── screens/
│   │   │   └── analiz_screen.dart
│   │   └── widgets/
│   │       ├── npk_input_card.dart
│   │       └── oneri_bottom_sheet.dart
│   │
│   ├── gecmis/                    # Ekran 6: Geçmiş Analizler
│   │   ├── data/
│   │   │   └── models/gecmis_kayit_model.dart
│   │   ├── providers/
│   │   │   └── gecmis_provider.dart
│   │   └── screens/
│   │       └── gecmis_screen.dart
│   │
│   └── profil/                    # Ekran 7: Profil + Ayarlar
│       ├── data/
│       │   └── models/urun_fiyat_model.dart
│       ├── providers/
│       │   └── profil_provider.dart
│       ├── screens/
│       │   ├── profil_screen.dart
│       │   └── fiyat_tablosu_screen.dart
│       └── widgets/
│           └── ayar_tile.dart
│
├── shared/                        # Feature'lar arası paylaşılan widget'lar
│   └── widgets/
│       ├── app_scaffold.dart      # BottomNavigationBar shell
│       ├── loading_indicator.dart
│       └── error_widget.dart
│
assets/
├── data/
│   └── tmo_fiyatlari.json         # TMO fiyat sözlüğü (statik seed)
└── images/
    └── logo.png
```

---

## 4. Routing (GoRouter)

```
/login                          → LoginScreen
/register                       → RegisterScreen
/                               → ShellRoute (BottomNav)
  ├── /dashboard                → DashboardScreen (Ana Sayfa)
  ├── /gecmis                   → GecmisScreen (Geçmiş)
  └── /profil                   → ProfilScreen (Profil)
/tarla/:id                      → TarlaDetayScreen (Ekili tarla detay)
/tarla/:id/analiz               → AnalizScreen (Boş tarla analiz)
/profil/fiyat-tablosu           → FiyatTablosuScreen (TMO fiyatları)
```

BottomNavigationBar 3 sekme: Ana Sayfa, Geçmiş, Profil (wireframe ile birebir).

---

## 5. State Management Kuralları (Riverpod)

- Her feature kendi `providers/` klasöründe provider tanımlar.
- API çağrıları `FutureProvider` veya `AsyncNotifierProvider` ile yapılır.
- UI'da `ref.watch()` ile dinlenir, `AsyncValue.when()` ile loading/error/data render edilir.
- Repository pattern: Provider → Repository → Dio → Backend API.
- Global state (auth token, kullanıcı bilgisi) `core/` altında tutulur.

---

## 6. API Bağlantı Kuralları

- Base URL ortam değişkeninden alınır (`--dart-define=API_BASE_URL=...`).
- Auth token Dio interceptor ile her isteğe eklenir.
- OpenWeatherMap API key `.env` dosyasından okunur (flutter_dotenv).
- Hata yönetimi: Dio exception → custom AppException → UI'da kullanıcı dostu mesaj.

---

## 7. Tema ve Renk Sistemi (Wireframe'den)

```dart
// Wireframe'deki renk paleti
primary:      #2E7D32  (koyu yeşil — header, butonlar)
primaryLight: #4CAF50  (açık yeşil — sağlık barı)
surface:      #FFFFFF  (kart arka planı)
background:   #F5F5F5  (sayfa arka planı)
onPrimary:    #FFFFFF  (beyaz metin yeşil üzerinde)
warning:      #FF9800  (turuncu — uyarı kartları)
error:        #D32F2F  (kırmızı — kritik uyarılar)
accent:       #9C27B0  (mor — Kaggle simülasyon butonu)
textPrimary:  #212121
textSecondary:#757575
```

---

## 8. Agent Kuralları (Windsurf / Cursor / Claude)

1. **Değişiklik yapmadan önce mevcut kodu oku ve raporla.** Asla körlemesine düzenleme yapma.
2. **Çalışan koda dokunma.** Sadece ilgili dosyayı değiştir.
3. **Her değişiklikten sonra** bu dosyanın CHANGELOG bölümüne tarih + sorun + çözüm ekle.
4. **Yeni dosya oluştururken** klasör yapısına (Bölüm 3) uy.
5. **State management:** Sadece Riverpod kullan. setState(), Provider veya Bloc KULLANMA.
6. **Routing:** Sadece GoRouter kullan. Navigator.push KULLANMA.
7. **HTTP:** Sadece Dio kullan. http paketi KULLANMA.
8. **Test:** Değişiklik sonrası `flutter analyze` çalıştır, hata bırakma.
9. **Türkçe UI metinleri** hardcode edilebilir (i18n ikinci fazda eklenecek).

---

## 9. Wireframe → Ekran Eşleştirme

| Ekran # | Wireframe | Flutter Dosya | DB Tablosu |
|---------|-----------|---------------|------------|
| 1 | Giriş/Kayıt | auth/screens/login_screen.dart | kullanicilar |
| 2 | Dashboard | dashboard/screens/dashboard_screen.dart | tarlalar, hava_durumu_kayitlari |
| 3 | Tarla Detay | tarla_detay/screens/tarla_detay_screen.dart | bakim_tavsiyeleri, hava_durumu_kayitlari |
| 4 | Toprak Analizi | analiz/screens/analiz_screen.dart | toprak_analizleri |
| 5 | AI Sonuç | analiz/widgets/oneri_bottom_sheet.dart | urun_onerileri, urun_fiyatlari |
| 6 | Geçmiş | gecmis/screens/gecmis_screen.dart | v_gecmis_analizler |
| 7 | Profil | profil/screens/profil_screen.dart | kullanicilar, urun_fiyatlari |

---

## CHANGELOG

| Tarih | Değişiklik | Detay |
|-------|-----------|-------|
| 2026-03-28 | İlk versiyon | ARCHITECTURE.md oluşturuldu. Wireframe + DB v2 şeması baz alındı. |
| 2026-05-19 | DRF API Genişletme | SensorDataViewSet, SensorReadingViewSet, SoilAnalysisViewSet eklendi. /sensors/data/ ve /sensors/latest/ özel action'ları. TokenVerifyView, SensorDataFilter, SensorReadingFilter eklendi. Postman koleksiyonu ve API dokümantasyonu oluşturuldu. |
