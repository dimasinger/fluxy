import gdstk
from gdstk import Library

from shapely import Polygon


def _convert_gdstk_polygon(polygon: gdstk.Polygon) -> Polygon:
    return Polygon(polygon.points)


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
        if infile is None:
            self.library = Library()
        else:
            self.library = _load_design(infile)

        self._layer_cache = {}

    def save(self, outfile: str):
        _save_design(outfile, self.library)

    def get_polygons(self, layer: int) -> list[Polygon]:
        if layer not in self._layer_cache:
            polygons = []
            for top_cell in self.library.top_level():
                polygons += [
                    _convert_gdstk_polygon(polygon)
                    for polygon in top_cell.get_polygons(layer=layer, datatype=0)
                ]

            valid_polygons = [polygon for polygon in polygons if polygon.is_valid]
            self._layer_cache[layer] = valid_polygons

        return self._layer_cache[layer]
