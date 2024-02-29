from Utility import *
from ursina import Entity, Draggable, mouse, clamp


def spawn_movers(entity: Entity) -> tuple[Entity, Entity, Entity]:
    x_mover = Draggable(
        parent = entity,
        position = right(scalar=entity.scale),
        lock = up(),
        world_rotation = (0, 0, 0),
        model = "arrow",
        collider = "arrow"
    )

    y_mover = Draggable(
        parent = entity,
        position = up(scalar=entity.scale),
        lock = right(),
        world_rotation = (0, 0, -90),
        model = "arrow",
        collider = "arrow"
    )

    z_mover = Draggable(
        parent = entity,
        position = forward(scalar=entity.scale),
        world_rotation = (0, 90, 0),
        model = "arrow",
        collider = "arrow"
    )

    # Override Draggable update function to work for z axis
    def z_mover_update(z_mover):
        if z_mover.dragging:
            if mouse.world_point:
                z_mover.world_z = mouse.world_point[0] - z_mover.start_offset[0]
                
            if z_mover.step[0] > 0:
                hor_step = 1/z_mover.step[0]
                z_mover.x = round(z_mover.x * hor_step) /hor_step
            if z_mover.step[1] > 0:
                ver_step = 1/z_mover.step[1]
                z_mover.y = round(z_mover.y * ver_step) /ver_step
            if z_mover.step[2] > 0:
                dep_step = 1/z_mover.step[2]
                z_mover.z = round(z_mover.z * dep_step) /dep_step

        z_mover.position = (
            clamp(z_mover.x, z_mover.min_x, z_mover.max_x),
            clamp(z_mover.y, z_mover.min_y, z_mover.max_y),
            clamp(z_mover.z, z_mover.min_z, z_mover.max_z)
        )

    z_mover.update = lambda: z_mover_update(z_mover)
    

    return (x_mover, y_mover, z_mover)
