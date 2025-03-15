from shapely import Polygon, MultiPolygon
from shapely import buffer, union, intersection

from enum import Enum

from .design import Design


class GridType(Enum):
    TRIANGLE = 1
    SQUARE = 2


class HoleType(Enum):
    CIRCLE = 1
    SQUARE = 2


class HoleZone:
    def __init__(
        self,
        design: Design,
        circuit_layers: list[int],
        circuit_margin: float = 10.0,
        exclusion_layers: list[int] = [],
        subgrids: int = 25,
    ):
        self.design = design

        # Prepare a shapely geometry of all areas to avoid putting holes in.
        # Hole centers will not be placed inside these areas.

        exclusion_polygons = []
        for exclusion_layer in exclusion_layers:
            exclusion_polygons += design.get_polygons(exclusion_layer)
        exclusion_zone = MultiPolygon([(polygon, []) for polygon in exclusion_polygons])

        circuit_polygons = []
        for circuit_layer in circuit_layers:
            circuit_polygons += design.get_polygons(circuit_layer)
        circuit_exclusion_zone = MultiPolygon(
            [(polygon, []) for polygon in circuit_polygons]
        )
        circuit_exclusion_zone = buffer(circuit_exclusion_zone, distance=circuit_margin)

        self.exclusion_zone = union(exclusion_zone, circuit_exclusion_zone)

        # Cut up the exclusion zone into a square matrix of subgrids.
        # Each hole only has to check collision with elements in its subgrid,
        # leading to a massive performance improvement.

        x0, y0, x1, y1 = self.design.get_bounds()

        grid_x = abs(x1 - x0) / subgrids
        grid_y = abs(y1 - y0) / subgrids

        self.exclusion_zone_subgrids = [
            [
                # Cut out a square larger than the grid cell by 2*circuit_margin.
                # This makes sure that circuit elements at the edge of the neigbouring
                # cell are also checked for collisions.
                intersection(
                    Polygon(
                        [
                            (
                                x0 + grid_x * sx - circuit_margin,
                                y0 + grid_y * sy - circuit_margin,
                            ),
                            (
                                x0 + grid_x * (sx + 1) + circuit_margin,
                                y0 + grid_y * sy - circuit_margin,
                            ),
                            (
                                x0 + grid_x * (sx + 1) + circuit_margin,
                                y0 + grid_y * (sy + 1) + circuit_margin,
                            ),
                            (
                                x0 + grid_x * sx - circuit_margin,
                                y0 + grid_y * (sy + 1) + circuit_margin,
                            ),
                        ]
                    ),
                    self.exclusion_zone,
                )
                for sy in range(subgrids)
            ]
            for sx in range(subgrids)
        ]

        # Functions to determine in which subgrid a point is located.
        self.in_subgrid_x = lambda x: min(
            subgrids - 1, floor(subgrids * (x - x0) / w_tot)
        )
        self.in_subgrid_y = lambda y: min(
            subgrids - 1, floor(subgrids * (y - y0) / h_tot)
        )

    def create_holes(
        self,
        hole_layer: int,
        hole_zone_layer: int,
        grid_size: float = 5.0,
        hole_size: float = 1.0,
        grid_type: GridType = GridType.TRIANGLE,
        hole_type: HoleType = HoleType.CIRCLE,
    ):
        """Add holes to the design.

        Parameters
        ----------
        hole_layer : int
            Layer number to place the holes on.
        hole_zone_layer : int
            Layer that contains zones in which holes should be placed.
        grid_size : float, optional
            Distance between two neighbouring holes, by default 5.0
        hole_size : float, optional
            Size of a single hole, by default 1.0
        grid_type : GridType, optional
            Lattice of the hole grid, by default GridType.TRIANGLE
        hole_type : HoleType, optional
            Shape of the holes, by default HoleType.CIRCLE
        """
