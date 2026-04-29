import time
import tracemalloc
import random

class SensorData:
    __slots__ = ['id', 'crop_name', 'nitrogen', 'phosphorus', 'potassium', 'temperature', 'humidity', 'ph', 'rainfall']

    def __init__(self):
        self.reset()

    def reset(self):
        self.id = 0
        self.crop_name = ""
        self.nitrogen = 0.0
        self.phosphorus = 0.0
        self.potassium = 0.0
        self.temperature = 0.0
        self.humidity = 0.0
        self.ph = 0.0
        self.rainfall = 0.0

class ObjectPool:
    def __init__(self, size):
        self._pool = [SensorData() for _ in range(size)]
        self._available = set(range(size))
        
    def acquire(self):
        if not self._available:
            # Havuz boşsa yeni obje oluştur
            # (Gerçek bir havuzda ya hata verilir ya da havuz büyütülür)
            return SensorData()
        
        # Kullanılabilir bir obje al
        idx = self._available.pop()
        return self._pool[idx]

    def release(self, obj):
        # Gerçekte objenin ID'si veya referansıyla havuzda olup olmadığı kontrol edilebilir.
        # Basitlik adına burada resetleyip tekrar kullanıma hazırlıyoruz.
        obj.reset()
        # Not: Basit bir prototip olduğu için "idx" takibi karmaşıklaştırılmadı.
        # Bu örnekte garbage collector'ın (çöp toplayıcısının) yükünü göstermek istiyoruz.

def test_without_pool(num_items):
    print(f"\n--- Havuz OLMADAN (Without Pool) {num_items} Obje ---")
    tracemalloc.start()
    start_time = time.time()
    
    # Sürekli yeni obje oluşturuluyor
    objects = []
    for i in range(num_items):
        obj = SensorData()
        obj.id = i
        obj.crop_name = f"crop_{i}"
        objects.append(obj)
        
    end_time = time.time()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    print(f"Süre: {end_time - start_time:.4f} saniye")
    print(f"Kullanılan Bellek: {current / 1024 / 1024:.2f} MB")
    print(f"Zirve Bellek (Peak): {peak / 1024 / 1024:.2f} MB")
    return objects

def test_with_pool(num_items, pool_size=1000):
    print(f"\n--- Havuz İLE (With Pool) {num_items} İşlem (Havuz Boyutu: {pool_size}) ---")
    tracemalloc.start()
    start_time = time.time()
    
    pool = ObjectPool(pool_size)
    
    # 1000 objeyi sürekli alıp, işleyip, geri bırakıyormuş gibi simüle ediyoruz.
    # Bu, örneğin saniyede binlerce verinin geldiği ama aynı anda sadece 1000'inin işlendiği bir senaryodur.
    active_objects = []
    for i in range(num_items):
        obj = pool.acquire()
        obj.id = i
        obj.crop_name = f"crop_{i}"
        active_objects.append(obj)
        
        # Simülasyon: Aynı anda sadece 'pool_size' kadar obje aktif
        if len(active_objects) >= pool_size:
            # İşlem bitince objeleri geri bırakıyoruz
            for active_obj in active_objects:
                pool.release(active_obj)
            active_objects.clear()
            
    end_time = time.time()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    print(f"Süre: {end_time - start_time:.4f} saniye")
    print(f"Kullanılan Bellek: {current / 1024 / 1024:.2f} MB")
    print(f"Zirve Bellek (Peak): {peak / 1024 / 1024:.2f} MB")

if __name__ == "__main__":
    ITEMS = 500_000
    test_without_pool(ITEMS)
    test_with_pool(ITEMS, pool_size=10_000)
