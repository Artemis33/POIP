"""Warehouse instance data loader.

This module provides a `WarehouseLoader` class that reads all the
files describing a warehouse slotting problem instance and returns
them as a structured `WarehouseInstance` dataclass.
"""

import os
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class WarehouseInstance:
    """
    A complete warehouse slotting problem instance.

    Attributes
    ----------
    adjacency : List[List[int]]
        Square adjacency matrix (n x n) between racks.
    rack_capacity : List[int]
        Capacity (number of slots) available for each rack.
    product_circuit : List[int]
        Circuit identifier for each product.
    aisles_racks : List[List[int]]
        For each aisle, the list of rack IDs present in the aisle.
    orders : List[List[int]]
        List of orders; each order is a list of product IDs.
    metadata : Dict[str, float]
        Miscellaneous instance metadata (counts and parameters).
    """
    def __init__(self, adjacency: List[List[int]], rack_capacity: List[int],
                 product_circuit: List[int], aisles_racks: List[List[int]],
                 orders: List[List[int]], metadata: Dict[str, float]):
        """
        Docstring pour __init__
        
        :param adjacency: Square adjacency matrix (n x n) between racks.
        :type adjacency: List[List[int]]
        :param rack_capacity: Capacity (number of slots) available for each rack.
        :type rack_capacity: List[int]
        :param product_circuit: Circuit identifier for each product.
        :type product_circuit: List[int]
        :param aisles_racks: For each aisle, the list of rack IDs present in the aisle.
        :type aisles_racks: List[List[int]]
        :param orders: List of orders; each order is a list of product IDs.
        :type orders: List[List[int]]
        :param metadata: Miscellaneous instance metadata (counts and parameters).
        :type metadata: Dict[str, float]
        """
        self.adjacency = adjacency
        self.rack_capacity = rack_capacity
        self.product_circuit = product_circuit
        self.aisles_racks = aisles_racks
        self.orders = orders
        self.metadata = metadata

    def __str__(self):
        return (f"WarehouseInstance(num_racks={len(self.rack_capacity)}, "
                f"capacity={sum(self.rack_capacity)}, "
                f"num_products={len(self.product_circuit)}, "
                f"num_orders={len(self.orders)})")


