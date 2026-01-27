"""
Solution checker for the slotting problem.

Checks:
1. All products assigned to a valid rack
2. Rack capacities respected
3. Minimum aeration per aisle
4. Circuit contiguity (intervals do not overlap except at boundaries)
"""

import os
import math
from collections import defaultdict


def read_solution(file_path) -> list[int]:
    """
    Read rack_product_assignment.txt: line 0 = number of products, then one rack per line.

    Parameters
    ----------
    file_path : str
        Path to the solution file.

    Returns
    -------
    list[int]
        List of racks assigned to each product.
    """
    with open(file_path) as f:
        lines = [l.strip() for l in f if l.strip()]
    n = int(lines[0])
    if len(lines) - 1 != n:
        raise ValueError(f"File declares {n} products but contains {len(lines) - 1} lines.")
    return [int(lines[i + 1]) for i in range(n)]


def check_all_products_assigned(instance, rack_of_product) -> None:
    """
    Verify that each product has a valid rack assignment.

    Parameters
    ----------
    instance : WarehouseInstance
        Problem instance.
    rack_of_product : list[int]
        List of racks assigned to each product.
    """
    expected = instance.metadata["num_products"]
    num_racks = len(instance.rack_capacity)

    if len(rack_of_product) != expected:
        raise ValueError(f"{len(rack_of_product)} products provided, {expected} expected.")

    for p, r in enumerate(rack_of_product):
        if not (0 <= r < num_racks):
            raise ValueError(f"Product {p}: invalid rack {r} (0 to {num_racks - 1}).")


def check_rack_capacity(instance, rack_of_product) -> None:
    """
    Verify that the number of products per rack does not exceed capacity.

    Parameters
    ----------
    instance : WarehouseInstance
        Problem instance.
    rack_of_product : list[int]
        List of racks assigned to each product.
    """
    count = defaultdict(int)
    for r in rack_of_product:
        count[r] += 1

    for r, n in count.items():
        cap = instance.rack_capacity[r]
        if n > cap:
            raise ValueError(f"Rack {r}: {n} products for capacity {cap}.")


def check_aeration(instance, rack_of_product) -> None:
    """
    Verify minimum aeration per aisle.

    Parameters
    ----------
    instance : WarehouseInstance
        Problem instance.
    rack_of_product : list[int]
        List of racks assigned to each product.
    """
    rate = instance.metadata["aeration_rate"] / 100.0
    count = defaultdict(int)
    for r in rack_of_product:
        count[r] += 1

    for i, aisle in enumerate(instance.aisles_racks):
        total_cap = sum(instance.rack_capacity[r] for r in aisle)
        min_aeration = math.ceil(total_cap * rate)
        actual = sum(instance.rack_capacity[r] - count[r] for r in aisle)
        if actual < min_aeration:
            raise ValueError(f"Aisle {i}: aeration {actual}, minimum {min_aeration}.")


def check_circuit_contiguity(instance, rack_of_product) -> None:
    """
    Verify circuit contiguity via intervals.
    Intervals [min, max] may only touch at boundaries (no overlap).

    Parameters
    ----------
    instance : WarehouseInstance
        Problem instance.
    rack_of_product : list[int]
        List of racks assigned to each product.
    """
    product_circuit = instance.product_circuit
    intervals = {}

    for p, r in enumerate(rack_of_product):
        c = product_circuit[p]
        if c not in intervals:
            intervals[c] = [r, r]
        else:
            intervals[c][0] = min(intervals[c][0], r)
            intervals[c][1] = max(intervals[c][1], r)

    # Sort by (lower bound, upper bound) then compare neighbors (O(n log n))
    circuits = sorted(intervals.keys(), key=lambda c: (intervals[c][0], intervals[c][1]))
    for c1, c2 in zip(circuits, circuits[1:]):
        # Overlap forbidden if max1 > min2 (equality at boundaries allowed)
        if intervals[c1][1] > intervals[c2][0]:
            raise ValueError(
                f"Contiguity violated: circuit {c1} {intervals[c1]} "
                f"and circuit {c2} {intervals[c2]}."
            )


def calculate_cost(instance, rack_of_product) -> int:
    """
    Compute total cost: sum of collection distances.

    Parameters
    ----------
    instance : WarehouseInstance
        Problem instance.
    rack_of_product : list[int]
        List of racks assigned to each product.

    Returns
    -------
    int
        Total solution cost.
    """
    adj = instance.adjacency
    start, end = 0, len(adj) - 1
    total = 0

    for order in instance.orders:
        racks = sorted({rack_of_product[p] for p in order})
        path = [start] + racks + [end]
        total += sum(adj[path[i]][path[i + 1]] for i in range(len(path) - 1))

    return total


def checker(instance, solution_dir) -> int:
    """
    Perform all checks and print the result.

    Parameters
    ----------
    instance : WarehouseInstance
        Problem instance.
    solution_dir : str
        Directory containing the solution.

    Returns
    -------
    int
        Solution cost if valid, None otherwise.
    """
    try:
        path = os.path.join(solution_dir, "rack_product_assignment.txt")
        rack_of_product = read_solution(path)

        check_all_products_assigned(instance, rack_of_product)
        check_rack_capacity(instance, rack_of_product)
        check_aeration(instance, rack_of_product)
        check_circuit_contiguity(instance, rack_of_product)

        cost = calculate_cost(instance, rack_of_product)
        print(f"Valid solution. Cost = {cost}")
        return cost

    except (ValueError, FileNotFoundError) as e:
        print(f"ERROR: {e}")
        return None
