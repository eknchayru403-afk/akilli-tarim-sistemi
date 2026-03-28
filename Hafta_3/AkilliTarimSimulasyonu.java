import java.util.Random;

/**
 * Akilli Tarim Sistemi - Karar Destek Algoritmasi ve Simulasyonu
 * Hazirlayan: Hayrunnisa Ekinci
 */
public class AkilliTarimSimulasyonu {

    public static void main(String[] args) {
        Random rastgele = new Random();
        
        System.out.println("=== AKILLI TARIM OTOMASYONU CALISIYOR ===");
        System.out.println("Sensor verileri simüle ediliyor...\n");

        // 5 farkli veri ölçümü yaparak sistemin nasil karar verdigini kanitlayalim
        for (int i = 1; i <= 5; i++) {
            // Sensorlerden gelen sanal veriler
            double nem = 10 + (rastgele.nextDouble() * 60); // %10 ile %70 arasi nem
            double sicaklik = 15 + (rastgele.nextDouble() * 30); // 15-45 derece arasi sicaklik
            
            System.out.println("OLCUM #" + i);
            System.out.println("Sensor -> Nem: %" + String.format("%.2f", nem) + " | Sicaklik: " + String.format("%.2f", sicaklik) + "C");

            // OPTIMIZASYON ALGORITMASI (Karar Mekanizmasi)
            if (nem < 30.0) {
                if (sicaklik > 38.0) {
                    System.out.println("KARAR: Sicaklik cok yuksek! Su israfini onlemek icin sulama ERTELENDI, fanlar acildi.");
                } else {
                    System.out.println("KARAR: Nem dusuk. Sulama pompasi AKTIF hale getirildi.");
                }
            } else if (nem > 70.0) {
                System.out.println("KARAR: Yuksek nem algilandi. Havalandirma kapaklari ACILDI.");
            } else {
                System.out.println("DURUM: Kosullar ideal. Sistem tasarruf modunda.");
            }
            System.out.println("-------------------------------------------");
        }
        System.out.println("=== ANALIZ TAMAMLANDI ===");
    }
}
