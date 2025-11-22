# CVRP Solver

Proyek ini menyediakan implementasi untuk menyelesaikan **Capacitated Vehicle Routing Problem (CVRP)** menggunakan dua pendekatan utama:

1. **Genetic Algorithm (GA)** - Pendekatan heuristik berbasis evolusi
2. **Google OR-Tools** - Solver optimasi komersial

## Deskripsi Proyek

Capacitated Vehicle Routing Problem (CVRP) adalah masalah optimasi kombinatorial klasik di bidang logistik dan distribusi. Masalah ini melibatkan penentuan rute optimal untuk armada kendaraan dengan kapasitas terbatas untuk melayani sekumpulan pelanggan, dengan tujuan meminimalkan total jarak tempuh atau biaya transportasi.

### Komponen Utama

- **parser.py**: Parser untuk membaca file instance CVRP (.vrp format)
- **ga_vrp.py**: Implementasi Genetic Algorithm untuk CVRP
- **ortools_solver.py**: Solver menggunakan Google OR-Tools
- **File instance**: Contoh instance CVRP (1_FaridFajar.vrp, dll.)

## Instalasi

### Persyaratan Sistem

- Python 3.8 atau lebih baru
- pip (package manager Python)

### Langkah Instalasi

1. **Clone atau download repository ini**

2. **Buat virtual environment (opsional tapi direkomendasikan)**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # atau
   .venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Penggunaan

### Format Input

Program menggunakan file instance CVRP dalam format standar:
- `DIMENSION`: Jumlah node (depot + pelanggan)
- `CAPACITY`: Kapasitas maksimal kendaraan
- `EDGE_WEIGHT_SECTION`: Matriks jarak antar node
- `DEMAND_SECTION`: Demand setiap node

### Menjalankan Genetic Algorithm

```bash
python ga_vrp.py [nama_file_instance.vrp]
```

Contoh:
```bash
python ga_vrp.py 1_FaridFajar.vrp
```

Parameter GA dapat dimodifikasi di dalam kode:
- `generations`: Jumlah generasi (default: 300)
- `pop_size`: Ukuran populasi (default: 150)
- `cx_prob`: Probabilitas crossover (default: 0.8)
- `mut_prob`: Probabilitas mutasi (default: 0.2)

### Menjalankan OR-Tools Solver

```bash
python ortools_solver.py [nama_file_instance.vrp]
```

Contoh:
```bash
python ortools_solver.py 1_FaridFajar.vrp
```

Parameter OR-Tools:
- `num_vehicles`: Jumlah kendaraan (default: 1, dapat ditingkatkan)
- `time_limit_sec`: Batas waktu pencarian (default: 30 detik)

## Output

### Genetic Algorithm
Program akan menampilkan:
- Progress setiap 50 generasi
- Solusi terbaik akhir
- Analisis rute: demand per rute, biaya per rute
- Ringkasan dalam format: `GA_SUMMARY|file|best_cost|avg_cost|worst_cost|runs|best_run|best_seed|num_routes|num_nodes|num_customers|capacity|total_demand|route_string|chromosome`

### OR-Tools
Program akan menampilkan:
- Status penyelesaian
- Rute optimal
- Total jarak
- Analisis rute detail
- Ringkasan dalam format: `ORTOOLS_SUMMARY|file|total_distance|num_routes|num_nodes|num_customers|capacity|total_demand|route_string`

## Struktur File

```
cv-rp-solver/
├── parser.py              # Parser untuk file .vrp
├── ga_vrp.py             # Implementasi Genetic Algorithm
├── ortools_solver.py     # Solver OR-Tools
├── requirements.txt      # Dependencies Python
├── README.md             # Dokumentasi ini
├── 1_FaridFajar.vrp      # Instance contoh 1
├── 2_WahyuDwi.vrp        # Instance contoh 2
├── 3_ChabibMaulana.vrp   # Instance contoh 3
└── 4_MochAlfian.vrp      # Instance contoh 4
```

## Contoh Output

### Genetic Algorithm
```
Gen 50: best fitness = 15423.5
Gen 100: best fitness = 14876.2
...
=== BEST OVERALL SOLUTION ===
Instance: 1_FaridFajar.vrp
Best fitness: 14234.8
Routes: 3 vehicles
Route 1: 0 -> 5 -> 12 -> 8 -> 0 (demand: 28.0/30.0, cost: 4567.2)
...
GA_SUMMARY|1_FaridFajar.vrp|14234.8|15234.5|16543.2|5|3|142|3|45|44|30.0|120.5|0-5-12-8-0/0-2-15-0/0-7-22-0|5-12-8-15-2-7-22
```

### OR-Tools
```
=== OR-TOOLS RESULT ===
Instance: 1_FaridFajar.vrp
Objective (total distance): 13892.4
Routes: 3 vehicles
Route 1: 0 -> 3 -> 9 -> 14 -> 0 (demand: 29.5/30.0, cost: 4234.1)
...
ORTOOLS_SUMMARY|1_FaridFajar.vrp|13892.4|3|45|44|30.0|118.2|0-3-9-14-0/0-1-6-11-0/0-4-13-0
```

## Algoritma Detail

### Genetic Algorithm

1. **Representasi**: Permutasi pelanggan (customers)
2. **Decoding**: Mengubah permutasi menjadi rute kendaraan dengan mempertimbangkan kapasitas
3. **Fitness**: Total jarak + penalti untuk pelanggaran kapasitas
4. **Operator**:
   - Selection: Tournament selection
   - Crossover: Order Crossover (OX)
   - Mutation: Swap mutation
5. **Local Search**: 2-opt untuk intensifikasi

### OR-Tools

Menggunakan constraint programming solver dari Google dengan:
- Distance callback untuk matriks jarak
- Capacity constraints per vehicle
- Guided Local Search metaheuristic

## Benchmarking

Untuk membandingkan performa kedua metode:

1. Jalankan GA dengan multiple runs untuk mendapatkan statistik
2. Jalankan OR-Tools dengan berbagai time limit
3. Bandingkan best/average cost dan waktu komputasi

## Pengembangan Lanjutan

Ide untuk pengembangan:
- Implementasi algoritma metaheuristik lain (Tabu Search, Simulated Annealing)
- Paralelisasi GA untuk performa lebih baik
- GUI untuk visualisasi rute
- Support untuk multiple depots
- Integration dengan Google Maps API untuk jarak real-world

## Kontribusi

Kontribusi sangat diterima! Silakan:

1. Fork repository
2. Buat branch fitur baru (`git checkout -b feature/AmazingFeature`)
3. Commit perubahan (`git commit -m 'Add some AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buat Pull Request

## Lisensi

Proyek ini menggunakan lisensi MIT. Lihat file `LICENSE` untuk detail lebih lanjut.

## Referensi

- OR-Tools Documentation: https://developers.google.com/optimization
- CVRP Benchmark Instances: http://vrp.atd-lab.inf.puc-rio.br/index.php/en/
- Genetic Algorithm for VRP: Literatur akademik terkait

## Kontak

Jika ada pertanyaan atau masalah, silakan buat issue di repository ini.