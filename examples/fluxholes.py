# %%

from fluxy.design import Design, HoleZone

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
    hole_radius=2,
)

design.save("examples/test_holed.oas")

# %%

# from fluxy.design import Design, HoleZone

# design = Design("../../test.oas")
