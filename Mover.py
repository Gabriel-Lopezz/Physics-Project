from Utility import *
from ursina import Entity, Draggable, mouse, clamp, scene, Tooltip, camera

class Mover(Draggable):
    parent_offset: tuple[float, float, float]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.parent_offset = self.parent.position - self.position

        position = f"({round(self.parent.position[0], 3)}, {round(self.parent.position[1], 3)}, {round(self.parent.position[2], 3)})"
        epsilons = f"({round(self.parent.epsilons[0], 3)}, {round(self.parent.epsilons[1], 3)}, {round(self.parent.epsilons[2], 3)})"
        
        info = "(X, Y, Z):      " + position  + "\n(Ex, Ey, Ez): " + epsilons
        
        self.tooltip = Tooltip(info, wordwrap = 75)

    # Modified standard Draggable Update
    def update(self):
        if self.dragging:
            if mouse.world_point:
                if not self.lock[0]:
                    self.parent.world_x = mouse.world_point[0] - self.start_offset[0] + self.parent_offset[0]
                if not self.lock[1]:
                    self.parent.world_y = mouse.world_point[1] - self.start_offset[1] + self.parent_offset[1]
                if not self.lock[2]:
                    self.parent.world_z = mouse.world_point[2] - self.start_offset[2] + self.parent_offset[2]

            if self.step[0] > 0:
                hor_step = 1/self.parent.step[0]
                self.parent.x = round(self.parent.x * hor_step) / hor_step
            if self.step[1] > 0:
                ver_step = 1/self.parent.step[1]
                self.parent.y = round(self.parent.y * ver_step) / ver_step
            if self.step[2] > 0:
                dep_step = 1/self.parent.step[2]
                self.parent.z = round(self.parent.z * dep_step) / dep_step

        self.parent.position = (
            clamp(self.parent.x, self.min_x, self.max_x),
            clamp(self.parent.y, self.min_y, self.max_y),
            clamp(self.parent.z, self.min_z, self.max_z)
        )



def spawn_movers(entity: Entity) -> tuple[Entity, Entity, Entity]:
    x_mover = Mover(
        parent = entity,
        lock = Vector3.up(),
        world_position = Vector3.right(entity.scale[2] / 1.5), # Divide by two because scale 'x' is halved
        world_rotation = (0, 0, 0),
        scale = (0.5, 1, 1),
        model = "arrow",
        collider = "arrow",
        color = color.red
    )

    y_mover = Mover(
        parent = entity,
        lock = Vector3.right(),
        world_position = Vector3.up(entity.scale[2] / 1.5),
        world_rotation = (0, 0, -90),
        scale = (0.5, 1, 1),
        model = "arrow",
        collider = "arrow",
        color = color.green
    )

    z_mover = Mover(
        parent = entity,
        lock = (1, 1, 0),
        world_position = Vector3.forward(entity.scale[2] / 1.5),
        world_rotation = (0, -90, 0),
        scale = (0.5, 1, 1),
        plane_direction = (1, 1, 0),
        model = "arrow",
        collider = "arrow",
        color = color.blue
    )

    return (x_mover, y_mover, z_mover)

