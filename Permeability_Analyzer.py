from typing import List
import numpy as np
import pandas as pd
from Geometries import PermeabilityCube, Sphere
from Utility import *
from ursina import *
import Sphere_Menu

##############################################################
### END 
### USER
### INPUTS
### HERE

### File Name Here
file_name = "perm_matrix.csv"

### epsilon max value here
max_epsilon = 100
### epsilon min value here
min_epsilon = 0
##############################################################

StoredVals.min_epsilon = min_epsilon
StoredVals.max_epsilon = max_epsilon

dataframe = pd.read_csv(file_name)

cube = PermeabilityCube(dataframe)

# 3D Rendering
app = Ursina()

length = int(math.cbrt(len(dataframe)))

index = 0
camera.position = (0, 0, -30)

camera = EditorCamera()
camera.hotkeys['focus'] = "`" # Change hotkey for 'focus' from 'f' to '`' so that typing is less problematic

# Spawn small spheres to represent every datapoint 
for x in range(length):
    for y in range(length):
        for z in range(length):
            x = dataframe["x"][index]
            y = dataframe["y"][index]
            z = dataframe["z"][index]
            
            Ex = dataframe["Ex"][index]
            Ey = dataframe["Ey"][index]
            Ez = dataframe["Ez"][index]

            position = (x, y, z)
            point_color = color_from_permeability(min_epsilon, max_epsilon, (Ex, Ey, Ez))

            ent = Entity(
                model ="sphere",
                color = point_color,
                position = position,
                parent = scene,
                origin_y = 0,
                origin_x = 0,
                origin_z = 0,
                scale = 0.25,
                alpha = 0.25
            )

            index += 1

# Open Sphere menu
menu = Entity()
menu_type = str()

# Input handler
def input(key):
    global menu
    global menu_type

    if key == "f":
        destroy(menu)

        if menu_type == "sphere":
            menu_type = str()
        else:
            menu = Sphere_Menu.create_menu()
            menu_type = "sphere"

app.run()