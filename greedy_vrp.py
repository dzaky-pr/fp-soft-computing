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

# ---------------------------------------------------------
# Load instance
# ---------------------------------------------------------
N, CAPACITY, DIST, DEMAND = load_cvrp_instance(INSTANCE_FILE)
DEPOT = 0


# ---------------------------------------------------------
# Baseline: Greedy Nearest Neighbor CVRP
# ---------------------------------------------------------
def greedy_vrp():
    """
    Konstruksi solusi CVRP dengan greedy nearest neighbor + capacity check.
    Return:
      - routes: list of routes (list of node visit including depot)
      - cost  : total distance of all routes
    """
    unvisited = set(range(1, N))
    routes = []
    total_cost = 0.0

    while unvisited:
        route = [DEPOT]
        load = 0.0
        current = DEPOT

        while True:
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
                break

            route.append(nearest)
            load += DEMAND[nearest]
            unvisited.remove(nearest)
            current = nearest

        # kembali ke depot
        route.append(DEPOT)
        routes.append(route)

        # hitung cost route ini
        route_cost = 0.0
        for i in range(len(route) - 1):
            route_cost += DIST[route[i]][route[i+1]]
        total_cost += route_cost

    return {"routes": routes, "cost": total_cost}


# ---------------------------------------------------------
# Visualisasi route (layout lingkaran)
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
# Main Execution
# ---------------------------------------------------------
if __name__ == "__main__":
    print(f"Using instance file: {INSTANCE_FILE}")

    # --- run greedy once (deterministic) ---
    start = time.perf_counter()
    result = greedy_vrp()
    end = time.perf_counter()
    elapsed = end - start

    routes = result["routes"]
    total_cost = result["cost"]

    print("\n=== GREEDY SUMMARY ===")
    print(f"Total cost     : {total_cost:.2f}")
    print(f"Num routes     : {len(routes)}")
    print(f"Time (sec)     : {elapsed:.6f}")

        # ---------- RINGKASAN SATU BARIS (GREEDY_SUMMARY) ----------
    route_strings = ["-".join(str(n) for n in r) for r in routes]
    final_route_str = "/".join(route_strings)

    line_text = (
        "GREEDY_SUMMARY|"
        f"{INSTANCE_FILE}|"
        f"{total_cost:.2f}|"
        f"{len(routes)}|"
        f"{CAPACITY}|"
        f"{final_route_str}|"
        f"{elapsed:.6f}"
    )

    print("\n" + line_text)


    # ---------------------------------------------------------
    # SIMPAN CSV SUMMARY
    # ---------------------------------------------------------
    base_name = os.path.splitext(os.path.basename(INSTANCE_FILE))[0]
    summary_file = f"{base_name}_greedy_summary.csv"
    file_exists = os.path.exists(summary_file)

    header = [
        "instance_file",
        "cost",
        "num_routes",
        "capacity",
        "route",
        "time_sec",
    ]

    route_strings = ["-".join(str(n) for n in r) for r in routes]
    final_route_str = "/".join(route_strings)

    row = [
        INSTANCE_FILE,
        f"{total_cost:.2f}",
        str(len(routes)),
        str(CAPACITY),
        final_route_str,
        f"{elapsed:.6f}",
    ]

    with open(summary_file, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(header)
        writer.writerow(row)

    # ---------------------------------------------------------
    # SIMPAN PLOT RUTE
    # ---------------------------------------------------------
    plot_filename = f"{base_name}_greedy_route.png"
    plot_routes(routes, plot_filename, f"Greedy Route - {INSTANCE_FILE}")
