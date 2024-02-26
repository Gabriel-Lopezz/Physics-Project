import pandas as pd
import numpy as np
from numpy import typing
import typing
import math
class ValuePoint:
    position: tuple[float, float, float]
    epsilons: tuple[float, float, float]

    def __init__(self, position, epsilons):
        self.position = position
        self.epsilons = epsilons

# Get the interpolation factor for 'p' between two 'a' and 'b'
def LerpFactor(a: float, b: float, p: float):
    return (p - a) / (b - a)

def Lerp(a: float, b: float, t: float):
    return a + t * (b - a)

def LerpPoints(A: ValuePoint, B: ValuePoint, P: tuple[float, float, float], axis: str) -> ValuePoint:
    # Determine index of specified axis
    ind = 0

    a = A.position
    epsilon_a = A.epsilons

    b = B.position
    epsilon_b = B.epsilons
    
    if axis == "y":
        ind = 1
    elif axis == "z":
        ind = 2
    elif axis != "x":
        raise Exception("Please input 'x', 'y', or 'z' as your axis.")
    
    # Get interpolation factor
    t = LerpFactor(a[ind], b[ind], P[ind])

    # Result is just point 'p' with lerped epsilon value at specified axis
    x = Lerp(a[0], b[0], t)
    y = Lerp(a[1], b[1], t)
    z = Lerp(a[2], b[2], t)
    result_pos = (x, y, z)

    epsilon_x = Lerp(epsilon_a[0], epsilon_b[0], t)
    epsilon_y = Lerp(epsilon_a[1], epsilon_b[1], t)
    epsilon_z = Lerp(epsilon_a[2], epsilon_b[2], t)
    result_epsilon = (epsilon_x, epsilon_y, epsilon_z)

    return ValuePoint(result_pos, result_epsilon)


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

        xx1 = LerpPoints(A, B, P, axis="x")
        print("XX1: ", xx1.epsilons)
        xx2 = LerpPoints(C, D, P, axis="x")
        print("XX2: ", xx2.epsilons)
        xz1 = LerpPoints(xx1, xx2, P, axis="z")
        print("XZ1: ", xz1.epsilons)

        xx3 = LerpPoints(E, F, P, axis="x")
        print("XX3: ", xx3.epsilons)
        xx4 = LerpPoints(G, H, P, axis="x")
        print("XX4: ", xx4.epsilons)
        xz2 = LerpPoints(xx3, xx4, P, axis="z")
        print("XZ2: ", xz2.epsilons)

        result_point = LerpPoints(xz1, xz2, P, axis="y")
        print("THIS IS THE RESULT POINT POSITION: ",
              "\nX: ", result_point.position[0],
              "\nY: ", result_point.position[1],
              "\nZ: ", result_point.position[2])
        
        result_epsilon = result_point.epsilons

        return result_epsilon




class Sphere(Shape):
    center: tuple[float, float, float]
    radius: float
    epsilon: float
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
    
    # Later implement out of range method