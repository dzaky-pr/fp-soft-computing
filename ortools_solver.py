from typing import List
import sys
import csv
import os
import time
import math

import matplotlib.pyplot as plt

from ortools.constraint_solver import routing_enums_pb2, pywrapcp
from parser import load_cvrp_instance

# ---------------------------------------------------------
# Pilih instance dari argumen CLI
# ---------------------------------------------------------
INSTANCE_FILE = sys.argv[1] if len(sys.argv) > 1 else "output_cvrp.vrp"

# ---------------------------------------------------------
# Load instance dari file .vrp
# ---------------------------------------------------------
N, CAPACITY, DIST, DEMAND = load_cvrp_instance(INSTANCE_FILE)
DEPOT = 0

# OR-Tools butuh demand integer → kita scale
DEMAND_SCALE = 100  # 1 unit = 0.01 di data asli
DEMAND_INT = [int(round(d * DEMAND_SCALE)) for d in DEMAND]
CAPACITY_INT = int(round(CAPACITY * DEMAND_SCALE))


# ---------------------------------------------------------
# Visualisasi rute (layout lingkaran sederhana)
# ---------------------------------------------------------
def plot_routes(routes: List[List[int]], title: str, filename: str):
    xs = []
    ys = []
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
    print(f"[OR-Tools] Route plot saved to {filename}")


# ---------------------------------------------------------
# Helper: solve CVRP/TSP dengan OR-Tools Routing
# ---------------------------------------------------------
def solve_with_ortools(num_vehicles: int = 1, time_limit_sec: int = 30):
    # Manager: mapping index internal ↔ node (0..N-1)
    manager = pywrapcp.RoutingIndexManager(N, num_vehicles, DEPOT)
    routing = pywrapcp.RoutingModel(manager)

    # ---- Distance callback ----
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return int(DIST[from_node][to_node])

    transit_cb_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_cb_index)

    # ---- Demand / Capacity dimension ----
    def demand_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        return DEMAND_INT[from_node]

    demand_cb_index = routing.RegisterUnaryTransitCallback(demand_callback)

    routing.AddDimensionWithVehicleCapacity(
        demand_cb_index,
        0,
        [CAPACITY_INT] * num_vehicles,
        True,
        "Capacity",
    )

    # ---- Search parameters ----
    search_params = pywrapcp.DefaultRoutingSearchParameters()
    search_params.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_params.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_params.time_limit.FromSeconds(time_limit_sec)

    # ---- Solve ----
    solution = routing.SolveWithParameters(search_params)

    if not solution:
        print("No solution found by OR-Tools.")
        return None

    # ---- Ekstrak rute ----
    routes: List[List[int]] = []
    total_distance = 0

    for vehicle_id in range(num_vehicles):
        index = routing.Start(vehicle_id)
        if routing.IsEnd(solution.Value(routing.NextVar(index))):
            continue

        route: List[int] = []
        route_distance = 0
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            route.append(node)
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id
            )
        route.append(manager.IndexToNode(index))

        routes.append(route)
        total_distance += route_distance

    return {
        "routes": routes,
        "total_distance": total_distance,
    }


