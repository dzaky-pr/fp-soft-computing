#!/usr/bin/env python3
"""
benchmark_all.py

Jalankan Greedy, GA, Tabu Search, OR-Tools, dan Simulated Annealing (SA)
untuk semua instance .vrp, lalu gabungkan hasilnya
ke dalam satu file CSV: benchmark_summary.csv
"""

import csv
import os
import subprocess
import sys

from parser import load_cvrp_instance

# ----------------------------------------------------------------------
# Konfigurasi eksperimen
# ----------------------------------------------------------------------
INSTANCE_FILES = [
    "1_FaridFajar.vrp",
    "2_WahyuDwi.vrp",
    "3_ChabibMaulana.vrp",
    "4_MochAlfian.vrp",
]

GA_RUNS = 5          # jumlah run GA per instance
TABU_RUNS = 5        # jumlah run Tabu per instance
ORTOOLS_RUNS = 1     # OR-Tools deterministik → cukup 1
SA_RUNS = 5          # jumlah run Simulated Annealing per instance

# ----------------------------------------------------------------------
# Helper untuk menjalankan command dan menangkap stdout
# ----------------------------------------------------------------------
def run_and_capture(cmd):
    print("\n" + "=" * 80)
    print("Running:", " ".join(cmd))
    print("=" * 80)

    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)

    if result.stderr:
        print("[stderr]\n" + result.stderr, file=sys.stderr)

    return result.stdout


def find_line_with_prefix(stdout: str, prefix: str):
    for line in stdout.splitlines():
        if line.startswith(prefix):
            return line.strip()
    return None


