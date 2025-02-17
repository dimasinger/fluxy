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
        circuit_layers: list[str],
    ):
        self.design = design

    def add_holes(
        self,
        layer: str,
        grid_size: float = 5.0,
        hole_size: float = 1.0,
        hole_margin: float = 5.0,
        grid_type: GridType = GridType.TRIANGLE,
        hole_type: HoleType = HoleType.CIRCLE,
    ): ...
