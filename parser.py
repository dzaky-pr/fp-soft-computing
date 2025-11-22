def load_cvrp_instance(path: str):
    """
    Parse file .vrp (CVRP, EXPLICIT FULL_MATRIX) dan kembalikan:
    - n          : jumlah node (depot + customer)
    - capacity   : kapasitas kendaraan
    - dist       : matriks jarak [n][n]
    - demands    : list demand per node (index 0 = depot)

    Diasumsikan format mirip:
        DIMENSION : 25
        CAPACITY : 30
        EDGE_WEIGHT_SECTION
        <n x n matrix>
        DEMAND_SECTION
        node demand
        ...
    """
    with open(path, "r") as f:
        # buang baris kosong & strip whitespace
        lines = [line.strip() for line in f if line.strip() != ""]

    n = None
    capacity = None

    i = 0
    # cari DIMENSION, CAPACITY dan EDGE_WEIGHT_SECTION
    while i < len(lines):
        line = lines[i]

        if line.startswith("DIMENSION"):
            # contoh: "DIMENSION : 25"
            n = int(line.split(":")[1])
        elif line.startswith("CAPACITY"):
            capacity = float(line.split(":")[1])
        elif line == "EDGE_WEIGHT_SECTION":
            i += 1  # posisi baris pertama matriks
            break

        i += 1

    if n is None or capacity is None:
        raise ValueError("DIMENSION atau CAPACITY tidak ditemukan di file .vrp")

    # baca matriks jarak n×n
    dist = []
    for r in range(n):
        parts = lines[i + r].split()
        if len(parts) != n:
            raise ValueError(f"Row {r} di EDGE_WEIGHT_SECTION tidak punya {n} kolom")
        row = list(map(float, parts))
        dist.append(row)
    i += n

    # lompat ke DEMAND_SECTION
    while i < len(lines) and lines[i] != "DEMAND_SECTION":
        i += 1
    if i >= len(lines):
        raise ValueError("DEMAND_SECTION tidak ditemukan di file .vrp")
    i += 1  # baris pertama data demand

    demands = [0.0] * n
    for _ in range(n):
        if i >= len(lines):
            raise ValueError("Jumlah baris DEMAND_SECTION kurang dari DIMENSION")
        node, d = lines[i].split()
        idx = int(node) - 1  # node 1 → index 0
        demands[idx] = float(d)
        i += 1

    return n, capacity, dist, demands