# ----------------------------------------------------------------------
# Main benchmark
# ----------------------------------------------------------------------
def main():
    output_csv = "benchmark_summary.csv"

    header = [
        "instance",
        "algorithm",
        "best_cost",
        "avg_cost",
        "worst_cost",
        "num_runs",
        "best_run",
        "best_seed_or_na",
        "num_routes",
        "num_nodes",
        "num_customers",
        "capacity",
        "total_demand",
        "best_route",
        "chromosome_or_na",
        "total_time_sec",
        "avg_time_sec",
    ]

    with open(output_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)

        for inst in INSTANCE_FILES:
            print(f"\n########## INSTANCE: {inst} ##########")

            # info dasar instance (dipakai untuk baris Greedy)
            n, cap, _, demands = load_cvrp_instance(inst)
            total_demand = sum(demands)

            # ------------------ GREEDY ------------------
            out = run_and_capture([sys.executable, "greedy_vrp.py", inst])
            line = find_line_with_prefix(out, "GREEDY_SUMMARY|")
            if line is None:
                print(f"[WARN] GREEDY_SUMMARY tidak ditemukan untuk {inst}", file=sys.stderr)
            else:
                # GREEDY_SUMMARY|instance|cost|num_routes|capacity|route|time_sec
                parts = line.split("|")
                (
                    _tag,
                    instance_file,
                    cost,
                    num_routes,
                    capacity_str,
                    route_str,
                    time_sec,
                ) = parts

                writer.writerow([
                    instance_file,           # instance
                    "Greedy",                # algorithm
                    float(cost),             # best_cost
                    float(cost),             # avg_cost
                    float(cost),             # worst_cost
                    1,                       # num_runs
                    1,                       # best_run
                    "-",                     # best_seed_or_na
                    int(num_routes),         # num_routes
                    n,                       # num_nodes
                    n - 1,                   # num_customers
                    float(capacity_str),     # capacity
                    total_demand,            # total_demand
                    route_str,               # best_route
                    "-",                     # chromosome_or_na
                    float(time_sec),         # total_time_sec
                    float(time_sec),         # avg_time_sec
                ])

            # ------------------ GA ------------------
            out = run_and_capture([sys.executable, "ga_vrp.py", inst, str(GA_RUNS)])
            line = find_line_with_prefix(out, "GA_SUMMARY|")
            if line is None:
                print(f"[WARN] GA_SUMMARY tidak ditemukan untuk {inst}", file=sys.stderr)
            else:
                parts = line.split("|")
                (
                    _tag,
                    instance_file,
                    best_cost,
                    avg_cost,
                    worst_cost,
                    num_runs,
                    best_run,
                    best_seed,
                    num_routes,
                    num_nodes,
                    num_customers,
                    capacity_str,
                    total_dem_str,
                    best_route_str,
                    chrom_str,
                    total_time_str,
                    avg_time_str,
                ) = parts

                writer.writerow([
                    instance_file,
                    "GA",
                    float(best_cost),
                    float(avg_cost),
                    float(worst_cost),
                    int(num_runs),
                    int(best_run),
                    best_seed,
                    int(num_routes),
                    int(num_nodes),
                    int(num_customers),
                    float(capacity_str),
                    float(total_dem_str),
                    best_route_str,
                    chrom_str,
                    float(total_time_str),
                    float(avg_time_str),
                ])

            # ------------------ TABU ------------------
            out = run_and_capture([sys.executable, "tabu_vrp.py", inst, str(TABU_RUNS)])
            line = find_line_with_prefix(out, "TABU_SUMMARY|")
            if line is None:
                print(f"[WARN] TABU_SUMMARY tidak ditemukan untuk {inst}", file=sys.stderr)
            else:
                parts = line.split("|")
                (
                    _tag,
                    instance_file,
                    best_cost,
                    avg_cost,
                    worst_cost,
                    num_runs,
                    best_run,
                    best_seed,
                    num_routes,
                    num_nodes,
                    num_customers,
                    capacity_str,
                    total_dem_str,
                    best_route_str,
                    chrom_str,
                    total_time_str,
                    avg_time_str,
                ) = parts

                writer.writerow([
                    instance_file,
                    "Tabu",
                    float(best_cost),
                    float(avg_cost),
                    float(worst_cost),
                    int(num_runs),
                    int(best_run),
                    best_seed,
                    int(num_routes),
                    int(num_nodes),
                    int(num_customers),
                    float(capacity_str),
                    float(total_dem_str),
                    best_route_str,
                    chrom_str,
                    float(total_time_str),
                    float(avg_time_str),
                ])

            # ------------------ SA (Simulated Annealing) ------------------
            out = run_and_capture([sys.executable, "sa_vrp.py", inst, str(SA_RUNS)])
            line = find_line_with_prefix(out, "SA_SUMMARY|")
            if line is None:
                print(f"[WARN] SA_SUMMARY tidak ditemukan untuk {inst}", file=sys.stderr)
            else:
                parts = line.split("|")
                (
                    _tag,
                    instance_file,
                    best_cost,
                    avg_cost,
                    worst_cost,
                    num_runs,
                    best_run,
                    best_seed,
                    num_routes,
                    num_nodes,
                    num_customers,
                    capacity_str,
                    total_dem_str,
                    best_route_str,
                    chrom_str,
                    total_time_str,
                    avg_time_str,
                ) = parts

                writer.writerow([
                    instance_file,
                    "SA",                    # Nama Algoritma
                    float(best_cost),
                    float(avg_cost),
                    float(worst_cost),
                    int(num_runs),
                    int(best_run),
                    best_seed,
                    int(num_routes),
                    int(num_nodes),
                    int(num_customers),
                    float(capacity_str),
                    float(total_dem_str),
                    best_route_str,
                    chrom_str,
                    float(total_time_str),
                    float(avg_time_str),
                ])

            # ------------------ OR-TOOLS ------------------
            out = run_and_capture([sys.executable, "ortools_solver.py", inst, str(ORTOOLS_RUNS)])
            line = find_line_with_prefix(out, "ORTOOLS_SUMMARY|")
            if line is None:
                print(f"[WARN] ORTOOLS_SUMMARY tidak ditemukan untuk {inst}", file=sys.stderr)
            else:
                parts = line.split("|")
                (
                    _tag,
                    instance_file,
                    best_cost,
                    avg_cost,
                    worst_cost,
                    num_runs,
                    best_run,
                    num_routes,
                    num_nodes,
                    num_customers,
                    capacity_str,
                    total_dem_str,
                    route_str,
                    best_time_str,
                    avg_time_str,
                ) = parts

                writer.writerow([
                    instance_file,
                    "OR-Tools",
                    float(best_cost),
                    float(avg_cost),
                    float(worst_cost),
                    int(num_runs),
                    int(best_run),
                    "-",                     # best_seed_or_na
                    int(num_routes),
                    int(num_nodes),
                    int(num_customers),
                    float(capacity_str),
                    float(total_dem_str),
                    route_str,
                    "-",                     # chromosome_or_na
                    float(best_time_str),
                    float(avg_time_str),
                ])

    print(f"\n✅ Ringkasan benchmarking tersimpan di: {output_csv}")


if __name__ == "__main__":
    main()