import pandas as pd
import numpy as np
from numpy import typing
from ursina import Entity, scene, ursinamath
from Utility import *
import math

class Shape:
    epsilon: float

    def permeability_at_point(self) -> float:
        return self.epsilon
    def is_out_of_range(self, val, min, max) -> bool:
            return val < min or val > max

class PermeabilityCube(Shape):
    coord_min: float # Least value for a coordinate in any given axis
    coord_max: float # Greatest value for a coordinate in any given axis

    possible_coords: list # List of all possible coordinate values for any given axis

    points_list: np.typing.NDArray
    pos_to_val: dict[tuple[float, float, float], tuple[float, float, float]] # Dict that inputs and outputs tuples (x,y,z) -> (Ex, Ey, Ez)

    def __init__(self, data: pd.DataFrame) -> None:
        final = len(data) - 1 # Gets last index of dataframe

        self.coord_min = data["x"][0]
        self.coord_max = data["x"][final]
        
        self.points_list = pd.DataFrame.to_numpy(data)

        self.possible_coords = data["x"].unique()

        self.pos_to_val = {}

        for point in data.iterrows():
            point = point[1]

            x = point['x']
            y = point['y']
            z = point['z']
            
            Ex = point['Ex']
            Ey = point['Ey']
            Ez = point['Ez']

            position = (x, y, z)
            values = (Ex, Ey, Ez)

            self.pos_to_val[position] = values
    
    def permeability_at_point(self, x: int, y: int, z:int) -> float:
        if super().is_out_of_range(x, self.coord_min, self.coord_max) or super().is_out_of_range(y, self.coord_min, self.coord_max) or super().is_out_of_range(z, self.coord_min, self.coord_max):
            raise Exception("Please input a coordinate within the bounds of the shape")
        
        pc = self.possible_coords # Stored for simplicity and efficiency
        # Get index that out x, y, and z belong 
        si_x = np.searchsorted(pc, x) # Search index x
        si_y = np.searchsorted(pc, z) # Search index y
        si_z = np.searchsorted(pc, y) # Search index z

        # Trilinear Interpolation
        # Let P = (given x, given y, given z)
        P = (x, y, z)
        
        # Create point A - H to represent the cube that point P is enclosed in
        x1 = pc[si_x -1]
        x2 = pc[si_x]

        y1 = pc[si_y -1]
        y2 = pc[si_y]

        z1 = pc[si_z -1]
        z2 = pc[si_z]

        # Each point is an array holding [position, epsilon values]
        # Square 1
        A = ValuePoint((x1, y1, z1), self.pos_to_val[(x1, y1, z1)])
        B = ValuePoint((x2, y1, z1), self.pos_to_val[(x2, y1, z1)])
        C = ValuePoint((x1, y1, z2), self.pos_to_val[(x1, y1, z2)])
        D = ValuePoint((x2, y1, z2), self.pos_to_val[(x2, y1, z2)])

        # Square 2
        E = ValuePoint((x1, y2, z1), self.pos_to_val[(x1, y2, z1)])
        F = ValuePoint((x2, y2, z1), self.pos_to_val[(x2, y2, z1)])
        G = ValuePoint((x1, y2, z2), self.pos_to_val[(x1, y2, z2)])
        H = ValuePoint((x2, y2, z2), self.pos_to_val[(x2, y2, z2)])
        
        print(
            "A: ", A.position, " ", A.epsilons,
            "\nB: ", B.position, " ", B.epsilons,
            "\nC: ", C.position, " ", C.epsilons,
            "\nD: ", D.position, " ", D.epsilons,
            "\nE: ", E.position, " ", E.epsilons,
            "\nF: ", F.position, " ", F.epsilons,
            "\nG: ", G.position, " ", G.epsilons,
            "\nH: ", H.position, " ",  H.epsilons
        )

        xx1 = lerp_points(A, B, P, axis="x")
        print("XX1: ", xx1.epsilons)
        xx2 = lerp_points(C, D, P, axis="x")
        print("XX2: ", xx2.epsilons)
        xz1 = lerp_points(xx1, xx2, P, axis="z")
        print("XZ1: ", xz1.epsilons)

        xx3 = lerp_points(E, F, P, axis="x")
        print("XX3: ", xx3.epsilons)
        xx4 = lerp_points(G, H, P, axis="x")
        print("XX4: ", xx4.epsilons)
        xz2 = lerp_points(xx3, xx4, P, axis="z")
        print("XZ2: ", xz2.epsilons)

        result_point = lerp_points(xz1, xz2, P, axis="y")
        print("THIS IS THE RESULT POINT POSITION: ",
              "\nX: ", result_point.position[0],
              "\nY: ", result_point.position[1],
              "\nZ: ", result_point.position[2])
        
        result_epsilon = result_point.epsilons

        return result_epsilon




class Sphere(Shape):
    center: tuple[float, float, float]
    radius: float
    epsilons: tuple[float, float, float]
    pattern: str

    def __init__(self, radius: float, epsilon: float, center=(0,0,0), pattern="uniform") -> None:
        self.center = center
        self.radius = radius
        self.epsilon = epsilon

        if pattern not in ["uniform", "inverse", "inverse-squared"]:
            raise Exception("Please input a valid pattern")
        self.pattern = pattern
    
    def permeability_at_point(self, x, y, z) -> float:
        distance = math.sqrt(self.center, (x, y, z))

        if self.pattern == "uniform":
            return self.epsilon
        if self.pattern == "inverse":
            return self.epsilon / distance
        if self.pattern == "inverse-squared":
            return self.epsilon / distance**2
        
    def spawn_sphere(pos: tuple[float, float, float], radius: float, min_epsilon: float, max_epsilon: float, epsilons: tuple[float, float, float]):
        try:
            Entity(
                model = "sphere",
                parent = scene,
                position = pos,
                color = color_from_permeability(min_epsilon, max_epsilon, epsilons),
                scale = radius
            )
        except:
            print("Please ensure Text Fields are in numbers")

    
    # Later implement out of range method

class Traverser:
    start_pos: tuple[float, float, float]
    direction: tuple[float, float, float]
    speed: float
    update_per_unit: float

    def epsilons_after_time(self, time) -> list[float]:
        destination = self.start_pos + self.direction * self.speed * time
        updates = math.ceil(ursinamath.distance(self.start_pos, destination)) * updates_per_unit
