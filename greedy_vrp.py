import sys
import csv
import os
import time
import math
from typing import List

import matplotlib.pyplot as plt
from parser import load_cvrp_instance

# ---------------------------------------------------------
# Instance file dari CLI
# ---------------------------------------------------------
INSTANCE_FILE = sys.argv[1] if len(sys.argv) > 1 else "output_cvrp.vrp"
NUM_RUNS = int(sys.argv[2]) if len(sys.argv) > 2 else 5

# ---------------------------------------------------------
# Load instance
# ---------------------------------------------------------
N, CAPACITY, DIST, DEMAND = load_cvrp_instance(INSTANCE_FILE)
DEPOT = 0


# ---------------------------------------------------------
# Baseline: Greedy Nearest Neighbor CVRP
# ---------------------------------------------------------
def greedy_vrp():
    unvisited = set(range(1, N))
    routes = []
    total_cost = 0.0

    while unvisited:
        route = [DEPOT]
        load = 0.0
        current = DEPOT

        while True:
            # cari customer terdekat yang tidak melanggar kapasitas
            nearest = None
            best_dist = float("inf")

            for cust in unvisited:
                if load + DEMAND[cust] > CAPACITY:
                    continue
                d = DIST[current][cust]
                if d < best_dist:
                    best_dist = d
                    nearest = cust

            if nearest is None:
                break  # harus kembali ke depot

            # kunjungi customer
            route.append(nearest)
            load += DEMAND[nearest]
            unvisited.remove(nearest)
            current = nearest

        # kembali ke depot
        route.append(DEPOT)
        routes.append(route)

        # hitung cost route ini
        route_cost = 0
        for i in range(len(route) - 1):
            route_cost += DIST[route[i]][route[i+1]]
        total_cost += route_cost

    return {"routes": routes, "cost": total_cost}


# ---------------------------------------------------------
# Visualisasi route (lingkaran)
# ---------------------------------------------------------
def plot_routes(routes: List[List[int]], filename: str, title: str):
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
        rx = [xs[n] for n in r]
        ry = [ys[n] for n in r]
        plt.plot(rx, ry, marker="o")

    plt.title(title)
    plt.axis("equal")
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()
    print(f"[Greedy] Route plot saved to {filename}")


# ---------------------------------------------------------
# Multi-run baseline greedy
# ---------------------------------------------------------
def multi_run_greedy(num_runs: int):
    best = None
    best_run_idx = None
    costs = []
    times = []

    for r in range(num_runs):
        print(f"\n=== GREEDY RUN {r+1}/{num_runs} ===")
        start = time.perf_counter()
        result = greedy_vrp()
        end = time.perf_counter()

        cost = result["cost"]
        elapsed = end - start

        print(f"Run {r+1}: cost={cost}, time={elapsed:.4f}s")

        costs.append(cost)
        times.append(elapsed)

        if best is None or cost < best["cost"]:
            best = {"routes": result["routes"], "cost": cost, "time": elapsed}
            best_run_idx = r + 1

    return best, costs, times, best_run_idx


# ---------------------------------------------------------
# Main Execution
# ---------------------------------------------------------
if __name__ == "__main__":
    print(f"Using instance file: {INSTANCE_FILE}")
    print(f"Number of Greedy runs: {NUM_RUNS}")

    best, costs, times, best_run_idx = multi_run_greedy(NUM_RUNS)

    best_cost = best["cost"]
    best_time = best["time"]
    avg_cost = sum(costs) / len(costs)
    worst_cost = max(costs)
    avg_time = sum(times) / len(times)

    print("\n=== GREEDY SUMMARY ===")
    print(f"Best cost      : {best_cost}")
    print(f"Best run index : {best_run_idx}")
    print(f"Avg cost       : {avg_cost}")
    print(f"Worst cost     : {worst_cost}")
    print(f"Avg time (sec) : {avg_time:.4f}")

    # simpan CSV summary
    base_name = os.path.splitext(os.path.basename(INSTANCE_FILE))[0]
    summary_file = f"{base_name}_greedy_summary.csv"
    file_exists = os.path.exists(summary_file)

    header = [
        "instance_file",
        "best_cost",
        "avg_cost",
        "worst_cost",
        "num_runs",
        "best_run",
        "num_routes",
        "capacity",
        "best_route",
        "best_time_sec",
        "avg_time_sec",
    ]

    best_routes = best["routes"]
    route_strings = ["-".join(str(n) for n in r) for r in best_routes]
    final_route_str = "/".join(route_strings)

    row = [
        INSTANCE_FILE,
        f"{best_cost:.2f}",
        f"{avg_cost:.2f}",
        f"{worst_cost:.2f}",
        str(NUM_RUNS),
        str(best_run_idx),
        str(len(best_routes)),
        str(CAPACITY),
        final_route_str,
        f"{best_time:.4f}",
        f"{avg_time:.4f}",
    ]

    with open(summary_file, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(header)
        writer.writerow(row)

    # simpan plot
    plot_routes(best_routes, f"{base_name}_greedy_route.png",
                f"Greedy Best Route - {INSTANCE_FILE}")
