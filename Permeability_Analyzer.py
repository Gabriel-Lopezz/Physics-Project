from typing import List
import numpy as np
import pandas as pd
from Geometries import PermeabilityCube, Lerp
from ursina import *

### File Name Here
file_name = "perm_matrix.csv"

dataframe = pd.read_csv(file_name)

cube = PermeabilityCube(dataframe)
'''
print(
    "Cells: " + str(len(dataframe)),
    "\nX min: " + str(cube.coord_min),
    "\nX max: " + str(cube.coord_max),
    "\nPossible Coords: " + str(cube.possible_coords)
    )
'''
print("\n-----------------\n")
print(cube.permeability_at_point(-3, 2.1, 2))
print(Lerp(0, 1, .5))

# 3D Rendering
app = Ursina()

length = int(math.cbrt(len(dataframe)))

index = 0
camera.position = (0, 0, -20)

camera = EditorCamera()

for x in range(length):
    for y in range(length):
        for z in range(length):
            ent = Entity(
                model="cube", color=color.white,
                position= (dataframe["x"][index], dataframe["y"][index], dataframe["z"][index]),
                parent=scene,
                origin_y=0,
                origin_x=0,
                origin_z=0,
                texture="Outline Texture.png"
            )
            
            print("pos: ", (dataframe["x"][index], dataframe["y"][index], dataframe["z"][index]))
            
            ent.scale = length/cube.coord_max * 0.5
            ent.alpha_setter(0.5)

            index += 1

# Create a button in the top right corner
button = Button(
    text='Click me!',
    color=color.azure,
    position=(0.8, 0.45),  # Adjust position to the top right
    scale=(0.1, 0.05),     # Adjust scale to make it smaller
    on_click=lambda: print('Button clicked!')
)
input_field = InputField(
    text='Type here...',
    position=(0.75, 0.4),  # Adjust position to the top right
    scale=(0.1, 0.05)     # Adjust scale to make it smaller
)
app.run()