from vpython import *

scene = canvas(
    title="Mi primera simulación",
    width=800,
    height=500,
    background=color.white
)

caja = box(
    pos=vector(0, 0, 0),
    size=vector(2, 1, 1),
    color=color.blue
)

while True:
    rate(60)

    caja.rotate(
        angle=0.02,
        axis=vector(0, 0, 1),
        origin=vector(0, 0, 0)
    )
