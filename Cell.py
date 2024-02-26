class Cell:
    epsilon_x: float
    epsilon_y: float
    epsilon_z: float

    def __init__(self, epsilon_x: float, epsilon_y: float, epsilon_z: float) -> None:
        self.epsilon_x = epsilon_x
        self.epsilon_y = epsilon_y
        self.epsilon_z = epsilon_z