import random
import sys
import csv
import os
import time
import math
import matplotlib.pyplot as plt
from typing import List, Optional
from parser import load_cvrp_instance

# --------------------------------------------------------------------
# Konfigurasi & Load Instance
# --------------------------------------------------------------------
INSTANCE_FILE = sys.argv[1] if len(sys.argv) > 1 else "output_cvrp.vrp"
N, CAPACITY, DIST, DEMAND = load_cvrp_instance(INSTANCE_FILE)
DEPOT = 0
CUSTOMERS = list(range(1, N))

# --------------------------------------------------------------------
# Fungsi Helper (Sama dengan algoritma lain)
# --------------------------------------------------------------------
def decode_routes(chromosome: List[int]) -> List[List[int]]:
    routes = []
    route = [DEPOT]
    load = 0.0

    for cust in chromosome:
        demand = DEMAND[cust]
        if load + demand > CAPACITY and route != [DEPOT]:
            route.append(DEPOT)
            routes.append(route)
            route = [DEPOT, cust]
            load = demand
        else:
            route.append(cust)
            load += demand
    route.append(DEPOT)
    routes.append(route)
    return routes

def route_cost(route: List[int]) -> float:
    cost = 0.0
    for i in range(len(route) - 1):
        cost += DIST[route[i]][route[i + 1]]
    return cost

def solution_cost(routes: List[List[int]]) -> float:
    return sum(route_cost(r) for r in routes)

def fitness(chromosome: List[int], penalty_factor: float = 1000.0) -> float:
    routes = decode_routes(chromosome)
    base_cost = solution_cost(routes)
    
    overload = 0.0
    for r in routes:
        load = sum(DEMAND[n] for n in r)
        if load > CAPACITY:
            overload += (load - CAPACITY)
            
    return base_cost + penalty_factor * overload

def random_chromosome() -> List[int]:
    chrom = CUSTOMERS[:]
    random.shuffle(chrom)
    return chrom

def plot_routes(routes: List[List[int]], title: str, filename: str):
    xs, ys = [], []
    for i in range(N):
        angle = 2 * math.pi * i / N
        xs.append(math.cos(angle))
        ys.append(math.sin(angle))

    plt.figure(figsize=(6, 6))
    plt.scatter(xs, ys)
    for i, (x, y) in enumerate(zip(xs, ys)):
        plt.text(x, y, str(i), fontsize=8, ha="center", va="center")
    for r in routes:
        rx = [xs[node] for node in r]
        ry = [ys[node] for node in r]
        plt.plot(rx, ry, marker="o")

    plt.title(title)
    plt.axis("equal")
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()

# --------------------------------------------------------------------
# Algoritma Utama: Simulated Annealing
# --------------------------------------------------------------------
def simulated_annealing(
    initial_temp: float = 1000.0,
    cooling_rate: float = 0.995,
    stop_temp: float = 0.1,
    time_limit_sec: Optional[float] = None
):
    start_time = time.perf_counter()
    
    # 1. Inisialisasi Solusi Awal
    current_sol = random_chromosome()
    current_cost = fitness(current_sol)
    
    best_sol = current_sol[:]
    best_cost = current_cost
    
    temp = initial_temp
    iter_count = 0
    
    # Loop sampai suhu dingin atau waktu habis
    while temp > stop_temp:
        iter_count += 1
        if time_limit_sec and (time.perf_counter() - start_time) > time_limit_sec:
            break
            
        # 2. Buat Neighbor (Tukar posisi 2 customer secara acak / SWAP)
        neighbor = current_sol[:]
        i, j = random.sample(range(len(neighbor)), 2)
        neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
        
        neighbor_cost = fitness(neighbor)
        
        # 3. Hitung Delta (Selisih cost)
        delta = neighbor_cost - current_cost
        
        # 4. Terima atau Tolak?
        # Jika delta < 0 (lebih bagus), PASTI terima.
        # Jika delta > 0 (lebih jelek), terima dengan peluang probabilitas.
        if delta < 0 or random.random() < math.exp(-delta / temp):
            current_sol = neighbor
            current_cost = neighbor_cost
            
            # Update Global Best jika ketemu solusi rekor baru
            if current_cost < best_cost:
                best_cost = current_cost
                best_sol = current_sol[:]
        
        # 5. Turunkan Suhu (Cooling)
        temp *= cooling_rate
        
    return {"chrom": best_sol, "fitness": best_cost, "iters": iter_count}

# --------------------------------------------------------------------
# Main Execution (Untuk dijalankan via terminal / benchmark)
# --------------------------------------------------------------------
if __name__ == "__main__":
    # Ambil parameter jumlah run dari command line
    NUM_RUNS = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    TIME_LIMIT = 10.0 # Detik per run (biar adil dengan algo lain)
    
    print(f"Running SA on {INSTANCE_FILE} for {NUM_RUNS} runs...")
    
    best_overall = None
    fitnesses = []
    
    start_total = time.perf_counter()
    
    for r in range(NUM_RUNS):
        seed = 300 + r
        random.seed(seed) # Set seed biar reproducible
        
        # Jalankan algoritma
        res = simulated_annealing(time_limit_sec=TIME_LIMIT)
        fitnesses.append(res["fitness"])
        
        # Simpan yang terbaik dari semua run
        if best_overall is None or res["fitness"] < best_overall["fitness"]:
            best_overall = {
                "chrom": res["chrom"],
                "fitness": res["fitness"],
                "run": r + 1,
                "seed": seed
            }
            
    end_total = time.perf_counter()
    total_time = end_total - start_total
    
    # --- Output Summary ---
    routes = decode_routes(best_overall["chrom"])
    route_str = "/".join(["-".join(map(str, r)) for r in routes])
    chrom_str = "-".join(map(str, best_overall["chrom"]))
    
    avg_cost = sum(fitnesses) / len(fitnesses)
    worst_cost = max(fitnesses)
    
    # Format output satu baris untuk ditangkap benchmark_all.py
    # Format: SA_SUMMARY|file|best|avg|worst|runs|best_run|seed|n_routes|n_nodes|n_cust|cap|total_dem|route|chrom|total_time|avg_time
    summary_line = (
        f"SA_SUMMARY|{INSTANCE_FILE}|{best_overall['fitness']:.2f}|"
        f"{avg_cost:.2f}|{worst_cost:.2f}|{NUM_RUNS}|"
        f"{best_overall['run']}|{best_overall['seed']}|{len(routes)}|{N}|{N-1}|"
        f"{CAPACITY}|{sum(DEMAND):.2f}|{route_str}|{chrom_str}|"
        f"{total_time:.4f}|{total_time/NUM_RUNS:.4f}"
    )
    print("\n" + summary_line)
    
    # Simpan ke CSV khusus SA
    base_name = os.path.splitext(os.path.basename(INSTANCE_FILE))[0]
    with open(f"{base_name}_sa_summary.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(summary_line.split("|"))
        
    # Simpan Gambar Rute
    plot_routes(routes, f"SA Best Route - {INSTANCE_FILE}", f"{base_name}_sa_route.png")