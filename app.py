from flask import Flask, request, jsonify

app = Flask(__name__)

# Sistemin durumunu kontrol etmek için GET uç noktası
@app.route('/status', methods=['GET'])
def check_status():
    # Sistem aktif mi kontrolü
    return jsonify({"durum": "Sistem Aktif", "mesaj": "Akıllı Tarım İzleniyor"})

# Sensörden veri almak için POST uç noktası
@app.route('/update-sensor', methods=['POST'])
def update_sensor():
    data = request.get_json()
    
    sensor_type = data.get('type')
    value = data.get('value')

    print(f"Gelen Veri -> Tip: {sensor_type}, Değer: {value}")

    # Akıllı Mantık: Eğer nem %30'dan az ise pompayı çalıştır
    if sensor_type == 'soil_moisture' and value < 30.0:
        return jsonify({
            "sonuc": "Su Pompası ÇALIŞTIRILDI",
            "aksiyon": "OTOMATIK_SULAMA"
        }), 200

    return jsonify({"sonuc": "Veri başarıyla alındı"}), 200

if __name__ == '__main__':
    # Sunucuyu başlat
    app.run(debug=True)
