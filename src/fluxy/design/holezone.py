from shapely import MultiPolygon
from shapely import buffer, union

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

    def create_holes(
        self,
        hole_layer: int,
        hole_zone_layer: int,
        grid_size: float = 5.0,
        hole_radius: float = 1.0,
        grid_type: GridType = GridType.TRIANGLE,
        hole_type: HoleType = HoleType.CIRCLE,
    ): ...
