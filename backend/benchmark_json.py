import json
import orjson
import time
import os
import random
from pathlib import Path

def generate_data(num_items=100000):
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

def benchmark():
    print("Veri oluşturuluyor...")
    data = generate_data(500000)
    print(f"Toplam kayıt: {len(data)}")

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
