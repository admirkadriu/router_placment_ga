import math


class Cell:
    distance_map = {}

    def __init__(self, i, j):
        self.i = i
        self.j = j
        self.distance_to_backbone = None
        self.id = str(self.i) + "," + str(self.j)

    def get_type(self):
        from models.building import Building
        return Building.planimetry[self.i][self.j]

    def get_distance_to_cell(self, cell):
        key1 = self.id + '_' + cell.id
        key2 = cell.id + '_' + self.id
        if key1 in Cell.distance_map:
            return Cell.distance_map[key1]
        elif key2 in Cell.distance_map:
            return Cell.distance_map[key2]
        else:
            distance = math.sqrt((self.i - cell.i) ** 2 + (self.j - cell.j) ** 2)
            Cell.distance_map[key1] = distance
            return distance

    def get_distance_to_backbone(self):
        if self.distance_to_backbone is None:
            from models.building import Building
            self.distance_to_backbone = self.get_distance_to_cell(Building.back_bone_cell)
        return self.distance_to_backbone
