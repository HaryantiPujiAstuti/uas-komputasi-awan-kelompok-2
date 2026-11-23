import json
import time
import urllib.request
import urllib.error
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed

URL = "https://cc-kelompok2-c103e.containers.snapdeploy.app/predict"
TOTAL_REQUESTS = 300  # Ubah ke 10 dengan jeda untuk pengujian trafik ringan
CONCURRENCY = 10

PAYLOAD = json.dumps({
    "features": {
        "Sex": "M",
        "Length": 0.455,
        "Diameter": 0.365,
        "Height": 0.095,
        "Whole weight": 0.514,
        "Shucked weight": 0.2245,
        "Viscera weight": 0.101,
        "Shell weight": 0.15
    }
}).encode("utf-8")

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def send_request(_):
    req = urllib.request.Request(URL, data=PAYLOAD, headers=HEADERS, method="POST")
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            resp.read()
            return resp.status, time.perf_counter() - start
    except urllib.error.HTTPError as e:
        return e.code, time.perf_counter() - start
    except Exception:
        return 0, time.perf_counter() - start

def main():
    print(f"Menjalankan load test ke {URL}")
    print(f"Total Request: {TOTAL_REQUESTS} | Concurrency: {CONCURRENCY}\n")

    start_all = time.perf_counter()
    results = []

    with ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
        futures = [executor.submit(send_request, i) for i in range(TOTAL_REQUESTS)]
        for f in as_completed(futures):
            results.append(f.result())

    total_time = time.perf_counter() - start_all
    latencies = sorted([r[1] for r in results])
    status_counts = Counter(r[0] for r in results)

    avg_lat = sum(latencies) / len(latencies)
    p50_lat = latencies[int(0.50 * len(latencies)) - 1]
    p95_lat = latencies[int(0.95 * len(latencies)) - 1]
    rps = TOTAL_REQUESTS / total_time

    print("=== HASIL LOAD TEST ===")
    print(f"Total Waktu Eksekusi : {total_time:.2f} detik")
    print(f"Rincian Status HTTP  : {dict(status_counts)}")
    print(f"Throughput           : {rps:.2f} req/detik")
    print(f"Latensi Rata-rata    : {avg_lat * 1000:.2f} ms")
    print(f"Latensi p50 (Median) : {p50_lat * 1000:.2f} ms")
    print(f"Latensi p95          : {p95_lat * 1000:.2f} ms ({p95_lat:.3f} detik)")

if __name__ == "__main__":
    main()
