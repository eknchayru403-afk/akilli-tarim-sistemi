package com.smartagri.system;

import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;
import java.util.Map;

/**
 * Akıllı Tarım Sistemi için API Denetleyicisi.
 * Bu sınıf، sensör verilerini alır ve sulama sistemini kontrol eder.
 */
@RestController
@RequestMapping("/api/v1/agriculture")
public class SmartAgriController {

    // Sensörden (NodeMCU/ESP32) gelen verileri almak için kullanılır
    @PostMapping("/update-sensor")
    public ResponseEntity<String> updateSensorData(@RequestBody Map<String, Object> payload) {
        String sensorType = (String) payload.get("type");
        Double value = Double.parseDouble(payload.get("value").toString());

        // Veriyi terminale yazdır (Kontrol amaçlı)
        System.out.println("Gelen Veri: " + sensorType + " Değer: " + value);

        // Akıllı mantık: Nem %30'un altındaysa pompayı çalıştır
        if (sensorType.equals("soil_moisture") && value < 30.0) {
            return ResponseEntity.ok("Su Pompası Çalıştırıldı (Otomatik)");
        }

        return ResponseEntity.ok("Veri Alındı.");
    }

    // Sistemin çalışıp çalışmadığını kontrol eden uç nokta
    @GetMapping("/status")
    public String checkStatus() {
        return "Sistem Aktif.";
    }
}
