# Windsurf Prompt 2: Giriş Ekranı (Ekran 1)

## Bağlam
ARCHITECTURE.md dosyasını oku. Proje iskeleti hazır.
Wireframe referansı: Giriş ekranı — koyu yeşil header, yaprak ikonu, "Toprağın Geleceği Burada" sloganı, e-posta + şifre alanları, "Giriş Yap" butonu, "Yeni Kayıt Oluştur" linki.

## Görev
`lib/features/auth/` altındaki dosyaları implemente et.

### 1. Model: user_model.dart
```dart
class UserModel {
  final String id;
  final String adSoyad;
  final String email;
  final String? konumAdi;
  final String? profilFotoUrl;
  final String token; // JWT

  // fromJson, toJson factory constructor
}
```

### 2. Repository: auth_repository.dart
- `login(String email, String password)` → `Future<UserModel>`
- `register(String adSoyad, String email, String password)` → `Future<UserModel>`
- Dio client kullan (core/network/dio_client.dart)
- Backend henüz yok, şimdilik mock response döndür:
  ```dart
  // TODO: Backend hazır olunca mock'u kaldır
  await Future.delayed(Duration(seconds: 1));
  return UserModel(id: 'mock-id', adSoyad: 'Ahmet Yılmaz', email: email, token: 'mock-token', konumAdi: 'Elazığ, Merkez');
  ```

### 3. Provider: auth_provider.dart
- `authStateProvider`: AsyncNotifierProvider — login/logout state yönetimi
- `currentUserProvider`: mevcut kullanıcı bilgisi
- Login başarılı → GoRouter ile /dashboard'a yönlendir
- Token'ı secure storage'a kaydet (TODO: flutter_secure_storage eklenecek)

### 4. Ekranlar

**login_screen.dart:**
Wireframe'e sadık kal:
- Üstte koyu yeşil curved header (%30 ekran yüksekliği)
- Ortada yaprak ikonu (Icons.eco) ve "Akıllı Tarım" başlığı
- "Toprağın Geleceği Burada" alt başlık
- Beyaz kart içinde:
  - E-POSTA label + TextFormField (Icons.mail prefix)
  - ŞİFRE label + TextFormField (Icons.lock prefix, obscure toggle)
  - "Unuttum?" linki sağ üstte
  - "Giriş Yap >" yeşil ElevatedButton (full width, 56px height)
  - "Hesabınız yok mu? Yeni Kayıt Oluştur" linki altta
- Form validation: email format, şifre min 6 karakter
- Loading state: buton disabled + CircularProgressIndicator
- Error state: SnackBar ile hata mesajı

**register_screen.dart:**
- login_screen ile benzer layout
- Ek alanlar: Ad Soyad, Şifre Tekrar
- "Kayıt Ol" butonu
- "Zaten hesabınız var mı? Giriş Yap" linki

### Dikkat
- Renkleri app_colors.dart'tan al, hardcode YAZMA.
- TextStyle'ları theme'dan al.
- Riverpod ConsumerWidget kullan.
- GoRouter ile navigate et.
- ARCHITECTURE.md CHANGELOG'u güncelle.
