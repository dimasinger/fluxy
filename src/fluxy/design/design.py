import gdstk
from gdstk import Library


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

    def save(self, outfile: str):
        _save_design(outfile, self.library)
