from Resolution import Resolution

class Naif(Resolution):

    def solve(self):
        """
        Naive resolution:
        - Group products by their circuit and place circuits one after another.
        - Keep products of the same circuit contiguous; allow boundary racks
          to contain the tail of one circuit and the beginning of the next.
        - Respect rack capacities and per-aisle aeration rate.
        """
        instance = self.instance

        product_circuit = instance.product_circuit
        rack_capacity = instance.rack_capacity
        aisles_racks = instance.aisles_racks
        aeration_rate = float(instance.metadata.get("aeration_rate", 0.0))
        num_products = int(instance.metadata.get("num_products", len(product_circuit)))

        # Group products by circuit, preserving original product order
        products_by_circuit = {}
        for pid, circuit in enumerate(product_circuit):
            products_by_circuit.setdefault(circuit, []).append(pid)

        # Place circuits sequentially (ascending circuit id)
        ordered_products = []
        for circuit_id in sorted(products_by_circuit.keys()):
            ordered_products.extend(products_by_circuit[circuit_id])

        # Compute allowed fill per aisle based on aeration rate
        aisle_allowed = []
        total_allowed = 0
        for racks in aisles_racks:
            total_cap = sum(rack_capacity[r] for r in racks)
            allowed = int((1.0 - aeration_rate/100.0) * total_cap)
            aisle_allowed.append(allowed)
            total_allowed += allowed
        
        if num_products > total_allowed:
            raise RuntimeError(
                "Insufficient capacity with aeration_rate to place all products"
            )

        # Assign product positions: index -> rack id
        positions = [None] * num_products
        prod_idx = 0

        # Fill aisle by aisle, rack by rack, respecting per-aisle allowed fill
        for i, racks in enumerate(aisles_racks):
            remaining_in_aisle = aisle_allowed[i]
            for r in racks:
                if remaining_in_aisle <= 0 or prod_idx >= num_products:
                    break
                cap = rack_capacity[r]
                slots = min(cap, remaining_in_aisle)
                for _ in range(slots):
                    if prod_idx >= num_products:
                        break
                    pid = ordered_products[prod_idx]
                    positions[pid] = r
                    prod_idx += 1
                    remaining_in_aisle -= 1
            if prod_idx >= num_products:
                break

        # Sanity check
        if any(p is None for p in positions):
            raise RuntimeError("Failed to assign all products to racks")

        self.solution._positions = positions
        self.solution._value = num_products

        