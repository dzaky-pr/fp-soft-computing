# CVRP Solver

Proyek ini menyediakan implementasi untuk menyelesaikan **Capacitated Vehicle Routing Problem (CVRP)** menggunakan beberapa pendekatan utama:

1. **Genetic Algorithm (GA)** – Metaheuristik evolusioner
2. **Greedy (Nearest Neighbor)** – Baseline heuristik sederhana
3. **Tabu Search** – Metaheuristik lokal dengan memori (tabu list)
4. **Google OR-Tools** – Solver optimasi dari Google

Selain itu, tersedia skrip **`benchmark_all.py`** untuk menjalankan semua algoritma pada beberapa instance sekaligus dan menggabungkan hasilnya ke satu file CSV.

---

## Deskripsi Proyek

Capacitated Vehicle Routing Problem (CVRP) adalah masalah optimasi kombinatorial di bidang logistik/distribusi. Kita ingin menentukan rute optimal untuk armada kendaraan dengan kapasitas terbatas untuk melayani sekumpulan pelanggan, dengan tujuan meminimalkan total jarak tempuh atau biaya transportasi.

### Komponen Utama

- **`parser.py`**  
  Parser untuk membaca file instance CVRP (`.vrp` format) dan mengembalikan:

  - `n` (jumlah node = depot + pelanggan),
  - `capacity`,
  - matriks jarak `dist[n][n]`,
  - `demands[n]`.

- **`ga_vrp.py`**  
  Implementasi **Genetic Algorithm** untuk CVRP:

  - Representasi: permutasi pelanggan.
  - Decoding: `decode_routes` yang membagi menjadi beberapa rute dengan batas kapasitas.
  - Fitness: total jarak + penalti jika overload kapasitas.
  - Operator: tournament selection, Order Crossover (OX), swap mutation.
  - Local search opsional: 2-opt.

- **`tabu_vrp.py`**  
  Implementasi **Tabu Search**:

  - Representasi & decoding sama dengan GA.
  - Neighborhood: semua solusi yang diperoleh dari **swap** dua pelanggan.
  - Tabu list: menyimpan pasangan pelanggan yang baru di-swap.
  - Aspiration: move tabu boleh jika menghasilkan solusi global terbaik baru.
  - Stopping: `max_iters`, `max_no_improve`, dan/atau time limit per run.

- **`greedy_vrp.py`**  
  Implementasi **Greedy Nearest Neighbor**:

  - Selalu pilih customer terdekat yang masih bisa dimasukkan ke rute (tidak melanggar kapasitas).
  - Jika tidak ada lagi customer yang muat, rute ditutup dan kendaraan kembali ke depot.
  - Digunakan sebagai baseline deterministik.

- **`ortools_solver.py`**  
  Solver menggunakan **Google OR-Tools Routing**:

  - Distance callback menggunakan matriks `DIST`.
  - Demand & kapasitas dimodelkan sebagai dimension dengan kapasitas per kendaraan.
  - Metaheuristik: Guided Local Search (GLS).
  - Time limit per run diset untuk fairness dengan GA dan Tabu.

- **`benchmark_all.py`**  
  Menjalankan **Greedy, GA, Tabu, dan OR-Tools** untuk setiap instance `.vrp` yang terdaftar di `INSTANCE_FILES`, membaca baris ringkasan dari setiap skrip, dan menggabungkannya ke satu file `benchmark_summary.csv`.

## Instalasi

### Persyaratan Sistem

- Python 3.8 atau lebih baru
- `pip` sebagai package manager

### Langkah Instalasi

1. **Clone atau download repository ini**

2. (Opsional) Buat virtual environment:

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

   File `requirements.txt` memuat: `ortools` dan `matplotlib`.

## Penggunaan

### Format Input (.vrp)

Program menggunakan file instance CVRP dengan format standar:

```
DIMENSION : <n>        # jumlah node (depot + pelanggan)
CAPACITY : <C>         # kapasitas kendaraan
EDGE_WEIGHT_SECTION    # matriks jarak n × n
... n baris matriks ...
DEMAND_SECTION
1 <d1>
2 <d2>
...
n <dn>
```

**Contoh minimal**:

```
DIMENSION : 25
CAPACITY : 30
EDGE_WEIGHT_SECTION
... 25 baris matriks 25x25 ...
DEMAND_SECTION
1 0      # depot, demand = 0
2 5
3 3
...
25 2
```

Parser mengasumsikan format ini konsisten.

**Catatan**: Secara praktis diasumsikan setiap `demand_i ≤ CAPACITY` agar solusi feasible (tidak ada customer yang demand-nya melebihi kapasitas kendaraan).

