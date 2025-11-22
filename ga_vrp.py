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
    """
    routes = decode_routes(chromosome)
    base_cost = solution_cost(routes)

    overload = 0.0
    for r in routes:
        load = sum(DEMAND[node] for node in r)
        if load > CAPACITY:
            overload += (load - CAPACITY)

    return base_cost + penalty_factor * overload


# --------------------------------------------------------------------
# Inisialisasi populasi
# --------------------------------------------------------------------
def random_chromosome() -> List[int]:
    chrom = CUSTOMERS[:]
    random.shuffle(chrom)
    return chrom


def make_individual() -> Dict[str, Any]:
    chrom = random_chromosome()
    return {
        "chrom": chrom,
        "fitness": fitness(chrom)
    }


def init_population(pop_size: int):
    return [make_individual() for _ in range(pop_size)]


# --------------------------------------------------------------------
# Selection, Crossover, Mutation
# --------------------------------------------------------------------
def tournament_selection(population, k: int = 3):
    """
    Ambil k individu random, pilih yang fitness-nya paling kecil (lebih baik).
    """
    best = None
    for _ in range(k):
        ind = random.choice(population)
        if best is None or ind["fitness"] < best["fitness"]:
            best = ind
    return best


def ox_crossover(p1: List[int], p2: List[int]) -> List[int]:
    """
    Order Crossover (OX) untuk permutasi.
    p1, p2: kromosom (list customer)
    return: child (juga permutasi valid)
    """
    n = len(p1)
    a, b = sorted(random.sample(range(n), 2))

    child: List[int] = [None] * n  # type: ignore

    # copy segmen dari parent 1
    child[a:b + 1] = p1[a:b + 1]

    # isi posisi lain dengan urutan gen dari parent 2
    pos = (b + 1) % n
    for gene in p2:
        if gene not in child:
            child[pos] = gene
            pos = (pos + 1) % n

    return child  # type: ignore


def mutate_swap(chromosome: List[int], mutation_prob: float = 0.2) -> List[int]:
    chrom = chromosome[:]
    if random.random() < mutation_prob:
        i, j = random.sample(range(len(chrom)), 2)
        chrom[i], chrom[j] = chrom[j], chrom[i]
    return chrom


# --------------------------------------------------------------------
# Local search 2-opt (opsional, untuk intensifikasi)
# --------------------------------------------------------------------
def two_opt(chromosome: List[int]) -> List[int]:
    """
    2-opt di level kromosom (anggap semua customer dalam satu tour besar).
    decode_routes + fitness akan tetap memastikan kapasitas terjaga.
    """
    best = chromosome[:]
    best_cost = fitness(best)
    improved = True

    while improved:
        improved = False
        for i in range(len(best) - 1):
            for j in range(i + 1, len(best)):
                new = best[:]
                new[i:j + 1] = reversed(new[i:j + 1])
                new_cost = fitness(new)
                if new_cost < best_cost:
                    best = new
                    best_cost = new_cost
                    improved = True

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
    print(f"[GA] Route plot saved to {filename}")


# --------------------------------------------------------------------
# Genetic Algorithm utama
# --------------------------------------------------------------------
def genetic_algorithm(
    generations: int = 300,
    pop_size: int = 150,
    cx_prob: float = 0.8,
    mut_prob: float = 0.2,
    elitism: int = 1,
    use_two_opt: bool = True,
    two_opt_prob: float = 0.3,
    log_every: int = 50,
):
    """
    Jalankan GA untuk instance CVRP/TSP dari file .vrp.
    """
    population = init_population(pop_size)
    best = min(population, key=lambda ind: ind["fitness"])

    for gen in range(generations):
        new_population = []

        # Elitism: copy beberapa individu terbaik langsung ke generasi baru
        elites = sorted(population, key=lambda ind: ind["fitness"])[:elitism]
        for e in elites:
            new_population.append({"chrom": e["chrom"][:], "fitness": e["fitness"]})

        # Buat individu baru sampai populasi penuh
        while len(new_population) < pop_size:
            parent1 = tournament_selection(population)

            # Crossover
            if random.random() < cx_prob:
                parent2 = tournament_selection(population)
                child_chrom = ox_crossover(parent1["chrom"], parent2["chrom"])
            else:
                child_chrom = parent1["chrom"][:]

            # Mutasi
            child_chrom = mutate_swap(child_chrom, mut_prob)

            # Optional: local search 2-opt
            if use_two_opt and random.random() < two_opt_prob:
                child_chrom = two_opt(child_chrom)

            new_population.append({
                "chrom": child_chrom,
                "fitness": fitness(child_chrom)
            })

        population = new_population

        # Update best global
        current_best = min(population, key=lambda ind: ind["fitness"])
        if current_best["fitness"] < best["fitness"]:
            best = {
                "chrom": current_best["chrom"][:],
                "fitness": current_best["fitness"]
            }

        # Log setiap beberapa generasi
        if log_every and (gen + 1) % log_every == 0:
            print(f"Gen {gen+1}: best fitness = {best['fitness']}")

    return best


# --------------------------------------------------------------------
# Analisis solusi (buat laporan)
# --------------------------------------------------------------------
def analyze_solution(chromosome: List[int]):
    routes = decode_routes(chromosome)
    print("\n=== ANALYSIS ===")
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
# Multi-run untuk statistik GA
# --------------------------------------------------------------------
def multi_run(num_runs: int = 10, **ga_kwargs):
    """
    Jalankan GA berkali-kali (dengan seed berbeda) untuk lihat:
    - best fitness per run
    - best overall
    """
    best_overall = None
    fitnesses = []

    for r in range(num_runs):
        seed = 100 + r
        random.seed(seed)
        print(f"\n=== RUN {r+1}/{num_runs} (seed={seed}) ===")
        best = genetic_algorithm(**ga_kwargs)
        fitnesses.append(best["fitness"])

        if best_overall is None or best["fitness"] < best_overall["fitness"]:
            best_overall = {
                "chrom": best["chrom"][:],
                "fitness": best["fitness"],
                "seed": seed,
                "run": r + 1,
            }

    print("\n=== SUMMARY ===")
    print("Instance:", INSTANCE_FILE)
    print("Best fitness per run:", fitnesses)
    print(
        f"Best overall: {best_overall['fitness']} "
        f"(run {best_overall['run']}, seed={best_overall['seed']})"
    )

    return best_overall, fitnesses


# --------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------
if __name__ == "__main__":
    print(f"Using instance file: {INSTANCE_FILE}")

    # --- berapa kali mau di-run (num_runs) dari CLI ---
    # Contoh: python ga_vrp.py 1_FaridFajar.vrp 10
    NUM_RUNS = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    print(f"Number of GA runs: {NUM_RUNS}")

    # --- ukur waktu eksekusi multi_run ---
    start_time = time.perf_counter()

    best_overall, fitnesses = multi_run(
        num_runs=NUM_RUNS,
        generations=300,
        pop_size=150,
        cx_prob=0.8,
        mut_prob=0.2,
        elitism=1,
        use_two_opt=True,
        two_opt_prob=0.3,
        log_every=50,
    )

    end_time = time.perf_counter()
    total_time_sec = end_time - start_time
    avg_time_per_run_sec = total_time_sec / NUM_RUNS

    print(f"\nTotal execution time (multi_run): {total_time_sec:.4f} s")
    print(f"Average time per run            : {avg_time_per_run_sec:.4f} s")

    print("\n=== BEST OVERALL SOLUTION ===")
    print("Instance:", INSTANCE_FILE)
    print("Best fitness:", best_overall["fitness"])
    print("Chromosome (customer order):")
    print(best_overall["chrom"])

    stats = analyze_solution(best_overall["chrom"])

    # ---------- RINGKASAN SATU BARIS (GA_SUMMARY) ----------
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
        "GA_SUMMARY|"
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

    # ---------- SIMPAN KE FILE <basename>_ga_summary.csv ----------
    base_name = os.path.splitext(os.path.basename(INSTANCE_FILE))[0]
    summary_file = f"{base_name}_ga_summary.csv"
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
    plot_filename = f"{base_name}_ga_route.png"
    plot_routes(routes, f"GA Best Route - {INSTANCE_FILE}", plot_filename)
