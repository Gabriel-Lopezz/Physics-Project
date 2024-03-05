import pandas as pd
import numpy as np
from numpy import typing
from ursina import Entity, scene, ursinamath
from Utility import *
import math
import Mover

def is_out_of_range(val, min, max) -> bool:
        return val < min or val > max


class Permeable(Entity):
    epsilons: tuple[float, float, float]

    def __init__(self, add_to_scene_entities=True, **kwargs) -> None:
        self.epsilons = kwargs["epsilons"]
        kwargs["color"] = color_from_permeability(StoredValues.min_epsilon, StoredValues.max_epsilon, self.epsilons)

        super().__init__(add_to_scene_entities, **kwargs)

        self.alpha_setter(kwargs["alpha"]) # Alpha parameter was not working right

    def permeability_at_point(self, position) -> tuple[float, float, float]:
        return self.epsilons
    
class Point(Permeable):
    def __init__(self, add_to_scene_entities=True, **kwargs) -> None:  
        super().__init__(
            add_to_scene_entities=add_to_scene_entities,
            model = "sphere", 
            collider = "sphere",
            **kwargs
        )

    def permeability_at_point(self) -> tuple[float, float, float]:
        return self.epsilons


class PermeabilityCube():
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
    
    # Returns direcitonal values from trilinearly interpolating nearby values
    def values_at_point(self, x: int, y: int, z:int) -> float:
        if is_out_of_range(x, self.coord_min, self.coord_max) or is_out_of_range(y, self.coord_min, self.coord_max) or is_out_of_range(z, self.coord_min, self.coord_max):
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

        # ValuePoint holds position and directional values (epsilons)
        # Square 1
        A = ValuePoint(position = (x1, y1, z1), epsilons = self.pos_to_val[(x1, y1, z1)])
        B = ValuePoint(position = (x2, y1, z1), epsilons = self.pos_to_val[(x2, y1, z1)])
        C = ValuePoint(position = (x1, y1, z2), epsilons = self.pos_to_val[(x1, y1, z2)])
        D = ValuePoint(position = (x2, y1, z2), epsilons = self.pos_to_val[(x2, y1, z2)])

        # Square 2
        E = ValuePoint(position = (x1, y2, z1), epsilons = self.pos_to_val[(x1, y2, z1)])
        F = ValuePoint(position = (x2, y2, z1), epsilons = self.pos_to_val[(x2, y2, z1)])
        G = ValuePoint(position = (x1, y2, z2), epsilons = self.pos_to_val[(x1, y2, z2)])
        H = ValuePoint(position = (x2, y2, z2), epsilons = self.pos_to_val[(x2, y2, z2)])

        xx1 = lerp_points(start = A, end = B, point = P, axis = "x") # ValuePoint between A and B, AB
        xx2 = lerp_points(start = C, end = D, point = P, axis = "x") # ValuePoint between C and D, CD
        xz1 = lerp_points(start = xx1, end = xx2, point = P, axis = "z") # ValuePoint AB and CD, ABCD

        xx3 = lerp_points(start = E, end = F, point = P, axis = "x") # ValuePoint between E and F, EF
        xx4 = lerp_points(start = G, end = H, point = P, axis = "x") # ValuePoint between G and H, GH
        xz2 = lerp_points(start = xx3, end = xx4, point = P, axis = "z") # ValuePoint between EF and GH, EFGH

        result_point = lerp_points(start = xz1, end = xz2, point = P, axis = "y") # ValuePoint between ABCD and EFGH
        
        result_epsilon = result_point.epsilons

        return result_epsilon

class Sphere(Permeable):
    movers: tuple[Entity, Entity, Entity]
    pattern: str

    def __init__(self, pattern="uniform", add_to_scene_entities=True, **kwargs) -> None:
        super().__init__(
            add_to_scene_entities=add_to_scene_entities,
            model = "sphere", 
            collider = "sphere",
            **kwargs)

        if pattern not in ["uniform", "inverse", "inverse-squared"]:
            raise Exception("Please input a valid pattern")
        self.pattern = pattern

        self.movers = Mover.spawn_movers(self)
    
    def permeability_at_point(self, position: tuple[float, float, float]) -> tuple[float, float, float]:
        distance = math.sqrt(self.position, position)

        if self.pattern == "uniform":
            Ex = self.epsilons[0]
            Ey = self.epsilons[1]
            Ez = self.epsilons[2]

            return (Ex, Ey, Ez)
        
        if self.pattern == "inverse":
            Ex = self.epsilons[0] / distance
            Ey = self.epsilons[1] / distance
            Ez = self.epsilons[2] / distance

            return (Ex, Ey, Ez)
        
        if self.pattern == "inverse-squared":
            Ex = self.epsilons[0] / distance**2
            Ey = self.epsilons[1] / distance**2
            Ez = self.epsilons[2] / distance**2

            return (Ex, Ey, Ez)
        
    def spawn_sphere(self):
        ent = Entity(
            model = "sphere",
            collider= "sphere",
            parent = scene,
            position = self.center,
            color = color_from_permeability(StoredVals.min_epsilon, StoredVals.max_epsilon, self.epsilons),
            scale = self.radius
        )

        ent.geometry = self

    
    # Later implement out of range method

class Traverser:
    start_pos: tuple[float, float, float]
    direction: tuple[float, float, float]
    speed: float
    updates_per_unit: int

    def __init__(self, start_pos: tuple[float, float, float], direction: tuple[float, float, float], speed: float = 1, updates_per_unit:float = 5) -> None:
        self.start_pos = start_pos
        self.direction = direction
        self.speed = speed
        self.updates_per_unit = updates_per_unit

    def epsilons_after_time(self, time: float, cube: PermeabilityCube) -> list[float]:
        destination = self.start_pos + self.direction * self.speed * time
        updates = math.ceil(ursinamath.distance(self.start_pos, destination)) * self.updates_per_unit

        # Only applicable for 1D movement
        index = self.direction.index(1) # Get index where direction = 1

        epsilons = [cube.values_at_point(self.start_pos)]
        
        for update in range(updates):
            distance = (updates + 1) / self.updates_per_unit # +1 because we already counted starting position
            cur_point = self.start_pos + self.direction * distance

            epsilons += [cube.values_at_point(cur_point)]
        
        return epsilons