---

### 1. Menjalankan Genetic Algorithm (GA)

```bash
python ga_vrp.py [nama_file_instance.vrp] [num_runs]
```

**Contoh** (jalankan GA 5 kali pada instance 1_FaridFajar.vrp):

```bash
python ga_vrp.py 1_FaridFajar.vrp 5
```

Jika argumen file tidak disertakan, skrip akan memakai default:

```python
INSTANCE_FILE = sys.argv[1] if len(sys.argv) > 1 else "output_cvrp.vrp"
```

**Default `num_runs` (jika argumen kedua tidak diberikan)**:

- GA (`ga_vrp.py`): 5 run
- Tabu (`tabu_vrp.py`): 5 run
- OR-Tools (`ortools_solver.py`): 1 run
- Greedy (`greedy_vrp.py`): hanya 1 run (deterministik, tidak ada `num_runs`)

**Parameter GA** dapat dimodifikasi di dalam kode (pemanggilan `genetic_algorithm`):

- `generations` (default: 300)
- `pop_size` (default: 150)
- `cx_prob` (default: 0.8)
- `mut_prob` (default: 0.2)
- `elitism` (default: 1)
- `use_two_opt` (default: True)
- `two_opt_prob` (default: 0.3)
- `time_limit_sec` (default: 10 detik per run, untuk fairness dengan Tabu & OR-Tools)

---

### 2. Menjalankan Tabu Search

```bash
python tabu_vrp.py [nama_file_instance.vrp] [num_runs]
```

**Contoh**:

```bash
python tabu_vrp.py 1_FaridFajar.vrp 5
```

**Parameter penting** di dalam `tabu_vrp.py`:

- `max_iters` (default: 500)
- `tabu_tenure` (default: 10)
- `max_no_improve` (default: 150)
- `time_limit_sec` (default: 10 detik per run, untuk fairness dengan GA & OR-Tools)

---

### 3. Menjalankan Greedy (Nearest Neighbor)

```bash
python greedy_vrp.py [nama_file_instance.vrp]
```

**Contoh**:

```bash
python greedy_vrp.py 1_FaridFajar.vrp
# atau tanpa argumen (default: output_cvrp.vrp)
python greedy_vrp.py
```

Greedy dijalankan **sekali** (deterministik). Skrip akan:

- Menghitung rute dengan strategi nearest neighbor + cek kapasitas.
- Mencetak ringkasan ke STDOUT (termasuk baris `GREEDY_SUMMARY|...`).
- Menyimpan hasil ke `<basename>_greedy_summary.csv`.
- Menyimpan plot rute ke `<basename>_greedy_route.png`.

---

### 4. Menjalankan OR-Tools Solver

```bash
python ortools_solver.py [nama_file_instance.vrp] [num_runs]
```

**Contoh**:

```bash
python ortools_solver.py 1_FaridFajar.vrp 3
```

Di dalam kode:

```python
TIME_LIMIT_PER_RUN = 10.0  # detik per run
```

Solver dipanggil dengan:

```python
solve_with_ortools(num_vehicles=1, time_limit_sec=int(TIME_LIMIT_PER_RUN))
```

Jika ingin mengubah jumlah kendaraan (`num_vehicles`) atau time limit, edit langsung di `ortools_solver.py`.

---

### 5. Menjalankan Benchmark Otomatis (Semua Algoritma)

```bash
python benchmark_all.py
```

Skrip ini akan:

1. Meload daftar instance dari `INSTANCE_FILES` di `benchmark_all.py`:

   ```python
   INSTANCE_FILES = [
       "1_FaridFajar.vrp",
       "2_WahyuDwi.vrp",
       "3_ChabibMaulana.vrp",
       "4_MochAlfian.vrp",
   ]
   ```

2. Untuk setiap instance, menjalankan:

   - `greedy_vrp.py`
   - `ga_vrp.py`
   - `tabu_vrp.py`
   - `ortools_solver.py`

3. Mengambil baris ringkasan dari setiap skrip:

   - `GREEDY_SUMMARY|...`
   - `GA_SUMMARY|...`
   - `TABU_SUMMARY|...`
   - `ORTOOLS_SUMMARY|...`

4. Menggabungkan semuanya ke file `benchmark_summary.csv` dengan kolom:
   ```
   instance_file|algorithm|best_cost|avg_cost|worst_cost|num_runs|best_run|num_routes|capacity|total_demand|best_route|total_time_sec|avg_time_sec
   ```

## Output & Format Ringkasan

### 1. Genetic Algorithm (`ga_vrp.py`)

