# CVRP Solver

Proyek ini menyediakan implementasi untuk menyelesaikan **Capacitated Vehicle Routing Problem (CVRP)** menggunakan tiga pendekatan utama:

1. **Genetic Algorithm (GA)** - Pendekatan heuristik berbasis evolusi
2. **Greedy (Nearest Neighbor)** - Baseline heuristik sederhana
3. **Google OR-Tools** - Solver optimasi komersial

## Deskripsi Proyek

Capacitated Vehicle Routing Problem (CVRP) adalah masalah optimasi kombinatorial klasik di bidang logistik dan distribusi. Masalah ini melibatkan penentuan rute optimal untuk armada kendaraan dengan kapasitas terbatas untuk melayani sekumpulan pelanggan, dengan tujuan meminimalkan total jarak tempuh atau biaya transportasi.

### Komponen Utama

- **parser.py**: Parser untuk membaca file instance CVRP (.vrp format)
- **ga_vrp.py**: Implementasi Genetic Algorithm untuk CVRP
- **greedy_vrp.py**: Implementasi Greedy baseline (Nearest Neighbor)
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
   Tip: `requirements.txt` includes `ortools` and `matplotlib` (plotting library). If you prefer to install only some packages, install at least `ortools` and `matplotlib`.

## Penggunaan

### Format Input

Program menggunakan file instance CVRP dalam format standar:

- `DIMENSION`: Jumlah node (depot + pelanggan)
- `CAPACITY`: Kapasitas maksimal kendaraan
- `EDGE_WEIGHT_SECTION`: Matriks jarak antar node
- `DEMAND_SECTION`: Demand setiap node

### Menjalankan Genetic Algorithm

```bash
python ga_vrp.py [nama_file_instance.vrp] [num_runs]
```

Contoh (jalankan GA 5 kali pada instance 1_FaridFajar.vrp):

```bash
python ga_vrp.py 1_FaridFajar.vrp 5
Catatan: Jika argumen file tidak disertakan, skrip akan mencoba menggunakan `output_cvrp.vrp` sebagai default (lihat `INSTANCE_FILE = sys.argv[1] if len(sys.argv) > 1 else "output_cvrp.vrp"` di masing-masing skrip).

Default `num_runs`:
- GA (`ga_vrp.py`): 5
- Greedy (`greedy_vrp.py`): 5
- OR-Tools (`ortools_solver.py`): 1
```

Parameter GA dapat dimodifikasi di dalam kode (nilai default tercantum di pemanggilan `genetic_algorithm` pada file):

- `generations`: Jumlah generasi (default: 300)
- `pop_size`: Ukuran populasi (default: 150)
- `cx_prob`: Probabilitas crossover (default: 0.8)
- `mut_prob`: Probabilitas mutasi (default: 0.2)
- `elitism`: Banyak individu elit yang diteruskan (default: 1)
- `use_two_opt`: Aktifkan 2-opt (default: True)
- `two_opt_prob`: Probabilitas menerapkan 2-opt pada child (default: 0.3)

### Menjalankan OR-Tools Solver

```bash
python ortools_solver.py [nama_file_instance.vrp] [num_runs]
```

Contoh (jalankan OR-Tools 3 kali):

```bash
python ortools_solver.py 1_FaridFajar.vrp 3
```

Catatan: `ortools_solver.py` memanggil `solve_with_ortools(num_vehicles=1, time_limit_sec=30)` di dalam kode, sehingga `num_vehicles` dan `time_limit_sec` di-set pada pemanggilan fungsi; jika Anda ingin mengubah nilai tersebut, edit file `ortools_solver.py`.

### Menjalankan Greedy (Nearest Neighbor)

```bash
python greedy_vrp.py [nama_file_instance.vrp] [num_runs]
```

Contoh:

```bash
python greedy_vrp.py 1_FaridFajar.vrp 5
```

## Output

### Genetic Algorithm

Program akan menampilkan:

- Progress setiap 50 generasi (default `log_every` = 50)
- Solusi terbaik akhir
- Analisis rute: demand per rute, biaya per rute
- Ringkasan (dicetak dan disimpan) dalam format satu baris `GA_SUMMARY|...` dan pada CSV `<basename>_ga_summary.csv`.

Contoh kolom CSV/format ringkasan (GA):
`GA_SUMMARY|instance_file|best_cost|avg_cost|worst_cost|num_runs|best_run|best_seed|num_routes|num_nodes|num_customers|capacity|total_demand|best_route|chromosome|total_time_sec|avg_time_per_run_sec`

