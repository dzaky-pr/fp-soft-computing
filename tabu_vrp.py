import random
import sys
import csv
import os
import time
import math
from typing import List, Dict, Any

import matplotlib.pyplot as plt

from parser import load_cvrp_instance

# --------------------------------------------------------------------
# Pilih instance file dari argumen CLI
# --------------------------------------------------------------------
INSTANCE_FILE = sys.argv[1] if len(sys.argv) > 1 else "output_cvrp.vrp"

# --------------------------------------------------------------------
# Load instance dari file .vrp
# --------------------------------------------------------------------
N, CAPACITY, DIST, DEMAND = load_cvrp_instance(INSTANCE_FILE)

DEPOT = 0
CUSTOMERS = list(range(1, N))  # node 1..N-1


# --------------------------------------------------------------------
# Representasi solusi & fungsi bantu
# --------------------------------------------------------------------
def decode_routes(chromosome: List[int]) -> List[List[int]]:
    """
    chromosome: permutasi customer [1..N-1] (index node, 0=depot)
    return: list of route, masing-masing route = [0, ..., 0]
    """
    routes: List[List[int]] = []
    route: List[int] = [DEPOT]
    load = 0.0

    for cust in chromosome:
        demand = DEMAND[cust]

        # kalau tambah cust melanggar kapasitas → tutup rute dan mulai baru
        if load + demand > CAPACITY and route != [DEPOT]:
            route.append(DEPOT)
            routes.append(route)
            route = [DEPOT, cust]
            load = demand
        else:
            route.append(cust)
            load += demand

    # tutup rute terakhir
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
    """
    Nilai fitness = total cost + penalti overload kapasitas (kalau ada).
    Decode routes akan sebisa mungkin menjaga kapasitas, tapi penalti disimpan
    untuk jaga-jaga jika ada overload.
    """
    routes = decode_routes(chromosome)
    base_cost = solution_cost(routes)

    overload = 0.0
    for r in routes:
        load = sum(DEMAND[node] for node in r)
        if load > CAPACITY:
            overload += (load - CAPACITY)

    return base_cost + penalty_factor * overload


def random_chromosome() -> List[int]:
    chrom = CUSTOMERS[:]
    random.shuffle(chrom)
    return chrom


# --------------------------------------------------------------------
# Tabu Search untuk CVRP (representasi: permutasi customer)
# --------------------------------------------------------------------
def tabu_search(
    max_iters: int = 500,
    tabu_tenure: int = 10,
    max_no_improve: int = 100,
    log_every: int = 50,
) -> Dict[str, Any]:
    """
    Tabu Search sederhana dengan neighborhood berbasis SWAP antar dua customer.
    - Representasi solusi: permutasi pelanggan [1..N-1]
    - Neighborhood: semua pasangan (i, j), i < j → swap posisi customer
    - Tabu list: pasangan customer (c1, c2) yang baru saja di-swap
    - Aspiration: move tabu boleh dipakai jika menghasilkan solusi global terbaik baru
    """

    current = random_chromosome()
    current_fitness = fitness(current)

    best = {
        "chrom": current[:],
        "fitness": current_fitness,
    }

    # key tabu: tuple(sorted(customer_i, customer_j)) → expire_iter
    tabu_list: Dict[tuple, int] = {}

    it = 0
    no_improve = 0

    while it < max_iters and no_improve < max_no_improve:
        it += 1

        best_candidate = None
        best_candidate_f = float("inf")
        best_candidate_move = None

        # generate semua neighbor via SWAP
        for i in range(len(current) - 1):
            for j in range(i + 1, len(current)):
                a = current[i]
                b = current[j]
                move_key = (min(a, b), max(a, b))

                neighbor = current[:]
                neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
                f = fitness(neighbor)

                # cek tabu + aspiration
                is_tabu = move_key in tabu_list and tabu_list[move_key] > it
                if is_tabu and f >= best["fitness"]:
                    # tabu dan tidak mengungguli solusi global terbaik
                    continue

                if f < best_candidate_f:
                    best_candidate_f = f
                    best_candidate = neighbor
                    best_candidate_move = move_key

        if best_candidate is None:
            # tidak ada neighbor yang dapat dipilih (jarang terjadi)
            print("[Tabu] Tidak menemukan neighbor yang valid, stop.")
            break

        # update current solution
        current = best_candidate
        current_fitness = best_candidate_f

        # update tabu list untuk move yang dipakai
        if best_candidate_move is not None:
            tabu_list[best_candidate_move] = it + tabu_tenure

        # bersihkan tabu yang sudah expired (opsional, untuk mencegah growth)
        expired_keys = [mv for mv, exp in tabu_list.items() if exp <= it]
        for k in expired_keys:
            del tabu_list[k]

        # update best global
        if current_fitness < best["fitness"]:
            best["chrom"] = current[:]
            best["fitness"] = current_fitness
            no_improve = 0
        else:
            no_improve += 1

        if log_every and it % log_every == 0:
            print(
                f"Iter {it}: current = {current_fitness:.2f}, "
                f"best = {best['fitness']:.2f}, "
                f"no_improve = {no_improve}"
            )

    print(
        f"[Tabu] Selesai di iter {it}, best fitness = {best['fitness']:.2f}, "
        f"no_improve = {no_improve}"
    )
    return best


