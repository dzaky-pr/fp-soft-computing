from typing import List
import sys

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

    result = solve_with_ortools(num_vehicles=1, time_limit_sec=30)

    if result is None:
        exit(0)

    routes = result["routes"]
    total_distance = result["total_distance"]

    print("\n=== OR-TOOLS RESULT ===")
    print("Instance:", INSTANCE_FILE)
    print("Objective (total distance):", total_distance)

    stats = analyze_routes(routes)

    # ---------- RINGKASAN SATU BARIS (ORTOOLS_SUMMARY) ----------
    num_routes = len(routes)
    num_nodes = N
    num_customers = N - 1
    total_demand = stats["total_demand"]

    route_strings = ["-".join(str(node) for node in r) for r in routes]
    route_str = "/".join(route_strings)

    print("\nORTOOLS_SUMMARY|"
          f"{INSTANCE_FILE}|"
          f"{total_distance}|"
          f"{num_routes}|"
          f"{num_nodes}|"
          f"{num_customers}|"
          f"{CAPACITY}|"
          f"{total_demand:.2f}|"
          f"{route_str}")