Menampilkan:

- Progress setiap beberapa generasi (mis. `log_every = 50`)
- Analisis rute (demand per rute, cost per rute)
- Satu baris ringkasan:

```
GA_SUMMARY|instance_file|best_cost|avg_cost|worst_cost|num_runs|best_run|best_seed|num_routes|num_nodes|num_customers|capacity|total_demand|best_route|chromosome|total_time_sec|avg_time_per_run_sec
```

Menyimpan:

- CSV `<basename>_ga_summary.csv` dengan header:
  ```
  instance_file,best_cost,avg_cost,worst_cost,num_runs,best_run,best_seed,num_routes,num_nodes,num_customers,capacity,total_demand,best_route,chromosome,total_time_sec,avg_time_per_run_sec
  ```
- Plot rute terbaik ke `<basename>_ga_route.png`

---

### 2. Tabu Search (`tabu_vrp.py`)

Menampilkan:

- Log setiap beberapa iterasi (mis. `log_every = 50`)
- Analisis rute detail
- Satu baris ringkasan:

```
TABU_SUMMARY|instance_file|best_cost|avg_cost|worst_cost|num_runs|best_run|best_seed|num_routes|num_nodes|num_customers|capacity|total_demand|best_route|chromosome|total_time_sec|avg_time_per_run_sec
```

Menyimpan:

- CSV `<basename>_tabu_summary.csv` dengan header yang sama dengan GA
- Plot rute terbaik ke `<basename>_tabu_route.png`

---

### 3. Greedy (`greedy_vrp.py`)

Output di terminal:

```
=== GREEDY SUMMARY ===
Total cost     : 21443.00
Num routes     : 3
Time (sec)     : 0.000123

GREEDY_SUMMARY|1_FaridFajar.vrp|21443.00|3|30.0|0-5-12-8-0/0-2-15-0/0-7-22-0|0.000123
```

Menyimpan:

- CSV `<basename>_greedy_summary.csv`:
  ```
  instance_file,cost,num_routes,capacity,route,time_sec
  1_FaridFajar.vrp,21443.00,3,30.0,0-5-12-8-0/0-2-15-0/0-7-22-0,0.000123
  ```
- Plot rute ke `<basename>_greedy_route.png`

---

### 4. OR-Tools (`ortools_solver.py`)

Output di terminal:

```
=== OR-TOOLS ANALYSIS ===
Instance file: 1_FaridFajar.vrp
Number of routes (vehicles): 1
Route 1: 0 -> 3 -> 9 -> 14 -> 0
  - Demand: 29.50 / Capacity: 30.0
  - Cost  : 4234.10
...
ORTOOLS_SUMMARY|1_FaridFajar.vrp|13892.40|13892.40|13892.40|3|2|1|45|44|30.00|118.20|0-3-9-14-0|0.3456|0.3210
```

Format ringkasan satu baris:

```
ORTOOLS_SUMMARY|instance_file|best_cost|avg_cost|worst_cost|num_runs|best_run|num_routes|num_nodes|num_customers|capacity|total_demand|route|best_solve_time_sec|avg_solve_time_sec
```

Menyimpan:

- CSV `<basename>_ortools_summary.csv`:
  ```
  instance_file,best_cost,avg_cost,worst_cost,num_runs,best_run,num_routes,num_nodes,num_customers,capacity,total_demand,route,best_solve_time_sec,avg_solve_time_sec
  ```
- Plot rute terbaik ke `<basename>_ortools_route.png`

## Struktur Folder

