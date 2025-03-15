# %%

import matplotlib.pyplot as plt

from fluxy.design import Design, HoleZone
from fluxy.design.util import plot_shapely_geometry

design = Design("examples/test.oas")


zone = HoleZone(
    design,
    circuit_layers=[1, 2],
    circuit_margin=10,
    exclusion_layers=[6],
)
zone.create_holes(
    hole_layer=3,
    hole_zone_layer=5,
    grid_size=6,
    hole_size=2,
)

plot_shapely_geometry(zone.exclusion_zone)
plt.show()

design.save("examples/test_holed.oas")

# %%

# from fluxy.design import Design, HoleZone

# design = Design("../../test.oas")
