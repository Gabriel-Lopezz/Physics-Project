from ursina import color, Color, Text, vec3

class StoredValues:
    min_epsilon = None
    max_epsilon = None

class ValuePoint:
    position: tuple[float, float, float]
    epsilons: tuple[float, float, float]

    def __init__(self, position, epsilons):
        self.position = position
        self.epsilons = epsilons

def try_float(a) -> float:
    try:
        return float(a)
    except:
        pass

def num_from_text(text: Text) -> float:
    try:
        return try_float(text.text)
    except:
        print("Please ensure Text Fields are in numbers")

# Get the interpolation factor for 'p' between two 'start' and 'end'
def lerp_factor(start: float, end: float, p: float):
    return (p - start) / (end - start)

def lerp(a: float, b: float, t: float):
    return a + t * (b - a)

def lerp_points(start: ValuePoint, end: ValuePoint, point: tuple[float, float, float], axis: str) -> ValuePoint:
    # Determine index of specified axis
    ind = 0

    a = start.position
    epsilon_a = start.epsilons

    b = end.position
    epsilon_b = end.epsilons
    
    if axis == "y":
        ind = 1
    elif axis == "z":
        ind = 2
    elif axis != "x":
        raise Exception("Please input 'x', 'y', or 'z' as your axis.")
    
    # Get interpolation factor
    t = lerp_factor(a[ind], b[ind], point[ind])

    # Result is just point 'p' with lerped epsilon value at specified axis
    x = lerp(a[0], b[0], t)
    y = lerp(a[1], b[1], t)
    z = lerp(a[2], b[2], t)
    result_pos = (x, y, z)

    epsilon_x = lerp(epsilon_a[0], epsilon_b[0], t)
    epsilon_y = lerp(epsilon_a[1], epsilon_b[1], t)
    epsilon_z = lerp(epsilon_a[2], epsilon_b[2], t)
    result_epsilon = (epsilon_x, epsilon_y, epsilon_z)

    return ValuePoint(result_pos, result_epsilon)

# We will use color to describe permeability in each direction (x, y, z)
# Ɛx determines redness, Ɛy determines greenness, Ɛz determines blueness
def color_from_epsilons(min_epsilon: float, max_epsilon: float, epsilons: tuple[float, float, float]) -> Color:
    # Get how big the permeability is in each direction relative to the min and max epsilons
    Ex = lerp_factor(min_epsilon, max_epsilon, epsilons[0])
    Ey = lerp_factor(min_epsilon, max_epsilon, epsilons[1])
    Ez = lerp_factor(min_epsilon, max_epsilon, epsilons[2])

    # 255 is the max RGB component value
    redness = Ex * 255
    greenness = Ey * 255
    blueness = Ez * 255

    point_color = color.rgb(redness, greenness, blueness)

    return point_color

class Vector3:
    x: float
    y: float
    z: float

    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z
    # Vectors as tuple
    def right(scalar: float = 1):
        return (scalar, 0, 0)

    def left(scalar: float = 1):
        return (-scalar, 0, 0)

    def up(scalar: float = 1):
        return (0, scalar, 0)

    def down(scalar: float = 1):
        return (0, -scalar, 0)

    def forward(scalar: float = 1):
        return (0, 0, scalar)

    def backwards(scalar = 1):
        return (0, 0, -scalar)