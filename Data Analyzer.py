from typing import List
import numpy as np
import pandas as pd
from Geometries import FieldCube, Point, FieldObject
from Utility import *
from ursina import *
import Sphere_Menu
import math

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

StoredValues.min_epsilon = min_epsilon
StoredValues.max_epsilon = max_epsilon

dataframe = pd.read_csv(file_name)

cube = FieldCube(dataframe)

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
            point.epsilons = epsilons

            index += 1

# Open Sphere menu
menu = Entity()
menu_type = str()

update_loop = []

# Input handler
def input(key):
    global menu
    global menu_type

    if key == "s":
        destroy(menu) # VSCode gives a warning in Python 3.12.2; but works fine

        if menu_type == "sphere":
            menu_type = str()
        else:
            menu = Sphere_Menu.create_menu()
            menu_type = "sphere"
    
    if key == "left mouse down":
        if mouse.world_point and mouse.hovered_entity: # If user clicked on a permeable geometry
            ent = mouse.hovered_entity

            if isinstance(ent, FieldObject): # If entity has permeability geometry
                print("Position: ", ent.position, "  | Epsilons: ", ent.epsilons)
            else:
                print("Nonpermeable| Position: ", ent.position)

app.run()