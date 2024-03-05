from Utility import *
from ursina import Entity, Draggable, mouse, clamp, scene, Vec3, camera

def spawn_movers(entity: Entity) -> tuple[Entity, Entity, Entity]:
    parent_ent = Entity()
    entity.parent = parent_ent

    x_mover = Draggable(
        parent = scene,
        world_position = right(entity.scale[2] / 1.5), # Divide by two because scale 'x' is halved
        world_rotation = (0, 0, 0),
        scale = (0.5, 1, 1),
        model = "arrow",
        collider = "arrow"
    )

    y_mover = Draggable(
        parent = entity,
        lock = right(),
        world_rotation = (0, 0, -90),
        scale = (0.5, 1, 1),
        model = "arrow",
        collider = "arrow"
    )

    z_mover = Draggable(
        parent = entity,
        world_rotation = (0, -90, 0),
        scale = (0.5, 1, 1),
        plane_direction = (1, 0, 0),
        lock = (0, 1, 0),
        model = "arrow",
        collider = "arrow"
    )

    ''' move_entity function
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
    ''' 

    # Override movers' start_dragging and stop_dragging methods
    

    x_mover.start_dragging = lambda: x_mover.start_dragging()
    y_mover.start_dragging = lambda: x_mover.start_dragging()
    z_mover.start_dragging = lambda: x_mover.start_dragging()

    x_mover.stop_dragging = lambda: unassign_mover(entity, x_mover, parent_ent)
    y_mover.stop_dragging = lambda: unassign_mover(entity, y_mover, parent_ent)
    z_mover.stop_dragging = lambda: unassign_mover(entity, z_mover, parent_ent)
    
    return (x_mover, y_mover, z_mover)

