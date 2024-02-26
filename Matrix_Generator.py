from os.path import isfile
import csv
import pandas as pd
import numpy as np

### NAME FILE HERE (do NOT include .csv)
file_name = "perm_matrix"

### DEFINE NUMBER OF POINTS HERE
# This will be how many permeability datapoints are in each axis
x_points = 10
y_points = 10
z_points = 10

### DEFINE DIMENSIONS HERE
# This is how far the cube is from the origin in each axis
# Ex: An 'x_length' of 10 means bounds in x in matrix are ±5
x_distance = 5
y_distance = 5
z_distance = 5

### DEFINE VALUE RANGE HERE (LOWEST AND HIGHEST EPSLION VALUES)
range_min = 0
range_max = 100

# Ensure we're not overriding another file
if isfile(file_name + ".csv"):
    raise Exception("! Please use an available file name")

# Get random 4D array: first x, then y, then z, then our epsilon values
# range_min is minimum value returned; range_max is max value returned; size is dimensions of array
value_matrix = np.random.uniform(low=range_min, high=range_max, size=(x_points, y_points, z_points, 3))

# Get all positions into an array of tuples centered about the origin
positions = []
indices = []

x_coords = np.linspace(-x_distance, x_distance, x_points)
y_coords = np.linspace(-y_distance, y_distance, y_points)
z_coords = np.linspace(-z_distance, z_distance, z_points)

for x, x_index in enumerate(x_coords):
    for y, y_index in enumerate(y_coords):
        for z, index in enumerate(z_coords):
            positions += [(x,y,z)]
            indices += [(x_index, y_index, index)]

# `data_rows` will be the array we dump our positions and values into
data_rows = []

for index, position in zip(positions, indices):
    # Get positions
    x, y, z = position[0], position[1], position[2]
    x_index, y_index, z_index = index[0], index[1], index[2]

    values = value_matrix[x_index][y_index][z_index]

    Ex, Ey, Ez = values[0], values[1], values[2]

    # Rounding for simplicity
    Ex, Ey, Ez = round(Ex, 2), round(Ey, 2), round(Ez, 2)

    data_rows += [{"x": x, "y": y, "z": z, "Ex": Ex, "Ey": Ey, "Ez": Ez, "x_index": x_index, "y_index": y_index, "z_index": z_index}]

# Create `file_name`.csv file and write our data
with open(file_name+".csv", mode='w') as file:
    headers = ["x", "y", "z", "Ex", "Ey", "Ez", "x_index", "y_index", "z_index"]
    writer = csv.DictWriter(file, fieldnames=headers)
    writer.writeheader()

    writer.writerows(data_rows)

# Here is to test what it looks like as a pandas Dataframe
df = pd.read_csv(file_name + '.csv')