import pandas as pd
import numpy as np
from numpy import typing
from ursina import Entity, scene, ursinamath, Tooltip, Button, destroy, mouse
from Utility import *
import math
import Mover
import time
import threading

def is_out_of_range(val, min, max) -> bool:
        return val < min or val > max

class FieldObject(Button):
    epsilons: tuple[float, float, float]

    def __init__(self, add_to_scene_entities=True, **kwargs) -> None:
        self.epsilons = kwargs["epsilons"]
        kwargs["color"] = color_from_permeability(StoredValues.min_epsilon, StoredValues.max_epsilon, self.epsilons)
        
        if not "parent" in kwargs:
            kwargs["parent"] = scene

        super().__init__(add_to_scene_entities, **kwargs)

        self.alpha_setter(kwargs["alpha"]) # Alpha set afterwards; otherwise, won't work (but it should)
        self.tooltip = None # setting it to None for simple evaluation

    def permeability_at_point(self, position) -> tuple[float, float, float]:
        return self.epsilons
    
    def on_mouse_enter(self):
        if self.tooltip is None:
            position = f"({round(self.position[0], 3)}, {round(self.position[1], 3)}, {round(self.position[2], 3)})"
            epsilons = f"({round(self.epsilons[0], 3)}, {round(self.epsilons[1], 3)}, {round(self.epsilons[2], 3)})"

            info = "(X, Y, Z):      " + position  + "\n(Ex, Ey, Ez): " + epsilons

            self.tooltip = Tooltip(info, wordwrap = 75)

        # Waits for the user to have been on object for a second before opening tooltip menu
        def focus_object():
            time.sleep(1)

            if self.hovered:
                self.tooltip.enable()

        t = threading.Thread(target=focus_object)
        t.start()

    def on_mouse_exit(self):
        self.tooltip.disable()
        destroy(self.tooltip) # To save memory; already so many entities
        self.tooltip = None
    
class Point(FieldObject):
    def __init__(self, add_to_scene_entities=True, **kwargs) -> None:  
        super().__init__(
            add_to_scene_entities=add_to_scene_entities,
            model = "sphere", 
            collider = "sphere",
            **kwargs
        )

    def permeability_at_point(self) -> tuple[float, float, float]:
        return self.epsilons

class FieldCube():
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

class Sphere(FieldObject):
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

    def activate_movers(self):
        self.movers[0].enable()
        self.movers[1].enable()
        self.movers[2].enable()

    def deactivate_movers(self):
        self.movers[0].disable()
        self.movers[1].disable()
        self.movers[2].disable()

    def on_click(self):
        self.activate_movers()
    
    def input(self, key):
        is_mover_hovered = self.movers[0].hovered or self.movers[1].hovered or self.movers[2].hovered

        if key == "left mouse down" and not is_mover_hovered:
            self.deactivate_movers()
    
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

    def epsilons_after_time(self, time: float, cube: FieldCube) -> list[float]:
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