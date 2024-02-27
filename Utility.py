from ursina import color, Color, Text

class StoredVals:
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

# Get the interpolation factor for 'p' between two 'a' and 'b'
def lerp_factor(a: float, b: float, p: float):
    return (p - a) / (b - a)

def lerp(a: float, b: float, t: float):
    return a + t * (b - a)

def lerp_points(A: ValuePoint, B: ValuePoint, P: tuple[float, float, float], axis: str) -> ValuePoint:
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
    t = lerp_factor(a[ind], b[ind], P[ind])

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
def color_from_permeability(min_epsilon: float, max_epsilon: float, epsilons: tuple[float, float, float]) -> Color:
    # Get how big the permeability is in each direction relative to the min and max epsilons
    perm_x = lerp_factor(min_epsilon, max_epsilon, epsilons[0])
    perm_y = lerp_factor(min_epsilon, max_epsilon, epsilons[1])
    perm_z = lerp_factor(min_epsilon, max_epsilon, epsilons[2])

    # 255 is the max RGB component value
    redness = perm_x * 255
    greenness = perm_y * 255
    blueness = perm_z * 255

    point_color = color.rgb(redness, greenness, blueness)

    return point_color