# --------------------------------------------------------------------
# Visualisasi rute (layout lingkaran sederhana)
# --------------------------------------------------------------------
def plot_routes(routes: List[List[int]], title: str, filename: str):
    # letakkan node 0..N-1 di lingkaran
    xs = []
    ys = []
    for i in range(N):
        angle = 2 * math.pi * i / N
        xs.append(math.cos(angle))
        ys.append(math.sin(angle))

    plt.figure(figsize=(6, 6))
    # titik
    plt.scatter(xs, ys)

    # label node
    for i, (x, y) in enumerate(zip(xs, ys)):
        plt.text(x, y, str(i), fontsize=8, ha="center", va="center")

    # gambar rute
    for r in routes:
        rx = [xs[node] for node in r]
        ry = [ys[node] for node in r]
        plt.plot(rx, ry, marker="o")

    plt.title(title)
    plt.axis("equal")
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()
    print(f"[Tabu] Route plot saved to {filename}")


# --------------------------------------------------------------------
# Analisis solusi (buat laporan)
# --------------------------------------------------------------------
def analyze_solution(chromosome: List[int]):
    routes = decode_routes(chromosome)
    print("\n=== TABU ANALYSIS ===")
    print(f"Instance file: {INSTANCE_FILE}")
    print(f"Number of routes (vehicles): {len(routes)}")

    total_demand = 0.0
    for idx, r in enumerate(routes, start=1):
        route_demand = sum(DEMAND[node] for node in r)
        route_cost_value = route_cost(r)
        total_demand += route_demand

        print(f"\nRoute {idx}: {' -> '.join(map(str, r))}")
        print(f"  - Demand: {route_demand:.2f} / Capacity: {CAPACITY}")
        print(f"  - Cost  : {route_cost_value}")

    print(f"\nTotal demand all routes : {total_demand:.2f}")
    print(f"Total cost (sum routes): {solution_cost(routes)}")

    return {
        "routes": routes,
        "total_demand": total_demand,
        "total_cost": solution_cost(routes),
    }


# --------------------------------------------------------------------
# Multi-run untuk statistik Tabu Search
# --------------------------------------------------------------------
def multi_run_tabu(num_runs: int = 5, **ts_kwargs):
    """
    Jalankan Tabu Search berkali-kali (dengan seed berbeda) untuk lihat:
    - best fitness per run
    - best overall
    """
    best_overall = None
    fitnesses = []

    for r in range(num_runs):
        seed = 200 + r
        random.seed(seed)
        print(f"\n=== TABU RUN {r+1}/{num_runs} (seed={seed}) ===")
        best = tabu_search(**ts_kwargs)
        fitnesses.append(best["fitness"])

        if best_overall is None or best["fitness"] < best_overall["fitness"]:
            best_overall = {
                "chrom": best["chrom"][:],
                "fitness": best["fitness"],
                "seed": seed,
                "run": r + 1,
            }

    print("\n=== TABU SUMMARY (PER RUN) ===")
    print("Instance:", INSTANCE_FILE)
    print("Best fitness per run:", fitnesses)
    print(
        f"Best overall: {best_overall['fitness']:.2f} "
        f"(run {best_overall['run']}, seed={best_overall['seed']})"
    )

    return best_overall, fitnesses


