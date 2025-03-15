import numpy as np
import matplotlib.pyplot as plt

from matplotlib.path import Path
from matplotlib.patches import PathPatch
from matplotlib.collections import PatchCollection

import gdstk

from shapely.geometry import Point, Polygon, MultiPoint, MultiPolygon


def convert_gdstk_polygon(polygon: gdstk.Polygon) -> Polygon:
    """Convert gdstk Polygon to shapely Polygon.

    Parameters
    ----------
    polygon : gdstk.Polygon
        Polygon to convert.

    Returns
    -------
    Polygon
        Converted shapely Polygon.
    """
    return Polygon(polygon.points)


def plot_shapely_geometry(geometry, ax=None):
    """Debug function to visualize shapely objects.

    Parameters
    ----------
    geometry :
        Shapely object to visualize. Can be Point, MultiPoint, Polygon, or MultiPolygon.
    ax :
        Matplotlib axis to plot on, by default None.
        If None, generates a new figure and axis.

    Returns
    -------
    ax
        Matplotlib axis with the plotted geometry.
    """

    points_to_plot_x = []
    points_to_plot_y = []
    polygons_to_plot = []

    if type(geometry) is Point:
        points_to_plot_x.append(geometry.x)
        points_to_plot_y.append(geometry.y)
    elif type(geometry) is MultiPoint:
        for point in geometry.geoms:
            points_to_plot_x.append(point.x)
            points_to_plot_y.append(point.y)
    elif type(geometry) is Polygon:
        polygons_to_plot.append(geometry)
    elif type(geometry) is MultiPolygon:
        polygons_to_plot += geometry.geoms
    else:
        print(f"Cannot visualize unsupported type '{type(geometry)}'")

    if ax is None:
        _, ax = plt.subplots()

    ax.set_aspect("equal")

    if points_to_plot_x:
        ax.scatter(points_to_plot_x, points_to_plot_y, s=5, c="red")

    for polygon in polygons_to_plot:
        path = Path.make_compound_path(
            Path(np.asarray(polygon.exterior.coords)[:, :2]),
            *[Path(np.asarray(ring.coords)[:, :2]) for ring in polygon.interiors],
        )

        patch = PathPatch(path)
        collection = PatchCollection([patch])

        ax.add_collection(collection, autolim=True)
        ax.autoscale_view()

    return ax
