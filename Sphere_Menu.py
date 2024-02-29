from ursina import *
from Utility import *
from Geometries import Sphere

def get_cube_info(circle_x, circle_y, circle_z, circle_r, epsilon):
    return {
        "radius": num_from_text(circle_r),
        "center": (num_from_text(circle_x), num_from_text(circle_y), num_from_text(circle_z)),
        "epsilons": (num_from_text(epsilon), num_from_text(epsilon), num_from_text(epsilon))
        }

def create_menu():
    menu = Entity(parent = camera.ui)

    # X input
    Text(
        text = "X: ",
        position=(0.6, 0.475),
        parent = menu
    )
    circle_x = InputField(
        text="0",
        position=(0.7, 0.475), 
        scale=(0.1, 0.05),
        parent = menu
    )

    # Y input
    Text(
        text = "Y: ",
        position=(0.6, 0.4),
        parent = menu
    )
    circle_y = InputField(
        text="0",
        position=(0.7, 0.4),
        scale=(0.1, 0.05),
        parent = menu
    )

    # Z input
    Text(
        text = "Z: ",
        position=(0.6, 0.325),
        parent = menu
    )
    circle_z = InputField(
        text="0",
        position=(0.7, 0.325),
        scale=(0.1, 0.05),
        parent = menu
    )

    # Radius Input
    Text(
        text = "Radius: ",
        position=(0.55, 0.25),
        parent = menu
    )
    circle_r = InputField(
        text="1",
        position=(0.7, 0.25),
        scale=(0.1, 0.05),
        parent = menu
    )

    # Epsilons Input
    Text(
        text = "Epsilon X: ",
        position=(0.5, 0.175),
        parent = menu
    )

    Ex = InputField(
        text="1",
        position=(0.7, 0.175),
        scale=(0.1, 0.05),
        parent = menu
    )

    Text(
        text = "Epsilon Y: ",
        position=(0.5, 0.1),
        parent = menu
    )
    Ey = InputField(
        text="1",
        position=(0.7, 0.1),
        scale=(0.1, 0.05),
        parent = menu
    )

    Text(
        text = "Epsilon Z: ",
        position=(0.5, 0.025),
        parent = menu
    )
    Ez = InputField(
        text="1",
        position=(0.7, 0.025),
        scale=(0.1, 0.05),
        parent = menu
    )

    button = Button(
        parent = menu,
        text = 'Spawn Sphere',
        color = color.azure,
        position = (0.7, -0.05),
        scale = (0.2, 0.05),
        on_click = lambda: Sphere(
            scale = num_from_text(circle_r),
            epsilons = (num_from_text(Ex), num_from_text(Ey), num_from_text(Ez)),
            position = (num_from_text(circle_x), num_from_text(circle_y), num_from_text(circle_z)),
            alpha = 0.5
        )
    )

    return menu