# --------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------
if __name__ == "__main__":
    print(f"Using instance file: {INSTANCE_FILE}")

    # --- berapa kali mau di-run (num_runs) dari CLI ---
    # Contoh: python tabu_vrp.py 1_FaridFajar.vrp 5
    NUM_RUNS = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    print(f"Number of Tabu Search runs: {NUM_RUNS}")

    # --- ukur waktu eksekusi multi_run_tabu ---
    start_time = time.perf_counter()

    best_overall, fitnesses = multi_run_tabu(
        num_runs=NUM_RUNS,
        max_iters=500,
        tabu_tenure=10,
        max_no_improve=150,
        log_every=50,
    )

    end_time = time.perf_counter()
    total_time_sec = end_time - start_time
    avg_time_per_run_sec = total_time_sec / NUM_RUNS

    print(f"\nTotal execution time (multi_run_tabu): {total_time_sec:.4f} s")
    print(f"Average time per run                 : {avg_time_per_run_sec:.4f} s")

    print("\n=== TABU BEST OVERALL SOLUTION ===")
    print("Instance:", INSTANCE_FILE)
    print("Best fitness:", best_overall["fitness"])
    print("Chromosome (customer order):")
    print(best_overall["chrom"])

    stats = analyze_solution(best_overall["chrom"])

    # ---------- RINGKASAN SATU BARIS (TABU_SUMMARY) ----------
    best_cost = best_overall["fitness"]
    avg_cost = sum(fitnesses) / NUM_RUNS
    worst_cost = max(fitnesses)
    best_run = best_overall["run"]
    best_seed = best_overall["seed"]

    routes = stats["routes"]
    total_demand = stats["total_demand"]
    num_routes = len(routes)
    num_nodes = N
    num_customers = N - 1

    # route string (kalau >1 route, digabung dengan '/')
    route_strings = ["-".join(str(node) for node in r) for r in routes]
    best_route_str = "/".join(route_strings)

    chrom_str = "-".join(str(c) for c in best_overall["chrom"])

    line_text = (
        "TABU_SUMMARY|"
        f"{INSTANCE_FILE}|"
        f"{best_cost:.2f}|"
        f"{avg_cost:.2f}|"
        f"{worst_cost:.2f}|"
        f"{NUM_RUNS}|"
        f"{best_run}|"
        f"{best_seed}|"
        f"{num_routes}|"
        f"{num_nodes}|"
        f"{num_customers}|"
        f"{CAPACITY}|"
        f"{total_demand:.2f}|"
        f"{best_route_str}|"
        f"{chrom_str}|"
        f"{total_time_sec:.4f}|"
        f"{avg_time_per_run_sec:.4f}"
    )

    print("\n" + line_text)

    # ---------- SIMPAN KE FILE <basename>_tabu_summary.csv ----------
    base_name = os.path.splitext(os.path.basename(INSTANCE_FILE))[0]
    summary_file = f"{base_name}_tabu_summary.csv"
    file_exists = os.path.exists(summary_file)

    header = [
        "instance_file",
        "best_cost",
        "avg_cost",
        "worst_cost",
        "num_runs",
        "best_run",
        "best_seed",
        "num_routes",
        "num_nodes",
        "num_customers",
        "capacity",
        "total_demand",
        "best_route",
        "chromosome",
        "total_time_sec",
        "avg_time_per_run_sec",
    ]

    row = [
        INSTANCE_FILE,
        f"{best_cost:.2f}",
        f"{avg_cost:.2f}",
        f"{worst_cost:.2f}",
        str(NUM_RUNS),
        str(best_run),
        str(best_seed),
        str(num_routes),
        str(num_nodes),
        str(num_customers),
        str(CAPACITY),
        f"{total_demand:.2f}",
        best_route_str,
        chrom_str,
        f"{total_time_sec:.4f}",
        f"{avg_time_per_run_sec:.4f}",
    ]

    with open(summary_file, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(header)
        writer.writerow(row)

    # ---------- PLOT RUTE TERBAIK ----------
    plot_filename = f"{base_name}_tabu_route.png"
    plot_routes(routes, f"Tabu Search Best Route - {INSTANCE_FILE}", plot_filename)
