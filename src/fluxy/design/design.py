import gdstk
from gdstk import Library

import shapely
from shapely import Polygon, MultiPolygon

from .util import convert_gdstk_polygon


def _load_design(infile: str):
    fileext = infile[-3:]
    if fileext == "oas":
        return gdstk.read_oas(infile)
    elif fileext == "gds":
        return gdstk.read_gds(infile)

    raise IOError(
        f"Unknown file type: {fileext}. Only supported file types are gds and oas."
    )


def _save_design(outfile: str, library: Library):
    fileext = outfile[-3:]
    if fileext == "oas":
        return library.write_oas(outfile)
    elif fileext == "gds":
        return library.write_gds(outfile)

    raise IOError(
        f"Unknown file type: {fileext}. Only supported file types are gds and oas."
    )


class Design:
    def __init__(
        self,
        infile: str | None = None,
    ):
        """Create or load a design.

        Parameters
        ----------
        infile : str | None, optional
            Path to the input file, by default None.
            If None, a new empty design is created.
        """
        if infile is None:
            self.library = Library()
        else:
            self.library = _load_design(infile)

        # select a top cell for added objects
        top_cells = self.library.top_level()
        self.top_cell = top_cells[0]
        if len(top_cells) > 1:
            print(f"Multiple top cells found. Using the the cell: {self.top_cell.name}")

    def save(self, outfile: str):
        """Save the design to a file.

        Parameters
        ----------
        outfile : str
            Path to the output file.
        """
        _save_design(outfile, self.library)

    def get_polygons(self, layer: int) -> list[Polygon]:
        """Return all polygons on a given layer.

        Parameters
        ----------
        layer : int
            Layer number.

        Returns
        -------
        list[Polygon]
            List of shapely Polygon objects representing the polygons on the given layer.
        """

        polygons = []
        for top_cell in self.library.top_level():
            polygons += [
                convert_gdstk_polygon(polygon)
                for polygon in top_cell.get_polygons(layer=layer, datatype=0)
            ]

        valid_polygons = [polygon for polygon in polygons if polygon.is_valid]
        return valid_polygons

    def get_all_polygons(self) -> list[Polygon]:
        """Return all polygons in the design.

        Returns
        -------
        list[Polygon]
            List of shapely Polygon objects representing the polygons.
        """

        polygons = []
        for top_cell in self.library.top_level():
            polygons += [
                convert_gdstk_polygon(polygon) for polygon in top_cell.get_polygons()
            ]
        return polygons

    def get_bounds(self):
        """Return the bounding box of the design.

        Returns
        -------
        tuple
            (minx, miny, maxx, maxy) of the bounding box.
        """

        polygons = self.get_all_polygons()
        return MultiPolygon(polygons).bounds

    def add(self, obj: gdstk.Cell | gdstk.Reference):
        """Add a cell or reference to the design.

        Parameters
        ----------
        obj : gdstk.Cell | gdstk.Reference
            Cell or reference to add.
        """

        if isinstance(obj, gdstk.Cell):
            self.library.add(obj)
        elif isinstance(obj, gdstk.Reference):
            self.top_cell.add(obj)
        else:
            raise TypeError(f"Object type {type(obj)} not supported.")
