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

    def __init__(self, instance_name: str) -> None:
        """
        Initializes the Resolution class with the given instance name.
        
        @param instance_name: str - The name of the warehouse instance to load.
        """
        warehouse_loader = WarehouseLoader(instance_name)

        self.name = instance_name.split("/")[-2]
        self.instance = warehouse_loader.load_all()
        self.solution = WarehouseSolution(self.name, self.__class__.__name__)

        self.solve()
        self.solution.save_solution()

    def solve(self) -> None:
        """
        Solves the warehouse problem.
        This method should be implemented in subclasses.
        """
        raise NotImplementedError("Method solve() must be implemented in \
subclass.")

    def load_solution(self, instance: str, algo: str, id: str) -> None:
        """
        Load a solution from a file named {instance}_{algo}_{id}.sol

        Parameters
        ----------
        instance : str
            Name of the instance
        algo : str
            Name of the algorithm
        id : str
            Identifier of the solution file
        """
        self.solution.read_solution(instance, algo, id)

    def write_svg(self, order_to_draw: int = 0, 
                  width: float = 1600.0, height: float = 800.0) -> bool:
        """
        Write an SVG representing the warehouse and order paths.

        - Rack rectangles are placed using coordinates from \
            ../help/rack_coordinates.txt.
        If coordinates are normalized in [0,1], they are scaled to the canvas \
            size.
        If coordinates are absolute (possibly negative), they are \
            affine-transformed
        to fit inside the canvas with margins.
        - Aisles are used for entry/exit points and traversal order (S-PATH):
        even aisles go up (entry at top, exit at bottom), odd aisles go down.
        - Rack ID is centered inside its rectangle.
        - Racks 0 (bottom center) and n-1 (top center) are included as \
            normal racks
        with their coordinates from the file.
        - For each order, draw path segments within aisles:
        entry -> visited racks in this aisle (only racks storing its products)\
              -> exit.
        Between consecutive aisles: an exit -> next entry segment.
        If an aisle contains no racks to visit, draw a direct entry \
            -> exit dashed line.

        Parameters
        ----------
        order_to_draw: int
            Index of the order to visualize (0-based).
        width: float
            Width of the SVG canvas (default: 1600.0).
        height: float
            Height of the SVG canvas (default: 800.0).

        Returns
        -------
        bool
            True if SVG was successfully written, False otherwise.
        """
        try:
            import os

            inst = self.instance
            sol = self.solution

            # Instance basics
            num_racks = int(inst.metadata.get("num_racks", \
                                              len(inst.rack_capacity)))
            aisles = inst.aisles_racks
            num_aisles = len(aisles)

            # Color palette
            palette = [
                "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
                "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"
            ]
            def color_for_index(i: int) -> str:
                if i < len(palette):
                    return palette[i]
                return palette[i % len(palette)]
            

            # Map racks -> products and circuits 
            # (limit: 2 products for coloring)
            rack_products = {}
            for p_idx, rack_id in enumerate(sol._positions):
                try:
                    rid = int(rack_id)
                except Exception:
                    continue
                if 0 <= rid < num_racks:
                    rack_products.setdefault(rid, []).append(p_idx)

            rack_circuits = {}
            for rid, plist in rack_products.items():
                circuits = []
                for p in plist[:2]:
                    circuits.append(inst.product_circuit[p])
                rack_circuits[rid] = circuits

            # Geometry and margins
            margin = 40.0
            rack_w = 46.0
            rack_h = 24.0
            top_y = margin + rack_h / 2.0
            bottom_y = height - margin - rack_h / 2.0
            # Load rack coordinates from ../help/rack_coordinates.txt
            # Format:
            #   line 1: integer n (number of racks)
            #   next n lines: "x y" floats (normalized [0,1] or absolute, 
            #                               possibly negative)
            coords_path = os.path.join("../data/", self.name, "help", \
                                       "rack_coordinates.txt")
            rack_centers = {}
            with open(coords_path, "r", encoding="utf-8") as f:
                lines = [ln.strip() for ln in f.readlines() if ln.strip()]
                n_coords = int(lines[0])
                num_use = min(n_coords, num_racks)

                # Parse raw coordinates
                raw_coords = []
                for i in range(num_use):
                    parts = lines[i + 1].replace(",", " ").split()
                    if len(parts) < 2:
                        raise ValueError(f"Invalid coordinates line {i+2}:"+\
                                         f" {lines[i+1]}")
                    x_val = float(parts[0])
                    y_val = float(parts[1])
                    raw_coords.append((x_val, y_val))

                # Detect normalization (assume [0,1] if all in range)
                max_x = max(c[0] for c in raw_coords)
                max_y = max(c[1] for c in raw_coords)
                min_x = min(c[0] for c in raw_coords)
                min_y = min(c[1] for c in raw_coords)
                normalized = (max_x <= 1.0 and max_y <= 1.0 and \
                              min_x >= 0.0 and min_y >= 0.0)
                if normalized:
                    # Direct scaling to canvas size
                    for rid in range(num_use):
                        rx, ry = raw_coords[rid]
                        cx = rx * width
                        cy = ry * height
                        rack_centers[rid] = (cx, cy)
                else:
                    # Affine transform to fit inside canvas with margins 
                    # (handles negatives)
                    span_x = max_x - min_x
                    span_y = max_y - min_y
                    scale_x = (width - 2.0 * margin) / span_x if span_x > 0 \
                                else 1.0
                    scale_y = (height - 2.0 * margin) / span_y if span_y > 0 \
                                else 1.0
                    for rid in range(num_use):
                        rx, ry = raw_coords[rid]
                        cx = margin + (rx - min_x) * scale_x
                        cy = margin + (ry - min_y) * scale_y
                        rack_centers[rid] = (cx, cy)

                # If coords file has more than metadata racks, ignore extras
                # If coords file has fewer, missing racks won't be drawn

            # Compute aisle centers (x only) from rack coordinates
            aisle_center_x = []
            for j in range(num_aisles):
                racks_j = [r for r in aisles[j] if r in rack_centers]
                if len(racks_j) == 0:
                    # As a last resort, center in canvas
                    aisle_center_x.append(width / 2.0)
                else:
                    mean_x = sum(rack_centers[r][0] for r in racks_j) / \
                        float(len(racks_j))
                    aisle_center_x.append(mean_x)

            # Determine vertical bounds for aisles
            top_y = margin + (min([c[1] \
                    for c in raw_coords[1:-1]]) - min_y) * scale_y - rack_h 
            bottom_y = margin + (max([c[1] \
                    for c in raw_coords[1:-1]]) - min_y) * scale_y + rack_h 
            # Output file
            path = f"../graphs/{self.name}_{self.solution._algorithm}_"+\
                    f"{order_to_draw}_{self.solution._id}.svg"
            with open(path, "w", encoding="utf-8") as svg:
                # SVG header
                svg.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
                svg.write(f"<svg xmlns=\"http://www.w3.org/2000/svg\" "+\
                          f"version=\"1.1\" width=\"{width}\" "+\
                          f"height=\"{height}\">\n")
                svg.write("<rect width=\"100%\" height=\"100%\" "+\
                          f"fill=\"white\"/>\n")

                # Draw aisle entry/exit points
                for j in range(num_aisles):
                    cx = aisle_center_x[j]
                    direction_up = (j % 2 == 0)  # even -> up, odd -> down
                    entry_y = top_y if direction_up else bottom_y
                    exit_y = bottom_y if direction_up else top_y
                    svg.write(f"<circle cx=\"{cx}\" cy=\"{entry_y}\" "+\
                              f"r=\"6\" fill=\"#333\"/>\n")
                    svg.write(f"<circle cx=\"{cx}\" cy=\"{exit_y}\" "+\
                              f"r=\"6\" fill=\"#333\"/>\n")

                # Draw racks (use coordinates from file or transformed)
                for rid, (cx, cy) in rack_centers.items():
                    x = cx - rack_w / 2.0
                    y = cy - rack_h / 2.0
                    circuits = rack_circuits.get(rid, [])
                    if len(circuits) == 0:
                        svg.write(f"<rect x=\"{x}\" y=\"{y}\" "+\
                                  f"width=\"{rack_w}\" height=\"{rack_h}\" "+\
                                  f"fill=\"white\" stroke=\"black\" "+\
                                  f"stroke-width=\"1\"/>\n")
                    elif len(circuits) == 1:
                        fill = color_for_index(int(circuits[0]))
                        svg.write(f"<rect x=\"{x}\" y=\"{y}\" "+\
                                  f"width=\"{rack_w}\" height=\"{rack_h}\" "+\
                                  f"fill=\"{fill}\" stroke=\"black\" "+\
                                  f"stroke-width=\"1\"/>\n")
                    else:
                        c1 = color_for_index(int(circuits[0]))
                        c2 = color_for_index(int(circuits[1]))
                        svg.write(f"<rect x=\"{x}\" y=\"{y}\" "+\
                                f"width=\"{rack_w/2.0}\" height=\"{rack_h}\" "+\
                                f"fill=\"{c1}\" stroke=\"black\" "+\
                                f"stroke-width=\"1\"/>\n")
                        svg.write(f"<rect x=\"{x + rack_w/2.0}\" y=\"{y}\" "+\
                                f"width=\"{rack_w/2.0}\" height=\"{rack_h}\" "+\
                                f"fill=\"{c2}\" stroke=\"black\" "+\
                                f"stroke-width=\"1\"/>\n")
                    svg.write(f"<text x=\"{cx}\" y=\"{cy + 4}\" "+\
                              f"font-size=\"12\" text-anchor=\"middle\" "+\
                              f"fill=\"black\">{rid}</text>\n")

                # Draw path for a specific order (serpentine across aisles)
                k = order_to_draw
                order = inst.orders[k]  # Only first order for clarity
                stroke = color_for_index(k)
                stroke_w = 2.0
                prev_exit = None
                for j in range(num_aisles):
                    cx = aisle_center_x[j]
                    direction_up = (j % 2 == 0)
                    entry_y = top_y if direction_up else bottom_y
                    exit_y = bottom_y if direction_up else top_y
                    entry_pt = (cx, entry_y)
                    exit_pt = (cx, exit_y)

                    # Link previous aisle exit to current entry
                    if prev_exit is not None:
                        svg.write(
                        f"<line x1=\"{prev_exit[0]}\" y1=\"{prev_exit[1]}\" "+\
                        f"x2=\"{entry_pt[0]}\" y2=\"{entry_pt[1]}\" "+\
                        f"stroke=\"{stroke}\" stroke-width=\"{stroke_w}\" "+\
                         "opacity=\"0.6\"/>\n"
                        )

                    # Collect visit points (racks in this aisle holding 
                    #                       products of the order)
                    aisle_racks_set = set([r for r in aisles[j] \
                        if r in rack_centers and r not in (0, num_racks - 1)])
                    visit_points = []
                    for prod in order:
                        try:
                            rid = int(sol._positions[prod])
                        except Exception:
                            continue
                        if rid in aisle_racks_set:
                            pt = rack_centers.get(rid)
                            if pt is not None:
                                visit_points.append(pt)

                    # Sort by vertical traversal according to S-PATH
                    if len(visit_points) > 0:
                        if direction_up:
                            # Traverse from top to bottom (increasing y)
                            visit_points.sort(key=lambda p: p[1])
                        else:
                            # Traverse from bottom to top (decreasing y)
                            visit_points.sort(key=lambda p: p[1], reverse=True)

                        # entry -> racks -> exit
                        last = entry_pt
                        for pt in visit_points:
                            svg.write(
                                f"<line x1=\"{last[0]}\" y1=\"{last[1]}\" "+\
                                f"x2=\"{pt[0]}\" y2=\"{pt[1]}\" "+\
                                f"stroke=\"{stroke}\" "+\
                                f"stroke-width=\"{stroke_w}\" "+\
                                f"opacity=\"0.8\"/>\n"
                            )
                            last = pt
                        svg.write(
                            f"<line x1=\"{last[0]}\" y1=\"{last[1]}\" "+\
                            f"x2=\"{exit_pt[0]}\" y2=\"{exit_pt[1]}\" "+\
                            f"stroke=\"{stroke}\" "+\
                            f"stroke-width=\"{stroke_w}\" "+\
                            f"opacity=\"{0.8}\"/>\n"
                        )
                    else:
                        # Aisle traversed without visiting racks
                        svg.write(
                        f"<line x1=\"{entry_pt[0]}\" y1=\"{entry_pt[1]}\" "+\
                        f"x2=\"{exit_pt[0]}\" y2=\"{exit_pt[1]}\" "+\
                        f"stroke=\"{stroke}\" "+\
                        f"stroke-width=\"{stroke_w}\" "+\
                        f"opacity=\"{0.35}\" stroke-dasharray=\"4 3\"/>\n"
                        )

                    prev_exit = exit_pt

                # SVG end
                svg.write("</svg>\n")

            return True
        except Exception:
            return False