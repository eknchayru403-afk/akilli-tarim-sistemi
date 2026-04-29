import json
import orjson
import time
import os
import random
import tracemalloc
from pathlib import Path

def generate_data_dicts(num_items=100000):
    return [
        {
            "crop_name": f"crop_{i}",
            "nitrogen": random.random() * 100,
            "phosphorus": random.random() * 100,
            "potassium": random.random() * 100,
            "temperature": random.random() * 40,
            "humidity": random.random() * 100,
            "ph": random.random() * 14,
            "rainfall": random.random() * 200,
            "metadata": {"source": "sensor", "id": i, "tags": ["test", "data", "benchmark"]},
            "history": [random.random() for _ in range(10)]
        }
        for i in range(num_items)
    ]

class SensorData:
    __slots__ = ['crop_name', 'nitrogen', 'phosphorus', 'potassium', 'temperature', 'humidity', 'ph', 'rainfall', 'metadata', 'history']
    def __init__(self, i):
        self.crop_name = f"crop_{i}"
        self.nitrogen = random.random() * 100
        self.phosphorus = random.random() * 100
        self.potassium = random.random() * 100
        self.temperature = random.random() * 40
        self.humidity = random.random() * 100
        self.ph = random.random() * 14
        self.rainfall = random.random() * 200
        self.metadata = {"source": "sensor", "id": i, "tags": ["test", "data", "benchmark"]}
        self.history = [random.random() for _ in range(10)]

def serialize_sensor_data(obj):
    return {
        "crop_name": obj.crop_name,
        "nitrogen": obj.nitrogen,
        "phosphorus": obj.phosphorus,
        "potassium": obj.potassium,
        "temperature": obj.temperature,
        "humidity": obj.humidity,
        "ph": obj.ph,
        "rainfall": obj.rainfall,
        "metadata": obj.metadata,
        "history": obj.history
    }

def generate_data_slots(num_items=100000):
    return [SensorData(i) for i in range(num_items)]

def benchmark():
    num_records = 500000
    
    # Bellek ölçümünü başlat
    print("Veri oluşturuluyor (Sözlük/Dict Yapısı)...")
    tracemalloc.start()
    data_dicts = generate_data_dicts(num_records)
    current_dicts, peak_dicts = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"Toplam kayıt: {len(data_dicts)}")
    print(f"Bellek Tüketimi (Sözlükler): {peak_dicts / 1024 / 1024:.2f} MB")

    print("\nVeri oluşturuluyor (__slots__ Yapısı)...")
    tracemalloc.start()
    data_slots = generate_data_slots(num_records)
    current_slots, peak_slots = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"Bellek Tüketimi (__slots__): {peak_slots / 1024 / 1024:.2f} MB")
    
    # Performans testleri için orjson varsayılan yöntemini slot verisine ayarlayalım
    print("\n--- Serileştirme Karşılaştırması Başlıyor ---\n")
    data = data_dicts  # Serileştirme testlerine dict ile devam edelim ki adil olsun

    # Serialization - standard json
    start = time.time()
    json_str = json.dumps(data)
    json_dump_time = time.time() - start
    print(f"json.dumps süresi: {json_dump_time:.4f} saniye")

    # Serialization - orjson
    start = time.time()
    orjson_bytes = orjson.dumps(data)
    orjson_dump_time = time.time() - start
    print(f"orjson.dumps süresi: {orjson_dump_time:.4f} saniye")

    print(f"Hızlanma (Serialization): {json_dump_time / orjson_dump_time:.2f}x")

    # Deserialization - standard json
    start = time.time()
    _ = json.loads(json_str)
    json_load_time = time.time() - start
    print(f"json.loads süresi: {json_load_time:.4f} saniye")

    # Deserialization - orjson
    start = time.time()
    _ = orjson.loads(orjson_bytes)
    orjson_load_time = time.time() - start
    print(f"orjson.loads süresi: {orjson_load_time:.4f} saniye")

    print(f"Hızlanma (Deserialization): {json_load_time / orjson_load_time:.2f}x")

    # File I/O Benchmark
    with open("test_data_json.json", "w") as f:
        json.dump(data, f)
    with open("test_data_orjson.json", "wb") as f:
        f.write(orjson.dumps(data))

    start = time.time()
    with open("test_data_json.json", "r") as f:
        _ = json.load(f)
    json_file_load = time.time() - start
    print(f"json.load (dosya) süresi: {json_file_load:.4f} saniye")

    start = time.time()
    with open("test_data_orjson.json", "rb") as f:
        _ = orjson.loads(f.read())
    orjson_file_load = time.time() - start
    print(f"orjson.loads (dosya) süresi: {orjson_file_load:.4f} saniye")

    print(f"Hızlanma (Dosya Okuma): {json_file_load / orjson_file_load:.2f}x")
    
    os.remove("test_data_json.json")
    os.remove("test_data_orjson.json")

if __name__ == "__main__":
    benchmark()
