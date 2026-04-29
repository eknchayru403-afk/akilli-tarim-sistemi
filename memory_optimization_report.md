# Akıllı Tarım Yönetim Sistemi - Bellek Optimizasyonu Raporu

## 1. Giriş ve Amaç
Bu rapor, Akıllı Tarım Yönetim Sistemi (ATYS) arka ucunda (backend) yüksek hacimli veri işlerken ortaya çıkan aşırı RAM (Bellek) tüketimini azaltmak adına yapılan "Nesne Havuzu (Object Pool)" ve `__slots__` optimizasyon testlerinin sonuçlarını içermektedir.

Sistemin saniyede binlerce sensörden veri aldığı veya yüz binlerce geçmiş kaydın işlendiği senaryolarda standart Python veri yapılarının (Dictionary/Sözlük) oluşturduğu bellek yükünün hafifletilmesi hedeflenmiştir.

## 2. Test Edilen Optimizasyon Yöntemleri

### Yöntem A: `__slots__` Kullanımı
Python'da objeler içlerindeki verileri tutmak için varsayılan olarak dinamik bir sözlük (`__dict__`) kullanır. `__slots__` tanımlandığında dinamik yapı devreden çıkar ve değişkenler için bellekte sabit yer ayrılır.
- **Hedef:** Mevcut `benchmark_json.py` içerisindeki veri üretimini `__slots__` destekli sınıfa çevirmek.
- **Beklenti:** %10 - %20 arası temel bir bellek tasarrufu.

### Yöntem B: Nesne Havuzu (Object Pool) Deseni
Milyonlarca veriyi işlerken sürekli yeni obje oluşturup silmek (garbage collection) yerine, `N` adet objenin (havuz) yaratılıp bu objelerin tekrar tekrar kullanıldığı mimaridir.
- **Hedef:** `memory_pool_prototype.py` üzerinden 500.000 veri işleme senaryosunda havuz kullanıldığında oluşan durumu gözlemlemek.
- **Beklenti:** RAM kullanımında dramatik (%90+) düşüş.

---

## 3. Optimizasyon Sonuçları

### Test 1: Temel Veri Yapıları Karşılaştırması (`benchmark_json.py` - 500.000 Kayıt)
Aynı anda 500.000 adet sensör verisi (10 parametreli karmaşık veri) belleğe yüklendiğinde alınan sonuçlar:

| Veri Yapısı | Zirve Bellek (Peak Memory) Tüketimi | Optimizasyon Oranı |
| :--- | :--- | :--- |
| **Standart Python Sözlüğü (Dict)** | 585.60 MB | Başlangıç Durumu |
| **`__slots__` Sınıfı** | 509.31 MB | ~ %13 Tasarruf |

*Not:* İç içe geçmiş veriler (listeler ve alt sözlükler) devam ettiği için `__slots__` tek başına mucizevi bir çözüm olmamış, ancak stabil bir %13'lük bellek tasarrufu sağlamıştır.

### Test 2: Nesne Havuzu Performansı (`memory_pool_prototype.py` - 500.000 İşlem)
Aynı 500.000 objenin işlenmesi sırasında, standart üretim ile 10.000 kapasiteli nesne havuzu (Pool) kullanımının karşılaştırılması:

| Senaryo | Zirve Bellek (Peak Memory) Tüketimi | CPU İşlem Süresi |
| :--- | :--- | :--- |
| **Havuz OLMADAN (Sürekli Obje Yaratımı)** | 93.51 MB | 2.07 Saniye |
| **Havuz İLE (10.000 Kapasiteli Object Pool)**| **3.45 MB** | 2.58 Saniye |

*(Bu testte veriler saf nesne olarak tutulduğu için sözlük bazlı test 1'den temel bellek boyutu daha düşüktür.)*

## 4. Teknik Çıkarımlar ve Sonuç

1. **Bellek Havuzu Gerçekten Hayat Kurtarıcıdır:** Sürekli obje yaratmak yerine 10.000'lik bir havuz kullandığımızda, bellek tüketimi **93.5 MB'dan 3.45 MB'a (%96 oranında)** düşmüştür. Bu, IoT tabanlı tarım sensörlerinden sürekli veri aktığı (Streaming) senaryolarda sunucu çökmesini (Out Of Memory) engelleyecek en kritik yapıdır.
2. **Toplu Veri Aktarımları İçin:** Eğer veriler anlık işleniyorsa (örneğin WebSocket veya RabbitMQ üzerinden akıyorsa) kesinlikle **Object Pool** kullanılmalıdır. Eğer veriler JSON olarak dışarı aktarılacaksa (Serialization) `__slots__` + `orjson` kombinasyonu en iyi performansı (hız + biraz daha az bellek) sunmaktadır.

## 5. Önerilen Sonraki Adımlar
- IoT sensör verilerini karşılayan Kafka/RabbitMQ Consumer servislerine `Object Pool` entegre edilmesi.
- Veritabanından (Django ORM) veri çekerken `.values()` veya `.iterator()` kullanılarak ORM objesi yerine doğrudan havuzdaki objelere aktarım yapılması.