### OR-Tools

Program akan menampilkan:

- Status penyelesaian
- Rute optimal
- Total jarak
- Analisis rute detail
- Ringkasan (dicetak dan disimpan) dalam format `ORTOOLS_SUMMARY|...` dan pada CSV `<basename>_ortools_summary.csv`.

Contoh kolom CSV/format ringkasan (OR-Tools):
`ORTOOLS_SUMMARY|instance_file|best_cost|avg_cost|worst_cost|num_runs|best_run|num_routes|num_nodes|num_customers|capacity|total_demand|route|best_solve_time_sec|avg_solve_time_sec`

### Greedy

Program akan menampilkan ringkasan (print block) dan menyimpan CSV; contoh CSV kolom:
`best_cost|avg_cost|worst_cost|num_runs|best_run|num_routes|capacity|best_route|best_time_sec|avg_time_sec` (disimpan sebagai `<basename>_greedy_summary.csv`).

Catatan: Berbeda dari GA/OR-Tools, skrip `greedy_vrp.py` tidak mencetak single-line `GREEDY_SUMMARY|...` di STDOUT; ia mencetak blok "=== GREEDY SUMMARY ===" dan menyimpan hasil ke CSV.

## Struktur File

```
cv-rp-solver/
├── parser.py              # Parser untuk file .vrp
├── ga_vrp.py             # Implementasi Genetic Algorithm
├── greedy_vrp.py         # Implementasi Greedy baseline
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
GA_SUMMARY|1_FaridFajar.vrp|14234.80|15234.50|16543.20|5|3|142|3|45|44|30.00|120.50|0-5-12-8-0/0-2-15-0/0-7-22-0|5-12-8-15-2-7-22|12.3456|2.4691
```

### OR-Tools

```
=== OR-TOOLS RESULT ===
Instance: 1_FaridFajar.vrp
Objective (total distance): 13892.4
Routes: 3 vehicles
Route 1: 0 -> 3 -> 9 -> 14 -> 0 (demand: 29.5/30.0, cost: 4234.1)
...
ORTOOLS_SUMMARY|1_FaridFajar.vrp|13892.40|13892.40|13892.40|1|1|3|45|44|30.00|118.20|0-3-9-14-0/0-1-6-11-0/0-4-13-0|0.3456|0.3456
```

### Greedy

```

=== GREEDY SUMMARY ===
Best cost : 21443.00
Best run index : 1
Avg cost : 21443.00
Worst cost : 21443.00
Avg time (sec) : 0.0001

```

Contoh CSV (saved as `<basename>_greedy_summary.csv`) header and a sample row:

```

instance_file,best_cost,avg_cost,worst_cost,num_runs,best_run,num_routes,capacity,best_route,best_time_sec,avg_time_sec
1_FaridFajar.vrp,21443.00,21443.00,21443.00,5,1,1,30.0,0-37-43-19-44-6-2-11-30-33-17-27-23-26-1-35-20-3-40-42-13-29-15-31-16-39-28-18-25-7-38-32-22-14-36-12-21-24-41-34-9-10-8-5-4-0,0.0001,0.0001

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

### Greedy (Nearest Neighbor)

1. **Heuristics**: Mencari customer terdekat yang masih dapat dimasukkan ke rute tanpa melanggar kapasitas.
2. **Decoding**: Rute akan berakhir di depot ketika tidak ada customer tersisa yang dapat dimasukkan ke rute saat ini.

### OR-Tools

Menggunakan constraint programming solver dari Google dengan:

- Distance callback untuk matriks jarak
- Capacity constraints per vehicle
- Guided Local Search metaheuristic

## Benchmarking

Untuk membandingkan performa ketiga metode (GA, Greedy, dan OR-Tools):

1. Jalankan GA dengan multiple runs untuk mendapatkan statistik (best/avg/worst)
2. Jalankan Greedy sebagai baseline (multiple runs)
3. Jalankan OR-Tools dengan berbagai time limit dan (opsional) jumlah kendaraan
4. Bandingkan best/average cost dan waktu komputasi untuk setiap metode

## Referensi

- OR-Tools Documentation: https://developers.google.com/optimization
- CVRP Benchmark Instances: http://vrp.atd-lab.inf.puc-rio.br/index.php/en/
- Genetic Algorithm for VRP: Literatur akademik terkait
