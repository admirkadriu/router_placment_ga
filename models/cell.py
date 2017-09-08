import math


class Cell:
    cells_map = {}

    @classmethod
    def get(cls, i, j):
        key = str(i) + "," + str(j)
        if key in cls.cells_map:
            return Cell.cells_map[key]

        cell = cls(i, j)
        cls.cells_map[key] = cell
        return cell

    def __init__(self, i, j):
        self.i = i
        self.j = j
        self.id = str(self.i) + "," + str(self.j)
        self.distance_to_backbone = None
        self.type = None
        self.covered_cells = None

    def get_type(self):
        if self.type is None:
            from models.building import Building
            self.type = Building.planimetry[self.i][self.j]
        return self.type

    def get_distance_to_cell(self, cell):
        distance = math.sqrt((self.i - cell.i) ** 2 + (self.j - cell.j) ** 2)
        return distance

    def get_distance_to_backbone(self):
        if self.distance_to_backbone is None:
            from models.building import Building
            self.distance_to_backbone = self.get_distance_to_cell(Building.back_bone_cell)
        return self.distance_to_backbone
