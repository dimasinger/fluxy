from math import floor, sqrt
import numpy as np

from shapely import buffer, union, intersection
from shapely.geometry import Point, Polygon, MultiPolygon

import gdstk

from enum import Enum

from .design import Design


class GridType(Enum):
    TRIANGLE = 1
    SQUARE = 2


class HoleType(Enum):
    CIRCLE = 1
    SQUARE = 2


def _generate_grid_points(
    bounds: tuple[float],
    grid_size: float,
    grid_type: GridType,
):
    x0, y0, x1, y1 = bounds
    w_tot = x1 - x0
    h_tot = y1 - y0

    if grid_type == GridType.TRIANGLE:
        x_center = x0 + w_tot / 2
        y_center = y0 + h_tot / 2

        imax = floor(w_tot / (2 * grid_size))
        jmax = floor(h_tot / (sqrt(3) * grid_size))
        grid_x = grid_size
        grid_y = sqrt(3) / 2 * grid_size

        for i in range(-imax, imax):
            for j in range(-jmax, jmax + 1):
                x = x_center + grid_x * i
                y = y_center + grid_y * j

                # offset every second row
                if j % 2 == 1:
                    x += grid_size / 2

                yield x, y

    elif grid_type == GridType.SQUARE:
        for x in np.arange(x0, x1, grid_size):
            for y in np.arange(y0, y1, grid_size):
                yield x, y

    else:
        raise ValueError(f"Unknown grid type: {grid_type}")


def _generate_hole_cell(
    hole_size: float,
    hole_type: HoleType,
    layer: int = 0,
) -> gdstk.Cell:
    if hole_type == HoleType.CIRCLE:
        hole = gdstk.ellipse(
            center=(0, 0),
            radius=hole_size / 2,
            layer=layer,
        )

    elif hole_type == HoleType.SQUARE:
        hole = gdstk.rectangle(
            corner1=(-hole_size / 2, -hole_size / 2),
            corner2=(hole_size / 2, hole_size / 2),
            layer=layer,
        )

    else:
        raise ValueError(f"Unknown hole type: {hole_type}")

    return gdstk.Cell(f"HOLE_{hole_type.name}_{hole_size:.1f}").add(hole)


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
        w_tot = abs(x1 - x0)
        h_tot = abs(y1 - y0)

        grid_x = w_tot / subgrids
        grid_y = h_tot / subgrids

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
        self.x_to_subgrid = lambda x: min(
            subgrids - 1, floor(subgrids * (x - x0) / w_tot)
        )
        self.y_to_subgrid = lambda y: min(
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

        hole_zone = MultiPolygon(self.design.get_polygons(hole_zone_layer))
        grid_points = _generate_grid_points(hole_zone.bounds, grid_size, grid_type)

        hole_cell = _generate_hole_cell(hole_size, hole_type)
        self.design.add(hole_cell)

        for xy in grid_points:
            point = Point(xy)
            if not hole_zone.contains(point):
                continue

            si = self.x_to_subgrid(xy[0])
            sj = self.y_to_subgrid(xy[1])
            subgrid = self.exclusion_zone_subgrids[si][sj]
            if subgrid.contains(point):
                continue

            self.design.add(gdstk.Reference(hole_cell, origin=xy))
