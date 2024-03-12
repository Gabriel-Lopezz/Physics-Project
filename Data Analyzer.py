from typing import List
import numpy as np
import pandas as pd
from Geometries import FieldCube, Point, Sphere
from Utility import *
from ursina import *
import Sphere_Menu
import math

##############################################################
### USER
### INPUTS
### HERE

### File Name Here
file_name = "perm_matrix.csv"

##############################################################

dataframe = pd.read_csv(file_name)

# Set minimums and maximums and x,y,z points
StoredValues.min_epsilon = dataframe["Ex"][0]
StoredValues.max_epsilon = dataframe["Ex"][1]
x_points = int(dataframe["x"][0])
y_points = int(dataframe["y"][0])
z_points = int(dataframe["z"][0])

# Drop first two "min" and 'max" rows
dataframe = dataframe[2:]
dataframe = dataframe.reset_index(drop=True)
dataframe.head()

cube = FieldCube(dataframe)
# 3D Rendering
app = Ursina()

index = 0
camera.position = (0, 0, -30)

camera = EditorCamera()
camera.hotkeys['focus'] = "`" # Change hotkey for 'focus' from 'f' to '`' so that typing is less problematic

# Spawn small spheres to represent every datapoint 
for x in range(x_points):
    for y in range(y_points):
        for z in range(z_points):
            x = dataframe["x"][index]
            y = dataframe["y"][index]
            z = dataframe["z"][index]
            
            Ex = dataframe["Ex"][index]
            Ey = dataframe["Ey"][index]
            Ez = dataframe["Ez"][index]

            position = (x, y, z)
            
            epsilons = (Ex, Ey, Ez)

            point = Point(
                add_to_scene_entities=True,
                epsilons = epsilons,
                position = position,
                parent = scene,
                origin_y = 0,
                origin_x = 0,
                origin_z = 0,
                scale = 0.25,
                alpha = 0.3
            )

            # Add Epsilon x,y,z attributes
            # Check if this is necessary!

            index += 1

# Open Sphere menu
menu = Entity()
menu_type = str()

# Store last pressed object
prev_highlighted_obj = None
highlighted_obj = None

# Input handler
def input(key):
    global menu
    global menu_type
    global prev_highlighted_obj
    global highlighted_obj

    print("key: " + key)
    match key:
        case "s":
            destroy(menu) # VSCode gives a warning in Python 3.12.2; but works fine

            if menu_type == "sphere":
                menu_type = str()
            else:
                menu = Sphere_Menu.create_menu()
                menu_type = "sphere"
        case "delete":
            if isinstance(highlighted_obj, Sphere):
                destroy(highlighted_obj)

app.run()