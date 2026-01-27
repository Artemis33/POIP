from WarehouseLoader import WarehouseLoader, WarehouseInstance
from WarehouseSolution import WarehouseSolution


class Resolution:
    """
    Base class for warehouse problem-solving algorithms.
    
    Attributes
    ----------
    warehouse_loader : WarehouseLoader
        WarehouseLoader instance that loads warehouse data.
    solution : WarehouseSolution
        WarehouseSolution instance that stores the problem solution.

    Methods
    -------
    __init__(self, instance_name: str)
        Initializes the Resolution class with the instance name.
    solve(self)
        Method to implement in subclasses to solve the problem.
    """

    def __init__(self, instance_name: str):
        """
        Initializes the Resolution class with the given instance name.
        
        @param instance_name: str - The name of the warehouse instance to load.
        """
        warehouse_loader = WarehouseLoader(instance_name)
        self.instance = warehouse_loader.load_all()

        self.solution = WarehouseSolution(instance_name.split("/")[-2], self.__class__.__name__)

        print(self.instance)

        self.solve()
        self.solution.save_solution()

    def solve(self):
        """
        Solves the warehouse problem.
        This method should be implemented in subclasses.
        """
        raise NotImplementedError("Method solve() must be implemented in subclass.")

    def write_svg(self, path: str, width: float = 1600.0, height: float = 800.0) -> bool:
        """
        Write an SVG that represents the warehouse and order paths.

        - Racks are rectangles, laid out per aisle (two columns per aisle).
        - Even-numbered aisles go up; odd-numbered aisles go down (S-PATH).
        - Rack ID is centered inside the rectangle.
        - Racks 0 (bottom center) and n-1 (top center) are outside aisles.
        - Each aisle has entry/exit points (depending on direction).
        - Each order is a path composed of segments within aisles:
            entry -> racks of the order (only those storing its products) -> exit.
            Between consecutive aisles: a segment exit -> next entry.
            For aisles with no racks to visit, draw a direct entry -> exit line.

        :param path: Output SVG file path.
        :param width: SVG canvas width.
        :param height: SVG canvas height.
        :return: True if writing succeeds, False otherwise.
        """
        try:
            inst = self.instance
            sol = self.solution

            num_racks = int(inst.metadata.get("num_racks", len(inst.rack_capacity)))
            aisles = inst.aisles_racks
            num_aisles = len(aisles)

            # Color palette for circuits and orders
            palette = [
                "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
                "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"
            ]
            def color_for_index(i: int) -> str:
                if i < len(palette):
                    return palette[i]
                base = i % len(palette)
                return palette[base]

            # Map rack -> placed products (and circuits)
            rack_products = {}
            for p_idx, rack_id in enumerate(sol._positions):
                try:
                    rid = int(rack_id)
                except Exception:
                    continue
                if rid < 0 or rid >= num_racks:
                    continue
                rack_products.setdefault(rid, []).append(p_idx)

            rack_circuits = {}
            for rid, plist in rack_products.items():
                circuits = []
                for p in plist[:2]:
                    c = inst.product_circuit[p]
                    circuits.append(c)
                rack_circuits[rid] = circuits

            # Geometry
            margin = 40.0
            rack_w = 46.0
            rack_h = 24.0
            col_gap = 70.0
            aisle_gap = 90.0

            top_y = margin + rack_h / 2.0
            bottom_y = height - margin - rack_h / 2.0

            def aisle_x_positions(j: int):
                left_x = margin + j * (2 * rack_w + col_gap + aisle_gap)
                right_x = left_x + rack_w + col_gap
                center_x = left_x + rack_w + col_gap / 2.0
                return left_x, right_x, center_x

            # Precompute: max rows per column for vertical spacing
            def split_columns(rack_list):
                # Exclude central racks 0 and n-1 from aisles
                filtered = [r for r in rack_list if r not in (0, num_racks - 1)]
                odds = sorted([r for r in filtered if r % 2 == 1])
                evens = sorted([r for r in filtered if r % 2 == 0])
                if len(filtered) > 0 and (len(odds) == 0 or len(evens) == 0):
                    # Fallback: split into two balanced columns if one is empty
                    srt = sorted(filtered)
                    mid = len(srt) // 2
                    odds = srt[:mid]
                    evens = srt[mid:]
                return odds, evens

            max_rows = 1
            columns_per_aisle = []
            for j in range(num_aisles):
                oc, ec = split_columns(aisles[j])
                columns_per_aisle.append((oc, ec))
                max_rows = max(max_rows, len(oc), len(ec))

            def y_positions(count: int, direction_up: bool):
                if count <= 0:
                    return []
                span = (bottom_y - top_y)
                step = span / max(count - 1, 1)
                ys = [top_y + i * step for i in range(count)]
                if direction_up:
                    # IDs increase with height -> sorted elements go bottom to top
                    ys = list(reversed(ys))
                return ys

            # Prepare rack centers for drawing and routing
            rack_centers = {}
            for j in range(num_aisles):
                direction_up = (j % 2 == 0)
                odds, evens = columns_per_aisle[j]
                y_odds = y_positions(len(odds), direction_up)
                y_evens = y_positions(len(evens), direction_up)
                left_x, right_x, center_x = aisle_x_positions(j)
                for idx, rid in enumerate(odds):
                    rack_centers[rid] = (left_x + rack_w / 2.0, y_odds[idx])
                for idx, rid in enumerate(evens):
                    rack_centers[rid] = (right_x + rack_w / 2.0, y_evens[idx])

            # Central racks 0 (bottom) and n-1 (top)
            center_x_global = width / 2.0
            rack_centers[0] = (center_x_global, bottom_y)
            rack_centers[num_racks - 1] = (center_x_global, top_y)

            # SVG writing
            with open(path, "w", encoding="utf-8") as svg:
                svg.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
                svg.write(f"<svg xmlns=\"http://www.w3.org/2000/svg\" version=\"1.1\" width=\"{width}\" height=\"{height}\">\n")
                svg.write("<rect width=\"100%\" height=\"100%\" fill=\"white\"/>\n")

                # Draw aisles: entry/exit points
                for j in range(num_aisles):
                    left_x, right_x, center_x = aisle_x_positions(j)
                    direction_up = (j % 2 == 0)
                    entry_y = top_y if direction_up else bottom_y
                    exit_y = bottom_y if direction_up else top_y
                    svg.write(f"<circle cx=\"{center_x}\" cy=\"{entry_y}\" r=\"6\" fill=\"#333\"/>\n")
                    svg.write(f"<circle cx=\"{center_x}\" cy=\"{exit_y}\" r=\"6\" fill=\"#333\"/>\n")

                # Draw racks (rectangles + label)
                for j in range(num_aisles):
                    left_x, right_x, center_x = aisle_x_positions(j)
                    odds, evens = columns_per_aisle[j]
                    direction_up = (j % 2 == 0)
                    y_odds = y_positions(len(odds), direction_up)
                    y_evens = y_positions(len(evens), direction_up)

                    for idx, rid in enumerate(odds):
                        cx, cy = left_x + rack_w / 2.0, y_odds[idx]
                        x = cx - rack_w / 2.0
                        y = cy - rack_h / 2.0
                        circuits = rack_circuits.get(rid, [])
                        if len(circuits) == 0:
                            svg.write(f"<rect x=\"{x}\" y=\"{y}\" width=\"{rack_w}\" height=\"{rack_h}\" fill=\"white\" stroke=\"black\" stroke-width=\"1\"/>\n")
                        elif len(circuits) == 1:
                            fill = color_for_index(int(circuits[0]))
                            svg.write(f"<rect x=\"{x}\" y=\"{y}\" width=\"{rack_w}\" height=\"{rack_h}\" fill=\"{fill}\" stroke=\"black\" stroke-width=\"1\"/>\n")
                        else:
                            c1 = color_for_index(int(circuits[0]))
                            c2 = color_for_index(int(circuits[1]))
                            svg.write(f"<rect x=\"{x}\" y=\"{y}\" width=\"{rack_w/2.0}\" height=\"{rack_h}\" fill=\"{c1}\" stroke=\"black\" stroke-width=\"1\"/>\n")
                            svg.write(f"<rect x=\"{x + rack_w/2.0}\" y=\"{y}\" width=\"{rack_w/2.0}\" height=\"{rack_h}\" fill=\"{c2}\" stroke=\"black\" stroke-width=\"1\"/>\n")
                        svg.write(f"<text x=\"{cx}\" y=\"{cy + 4}\" font-size=\"12\" text-anchor=\"middle\" fill=\"black\">{rid}</text>\n")

                    for idx, rid in enumerate(evens):
                        cx, cy = right_x + rack_w / 2.0, y_evens[idx]
                        x = cx - rack_w / 2.0
                        y = cy - rack_h / 2.0
                        circuits = rack_circuits.get(rid, [])
                        if len(circuits) == 0:
                            svg.write(f"<rect x=\"{x}\" y=\"{y}\" width=\"{rack_w}\" height=\"{rack_h}\" fill=\"white\" stroke=\"black\" stroke-width=\"1\"/>\n")
                        elif len(circuits) == 1:
                            fill = color_for_index(int(circuits[0]))
                            svg.write(f"<rect x=\"{x}\" y=\"{y}\" width=\"{rack_w}\" height=\"{rack_h}\" fill=\"{fill}\" stroke=\"black\" stroke-width=\"1\"/>\n")
                        else:
                            c1 = color_for_index(int(circuits[0]))
                            c2 = color_for_index(int(circuits[1]))
                            svg.write(f"<rect x=\"{x}\" y=\"{y}\" width=\"{rack_w/2.0}\" height=\"{rack_h}\" fill=\"{c1}\" stroke=\"black\" stroke-width=\"1\"/>\n")
                            svg.write(f"<rect x=\"{x + rack_w/2.0}\" y=\"{y}\" width=\"{rack_w/2.0}\" height=\"{rack_h}\" fill=\"{c2}\" stroke=\"black\" stroke-width=\"1\"/>\n")
                        svg.write(f"<text x=\"{cx}\" y=\"{cy + 4}\" font-size=\"12\" text-anchor=\"middle\" fill=\"black\">{rid}</text>\n")

                # Central racks 0 and n-1
                for rid in (0, num_racks - 1):
                    cx, cy = rack_centers[rid]
                    x = cx - rack_w / 2.0
                    y = cy - rack_h / 2.0
                    circuits = rack_circuits.get(rid, [])
                    if len(circuits) == 0:
                        svg.write(f"<rect x=\"{x}\" y=\"{y}\" width=\"{rack_w}\" height=\"{rack_h}\" fill=\"white\" stroke=\"black\" stroke-width=\"1.5\"/>\n")
                    elif len(circuits) == 1:
                        fill = color_for_index(int(circuits[0]))
                        svg.write(f"<rect x=\"{x}\" y=\"{y}\" width=\"{rack_w}\" height=\"{rack_h}\" fill=\"{fill}\" stroke=\"black\" stroke-width=\"1.5\"/>\n")
                    else:
                        c1 = color_for_index(int(circuits[0]))
                        c2 = color_for_index(int(circuits[1]))
                        svg.write(f"<rect x=\"{x}\" y=\"{y}\" width=\"{rack_w/2.0}\" height=\"{rack_h}\" fill=\"{c1}\" stroke=\"black\" stroke-width=\"1.5\"/>\n")
                        svg.write(f"<rect x=\"{x + rack_w/2.0}\" y=\"{y}\" width=\"{rack_w/2.0}\" height=\"{rack_h}\" fill=\"{c2}\" stroke=\"black\" stroke-width=\"1.5\"/>\n")
                    svg.write(f"<text x=\"{cx}\" y=\"{cy + 4}\" font-size=\"12\" text-anchor=\"middle\" fill=\"black\">{rid}</text>\n")

                # Paths per order
                for k, order in enumerate(inst.orders):
                    stroke = color_for_index(k)
                    stroke_w = 2.0
                    # Iterate aisles to build overall serpentine path
                    prev_exit = None
                    for j in range(num_aisles):
                        left_x, right_x, center_x = aisle_x_positions(j)
                        direction_up = (j % 2 == 0)
                        entry_y = top_y if direction_up else bottom_y
                        exit_y = bottom_y if direction_up else top_y
                        entry_pt = (center_x, entry_y)
                        exit_pt = (center_x, exit_y)

                        if prev_exit is not None:
                            svg.write(
                                f"<line x1=\"{prev_exit[0]}\" y1=\"{prev_exit[1]}\" x2=\"{entry_pt[0]}\" y2=\"{entry_pt[1]}\" stroke=\"{stroke}\" stroke-width=\"{stroke_w}\" opacity=\"0.6\"/>\n"
                            )

                        # Order racks within this aisle
                        aisle_racks_set = set([r for r in aisles[j] if r not in (0, num_racks - 1)])
                        visit_points = []
                        for prod in order:
                            try:
                                rid = int(sol._positions[prod])
                            except Exception:
                                continue
                            if rid in aisle_racks_set:
                                visit_points.append(rack_centers.get(rid))

                        # Sort by traversal direction within the aisle
                        if len(visit_points) > 0:
                            if direction_up:
                                visit_points.sort(key=lambda p: p[1], reverse=False)  # top to bottom: increasing y
                            else:
                                visit_points.sort(key=lambda p: p[1], reverse=True)   # bottom to top: decreasing y

                            # entry -> racks -> exit
                            last = entry_pt
                            for pt in visit_points:
                                svg.write(
                                    f"<line x1=\"{last[0]}\" y1=\"{last[1]}\" x2=\"{pt[0]}\" y2=\"{pt[1]}\" stroke=\"{stroke}\" stroke-width=\"{stroke_w}\" opacity=\"0.8\"/>\n"
                                )
                                last = pt
                            svg.write(
                                f"<line x1=\"{last[0]}\" y1=\"{last[1]}\" x2=\"{exit_pt[0]}\" y2=\"{exit_pt[1]}\" stroke=\"{stroke}\" stroke-width=\"{stroke_w}\" opacity=\"0.8\"/>\n"
                            )
                        else:
                            # Aisle traversed without visiting racks
                            svg.write(
                                f"<line x1=\"{entry_pt[0]}\" y1=\"{entry_pt[1]}\" x2=\"{exit_pt[0]}\" y2=\"{exit_pt[1]}\" stroke=\"{stroke}\" stroke-width=\"{stroke_w}\" opacity=\"0.35\" stroke-dasharray=\"4 3\"/>\n"
                            )

                        prev_exit = exit_pt

                svg.write("</svg>\n")
            return True
        except Exception:
            return False