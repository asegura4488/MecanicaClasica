

from vpython import *

scene = canvas(
    title="Mi primera simulación 3D",
    width=800,
    height=500,
    background=color.white
)

esfera = sphere(
    pos=vector(0,0,0),
    radius=1,
    color=color.blue
)

while True:
    rate(60)
    esfera.rotate(
        angle=0.02,
        axis=vector(0,1,0),
        origin=vector(0,0,0)
    )


