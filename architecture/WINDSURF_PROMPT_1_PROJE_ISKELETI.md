# Windsurf Prompt 1: Flutter Proje İskeleti Kurulumu

## Bağlam
Akıllı Tarım Yönetim Sistemi mobil uygulamasını Flutter ile geliştiriyoruz.
Önce ARCHITECTURE.md dosyasını oku — tüm kurallar, klasör yapısı ve tech stack orada tanımlı.

## Görev
Aşağıdaki adımları SIRAYLA uygula. Her adımı tamamladıktan sonra bir sonrakine geç.

### Adım 1: Flutter projesi oluştur
```
flutter create --org com.ats akilli_tarim
```

### Adım 2: pubspec.yaml bağımlılıklarını ekle
```yaml
dependencies:
  flutter:
    sdk: flutter
  flutter_riverpod: ^2.6.1
  go_router: ^14.6.2
  dio: ^5.7.0
  flutter_dotenv: ^5.2.1
  google_fonts: ^6.2.1
  intl: ^0.19.0

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^5.0.0
```

### Adım 3: Klasör yapısını oluştur
ARCHITECTURE.md Bölüm 3'teki yapıyı birebir oluştur.
Boş .gitkeep dosyaları koy ki klasörler git'te korunsun.

### Adım 4: core/ dosyalarını yaz

**core/constants/app_colors.dart:**
Wireframe'den alınan renk paleti:
- primary: #2E7D32
- primaryLight: #4CAF50
- surface: #FFFFFF
- background: #F5F5F5
- warning: #FF9800
- error: #D32F2F
- accent: #9C27B0 (Kaggle butonu)
- textPrimary: #212121
- textSecondary: #757575

**core/theme/app_theme.dart:**
Light ve dark ThemeData. Google Fonts kullanma, sistem fontlarıyla git.
AppBar theme: koyu yeşil arka plan, beyaz metin.
Card theme: elevation 0, border radius 16.
ElevatedButton: yeşil arka plan, rounded corners (24 radius).

**core/constants/api_endpoints.dart:**
```dart
class ApiEndpoints {
  static const String baseUrl = String.fromEnvironment('API_BASE_URL', defaultValue: 'http://10.0.2.2:8000');
  static const String openWeatherBaseUrl = 'https://api.openweathermap.org/data/2.5';
  // Auth
  static const String login = '/api/auth/login';
  static const String register = '/api/auth/register';
  // Tarlalar
  static const String tarlalar = '/api/tarlalar';
  // Analiz
  static const String analizBaslat = '/api/analiz/baslat';
  static const String simulasyon = '/api/analiz/simulasyon';
  // Hava durumu
  static const String havaDurumu = '/weather';
  static const String havaForecast = '/forecast';
}
```

**core/network/dio_client.dart:**
Singleton Dio instance. BaseOptions: baseUrl, connectTimeout 10s, receiveTimeout 15s.
Interceptor: Authorization header (Bearer token), logging.

### Adım 5: Routing kur (app.dart)

GoRouter ile ARCHITECTURE.md Bölüm 4'teki route yapısını kur.
ShellRoute ile BottomNavigationBar (3 sekme: Ana Sayfa, Geçmiş, Profil).
Auth guard: token yoksa /login'e yönlendir.

### Adım 6: main.dart

```dart
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await dotenv.load(fileName: '.env');
  runApp(const ProviderScope(child: AkilliTarimApp()));
}
```

### Adım 7: Her ekran için boş scaffold oluştur

Her screen dosyasında sadece:
- Scaffold + AppBar (ekran adı)
- Center(child: Text('Ekran adı — yapılacak'))
- Gerekli Riverpod ConsumerWidget yapısı

### Adım 8: flutter analyze çalıştır, hata kalmadığını doğrula.

### Adım 9: ARCHITECTURE.md CHANGELOG'a ekle:
"2026-03-28 | Proje iskeleti | Flutter projesi oluşturuldu, routing, tema, klasör yapısı kuruldu."

## Dikkat
- ARCHITECTURE.md ve .windsurfrules kurallarına uy.
- Hiçbir ekranın iç mantığını YAZMA. Sadece boş scaffold.
- setState() KULLANMA. Her şey Riverpod.
- Navigator.push KULLANMA. Her şey GoRouter.