class WarehouseLoader:
    """
    Loads warehouse data files from a directory.

    Attributes
    ----------
    dir : str
        Path to the directory containing the instance files.

    Methods
    -------
    __init__(warehouse_dir: str)
        Initializes the loader with the given directory.
    _path(filename: str) -> str
        Builds the absolute path to a file within the directory.
    _read_lines(filename: str) -> List[str]
        Reads non-empty, non-comment lines from a file.
    load_adjacency_matrix() -> List[List[int]]
        Loads the rack adjacency matrix.
    load_rack_capacity() -> List[int]
        Loads the rack capacities.
    load_product_circuits() -> List[int]
        Loads the circuit ID for each product.
    load_aisles_racks() -> List[List[int]]
        Loads the aisle-to-racks mapping.
    load_orders() -> List[List[int]]
        Loads the list of orders and their product IDs.
    load_metadata() -> Dict[str, float]
        Loads instance metadata values.
    load_all() -> WarehouseInstance
        Loads all components and returns a `WarehouseInstance`.
    """

    def __init__(self, warehouse_dir: str):
        """
        Initializes the `WarehouseLoader` with the path to the instance directory.

        Parameters
        ----------
        warehouse_dir : str
            Directory containing the instance files.
        """
        self.dir = warehouse_dir

    def _path(self, filename: str) -> str:
        """
        Build an absolute path for a file inside the instance directory.

        Parameters
        ----------
        filename : str
            File name relative to the instance directory.

        Returns
        -------
        str
            The absolute filesystem path.
        """
        return os.path.join(self.dir, filename)

    def _read_lines(self, filename: str) -> List[str]:
        """
        Read non-empty, non-comment lines from a file.

        Notes
        -----
        Lines that are empty or start with "..." are ignored.

        Parameters
        ----------
        filename : str
            File name to read from the instance directory.

        Returns
        -------
        List[str]
            Cleaned list of lines.
        """
        with open(self._path(filename)) as f:
            return [l.strip() for l in f if l.strip() and not l.startswith("...")]

    def load_adjacency_matrix(self) -> List[List[int]]:
        """
        Load the rack adjacency matrix.

        Format
        ------
        The first line contains `n`, the number of racks. The next `n` lines
        contain `n` integers each, forming a square adjacency matrix.

        Returns
        -------
        List[List[int]]
            The `n x n` adjacency matrix of racks.
        """
        lines = self._read_lines("rack_adjacency_matrix.txt")
        n = int(lines[0])
        return [list(map(int, lines[i + 1].split())) for i in range(n)]

    def load_rack_capacity(self) -> List[int]:
        """
        Load the capacity for each rack.

        Format
        ------
        The first line is a header; capacities start from line 2 to the end.

        Returns
        -------
        List[int]
            Capacity per rack.
        """
        lines = self._read_lines("rack_capacity.txt")
        return list(map(int, lines[1:]))

    def load_product_circuits(self) -> List[int]:
        """
        Load the circuit identifier for each product.

        Format
        ------
        The first line is a header; circuit IDs start from line 2 to the end.

        Returns
        -------
        List[int]
            Circuit ID per product.
        """
        lines = self._read_lines("product_circuit.txt")
        return list(map(int, lines[1:]))

    def load_aisles_racks(self) -> List[List[int]]:
        """
        Load the list of racks per aisle.

        Format
        ------
        Each line (after the header) is formatted as:
        `<num_racks> <rack_id_1> <rack_id_2> ...`. The first element is a
        count and is skipped; the remainder are rack IDs.

        Returns
        -------
        List[List[int]]
            For each aisle, the list of rack IDs.
        """
        lines = self._read_lines("aisle_racks.txt")
        # New format: the first integer on each line is the count, which we skip.
        return [list(map(int, l.split()))[1:] for l in lines[1:]]

    def load_orders(self) -> List[List[int]]:
        """
        Load the list of orders.

        Format
        ------
        Each line (after the header) is formatted as:
        `<num_products> <product_id_1> <product_id_2> ...`. The first element
        is a count and is skipped; the remainder are product IDs.

        Returns
        -------
        List[List[int]]
            Orders represented as lists of product IDs.
        """
        lines = self._read_lines("orders.txt")
        return [list(map(int, l.split()))[1:] for l in lines[1:]]

    def load_metadata(self) -> Dict[str, float]:
        """
        Load instance metadata values.

        Keys
        ----
        `num_racks`, `total_slots`, `aeration_rate`, `num_products`,
        `num_circuits`, `num_aisles`, `num_orders`.

        Notes
        -----
        `aeration_rate` is parsed as `float`, all others as `int`.

        Returns
        -------
        Dict[str, float]
            Mapping of metadata keys to their numeric values.
        """
        lines = self._read_lines("metadata.txt")
        keys = ["num_racks", "total_slots", "aeration_rate",
                "num_products", "num_circuits", "num_aisles", "num_orders"]
        return {k: float(lines[i]) if k == "aeration_rate" else int(lines[i])
                for i, k in enumerate(keys)}

    def load_all(self) -> WarehouseInstance:
        """
        Load all components of the warehouse instance.

        Returns
        -------
        WarehouseInstance
            Structured data object containing all loaded components.
        """
        return WarehouseInstance(
            adjacency=self.load_adjacency_matrix(),
            rack_capacity=self.load_rack_capacity(),
            product_circuit=self.load_product_circuits(),
            aisles_racks=self.load_aisles_racks(),
            orders=self.load_orders(),
            metadata=self.load_metadata(),
        )
