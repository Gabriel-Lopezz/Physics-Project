from Utility import *
from ursina import Entity, Draggable, mouse, clamp

def spawn_movers(entity: Entity) -> tuple[Entity, Entity, Entity]:
    x_mover = Draggable(
        parent = entity,
        lock = up(),
        world_position = forward(entity.scale[2] / 1.5), # Divide by two because scale 'x' is halved
        world_rotation = (0, 0, 0),
        scale = (0.5, 1, 1),
        model = "arrow",
        collider = "arrow"
    )

    y_mover = Draggable(
        parent = entity,
        lock = right(),
        world_position = forward(entity.scale[2] / 1.5),
        world_rotation = (0, 0, -90),
        scale = (0.5, 1, 1),
        model = "arrow",
        collider = "arrow"
    )

    z_mover = Draggable(
        parent = entity,
        world_position = forward(entity.scale[2] / 1.5),
        world_rotation = (0, -90, 0),
        scale = (0.5, 1, 1),
        plane_direction = (1, 0, 0),
        lock = (0, 1, 0),
        model = "arrow",
        collider = "arrow"
    )

    def move_entity(entity, mover, axis: str):

        new_pos: tuple[float, float, float]
        if axis.lower() == "x":
            new_scalar = mover.world_position[0] - entity.scale[0] / 1.5
            new_pos = (entity.position[0], new_scalar, entity.position[2])
        elif axis.lower() == "y":
            new_scalar = mover.world_position[1] - entity.scale[1] / 1.5
            new_pos = (entity.position[0], new_scalar, entity.position[2])
        elif axis.lower() == "z":
            new_scalar = mover.world_position[2] - entity.scale[2] / 1.5
            new_pos = (entity.position[0], entity.position[1], new_scalar)
        else:
            raise Exception("You did not input a valid Move_entity axis")

        entity.position = new_pos
        

    x_mover.start_dragging = lambda: move_entity(entity, x_mover, "x")
    y_mover.update = lambda: move_entity(entity, y_mover, "y")
    z_mover.update = lambda: move_entity(entity, z_mover, "z")
    
    return (x_mover, y_mover, z_mover)