# ---------------------------------------------------------
# Analisis hasil
# ---------------------------------------------------------
def analyze_routes(routes: List[List[int]]):
    print("\n=== OR-TOOLS ANALYSIS ===")
    print(f"Instance file: {INSTANCE_FILE}")
    print(f"Number of routes (vehicles): {len(routes)}")

    total_demand = 0.0
    total_cost = 0.0

    for idx, r in enumerate(routes, start=1):
        route_demand = sum(DEMAND[node] for node in r)
        route_cost = 0.0
        for i in range(len(r) - 1):
            route_cost += DIST[r[i]][r[i + 1]]

        total_demand += route_demand
        total_cost += route_cost

        print(f"\nRoute {idx}: {' -> '.join(map(str, r))}")
        print(f"  - Demand: {route_demand:.2f} / Capacity: {CAPACITY}")
        print(f"  - Cost  : {route_cost}")

    print(f"\nTotal demand all routes : {total_demand:.2f}")
    print(f"Total cost (sum routes): {total_cost}")

    return {
        "routes": routes,
        "total_demand": total_demand,
        "total_cost": total_cost,
    }


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------
if __name__ == "__main__":
    print(f"Using instance file: {INSTANCE_FILE}")

    # --- berapa kali mau di-run (num_runs) dari CLI ---
    # Contoh: python ortools_solver.py 1_FaridFajar.vrp 5
    NUM_RUNS = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    print(f"Number of OR-Tools runs: {NUM_RUNS}")

    costs = []
    times = []
    best_result = None
    best_run_idx = None

    for r in range(NUM_RUNS):
        print(f"\n=== OR-TOOLS RUN {r+1}/{NUM_RUNS} ===")
        start_time = time.perf_counter()
        result = solve_with_ortools(num_vehicles=1, time_limit_sec=30)
        end_time = time.perf_counter()
        solve_time_sec = end_time - start_time

        if result is None:
            print("No solution in this run.")
            continue

        total_distance = result["total_distance"]
        routes = result["routes"]

        print(f"Run {r+1}: objective = {total_distance}, time = {solve_time_sec:.4f} s")

        costs.append(total_distance)
        times.append(solve_time_sec)

        if best_result is None or total_distance < best_result["total_distance"]:
            best_result = {
                "routes": routes,
                "total_distance": total_distance,
                "solve_time": solve_time_sec,
            }
            best_run_idx = r + 1

    if best_result is None:
        print("No solution found in any run.")
        sys.exit(0)

    best_cost = best_result["total_distance"]
    avg_cost = sum(costs) / len(costs)
    worst_cost = max(costs)
    best_solve_time = best_result["solve_time"]
    avg_solve_time = sum(times) / len(times)

    print("\n=== OR-TOOLS BEST RUN ===")
    print(f"Instance: {INSTANCE_FILE}")
    print(f"Best cost      : {best_cost}")
    print(f"Best run index : {best_run_idx}")
    print(f"Best solve time: {best_solve_time:.4f} s")

    print("\n=== OR-TOOLS SUMMARY OVER RUNS ===")
    print(f"Costs per run : {costs}")
    print(f"Avg cost      : {avg_cost}")
    print(f"Worst cost    : {worst_cost}")
    print(f"Avg time (sec): {avg_solve_time:.4f}")

    # Analisis & visualisasi untuk rute terbaik saja
    stats = analyze_routes(best_result["routes"])

    # ---------- RINGKASAN SATU BARIS (ORTOOLS_SUMMARY) ----------
    num_routes = len(best_result["routes"])
    num_nodes = N
    num_customers = N - 1
    total_demand = stats["total_demand"]

    route_strings = ["-".join(str(node) for node in r) for r in best_result["routes"]]
    route_str = "/".join(route_strings)

    line_text = (
        "ORTOOLS_SUMMARY|"
        f"{INSTANCE_FILE}|"
        f"{best_cost}|"
        f"{avg_cost}|"
        f"{worst_cost}|"
        f"{NUM_RUNS}|"
        f"{best_run_idx}|"
        f"{num_routes}|"
        f"{num_nodes}|"
        f"{num_customers}|"
        f"{CAPACITY}|"
        f"{total_demand:.2f}|"
        f"{route_str}|"
        f"{best_solve_time:.4f}|"
        f"{avg_solve_time:.4f}"
    )

    print("\n" + line_text)

    # ---------- SIMPAN KE FILE <basename>_ortools_summary.csv ----------
    base_name = os.path.splitext(os.path.basename(INSTANCE_FILE))[0]
    summary_file = f"{base_name}_ortools_summary.csv"
    file_exists = os.path.exists(summary_file)

    header = [
        "instance_file",
        "best_cost",
        "avg_cost",
        "worst_cost",
        "num_runs",
        "best_run",
        "num_routes",
        "num_nodes",
        "num_customers",
        "capacity",
        "total_demand",
        "route",
        "best_solve_time_sec",
        "avg_solve_time_sec",
    ]

    row = [
        INSTANCE_FILE,
        str(best_cost),
        f"{avg_cost:.2f}",
        str(worst_cost),
        str(NUM_RUNS),
        str(best_run_idx),
        str(num_routes),
        str(num_nodes),
        str(num_customers),
        str(CAPACITY),
        f"{total_demand:.2f}",
        route_str,
        f"{best_solve_time:.4f}",
        f"{avg_solve_time:.4f}",
    ]

    with open(summary_file, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(header)
        writer.writerow(row)

    # ---------- PLOT RUTE TERBAIK ----------
    plot_filename = f"{base_name}_ortools_route.png"
    plot_routes(best_result["routes"], f"OR-Tools Best Route - {INSTANCE_FILE}", plot_filename)