```
cvrp-solver/
├── parser.py           # Parser file .vrp
├── ga_vrp.py           # Genetic Algorithm CVRP
├── tabu_vrp.py         # Tabu Search CVRP
├── greedy_vrp.py       # Greedy Nearest Neighbor baseline
├── ortools_solver.py   # Solver OR-Tools
├── benchmark_all.py    # Jalankan semua algoritma & gabungkan hasil
├── requirements.txt    # Dependencies Python
├── README.md           # Dokumentasi
├── 1_FaridFajar.vrp    # Instance contoh 1
├── 2_WahyuDwi.vrp      # Instance contoh 2
├── 3_ChabibMaulana.vrp # Instance contoh 3
└── 4_MochAlfian.vrp    # Instance contoh 4
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

Visualisasi rute akan disimpan sebagai `1_FaridFajar_ga_route.png`

### Tabu Search

```
Iter 50: best = 16234.5
Iter 100: best = 15876.2
...
=== TABU SEARCH RESULT ===
Instance: 1_FaridFajar.vrp
Best fitness: 14891.3
Routes: 3 vehicles
Route 1: 0 -> 8 -> 12 -> 5 -> 0 (demand: 28.0/30.0, cost: 4234.5)
...
TABU_SUMMARY|1_FaridFajar.vrp|14891.30|15123.40|15890.20|5|2|3|45|44|30.00|120.50|0-8-12-5-0/0-2-15-0/0-7-22-0|8.1234|1.6247
```

Visualisasi rute akan disimpan sebagai `1_FaridFajar_tabu_route.png`

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

Visualisasi rute akan disimpan sebagai `1_FaridFajar_ortools_route.png`

### Greedy

```
=== GREEDY SUMMARY ===
Best cost : 21443.00
Best run index : 1
Avg cost : 21443.00
Worst cost : 21443.00
Avg time (sec) : 0.0001
```

Visualisasi rute akan disimpan sebagai `1_FaridFajar_greedy_route.png`

### Benchmark Summary

Setelah menjalankan `benchmark_all.py`, file `benchmark_summary.csv` akan berisi ringkasan semua algoritma:

```
instance_file,algorithm,best_cost,avg_cost,worst_cost,num_runs,best_run,num_routes,capacity,total_demand,best_route,total_time_sec,avg_time_sec
1_FaridFajar.vrp,GA,14234.80,15234.50,16543.20,5,3,3,30.0,120.50,0-5-12-8-0/0-2-15-0/0-7-22-0,12.3456,2.4691
1_FaridFajar.vrp,Greedy,21443.00,21443.00,21443.00,5,1,1,30.0,120.50,0-37-43-19-44-...-0,0.0005,0.0001
1_FaridFajar.vrp,Tabu,14891.30,15123.40,15890.20,5,2,3,30.0,120.50,0-8-12-5-0/0-2-15-0/0-7-22-0,8.1234,1.6247
1_FaridFajar.vrp,OR-Tools,13892.40,13892.40,13892.40,1,1,3,30.0,118.20,0-3-9-14-0/0-1-6-11-0/0-4-13-0,0.3456,0.3456
```

## Algoritma Singkat

### Genetic Algorithm

1. **Representasi**: Permutasi pelanggan.
2. **Decoding**: `decode_routes` → beberapa rute dengan batas kapasitas.
3. **Fitness**: Total cost + penalti overload.
4. **Operator**: Tournament selection, OX crossover, swap mutation.
5. **Intensifikasi**: 2-opt (opsional, probabilistik).

### Greedy (Nearest Neighbor)

1. Mulai dari depot, pilih customer terdekat yang masih muat kapasitas.
2. Jika tidak ada yang muat, kembali ke depot dan mulai rute baru.
3. Ulang sampai semua customer terlayani.

### Tabu Search

1. **Representasi**: Permutasi pelanggan.
2. **Neighborhood**: Semua solusi dari swap dua posisi pelanggan.
3. **Tabu list**: Menyimpan move yang baru digunakan untuk beberapa iterasi.
4. **Aspiration**: Move tabu boleh dipakai jika memberi solusi global terbaik.
5. **Stop**: `max_iters`, `max_no_improve`, atau time limit.

### OR-Tools

- Gunakan `RoutingIndexManager` dan `RoutingModel`.
- Definisikan distance callback dan demand callback.
- Tambahkan kapasitas kendaraan via `AddDimensionWithVehicleCapacity`.
- Set strategi:
  - **First solution**: `PATH_CHEAPEST_ARC`
  - **Local search metaheuristic**: `GUIDED_LOCAL_SEARCH`
- Set time limit per run dan solve.

## Benchmarking

Untuk membandingkan performa empat metode (Greedy, GA, Tabu, dan OR-Tools), kamu bisa:

1. **Menjalankan keempat skrip secara manual**, atau
2. **Menggunakan skrip otomatis `benchmark_all.py`** yang akan:
   - Menjalankan Greedy, GA, Tabu, dan OR-Tools untuk semua instance yang didefinisikan di `INSTANCE_FILES`.
   - Menggabungkan semua ringkasan (`*_SUMMARY|...`) menjadi satu file `benchmark_summary.csv` dengan kolom:
     ```
     instance_file|algorithm|best_cost|avg_cost|worst_cost|num_runs|best_run|num_routes|capacity|total_demand|best_route|total_time_sec|avg_time_sec
     ```

## Referensi

- OR-Tools Documentation: https://developers.google.com/optimization
- CVRP Benchmark Instances: http://vrp.atd-lab.inf.puc-rio.br/index.php/en/
- Genetic Algorithm for VRP: Literatur akademik terkait
