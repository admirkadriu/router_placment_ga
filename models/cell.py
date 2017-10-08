import math

from enums.CellType import CellType


class Cell:
    cells_map = {}

    @staticmethod
    def is_in_planimetry(i, j):
        from models.building import Building
        if 0 <= i < Building.row_count and 0 <= j < Building.column_count:
            return True

        return False

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
        self.position = (i, j)

    def get_type(self):
        if self.type is None:
            from models.building import Building
            self.type = Building.planimetry[self.i][self.j]
        return self.type

    def is_visible_by(self, cell):
        top = min(self.i, cell.i)
        bottom = max(self.i, cell.i)

        left = min(self.j, cell.j)
        right = max(self.j, cell.j)

        for i in range(top, bottom + 1):
            for j in range(left, right + 1):
                if Cell(i, j).get_type() == CellType.WALL.value:
                    return False

        return True

    def get_distance_to_cell(self, cell):
        distance = math.sqrt((self.i - cell.i) ** 2 + (self.j - cell.j) ** 2)
        return distance

    def get_distance_to_backbone(self):
        if self.distance_to_backbone is None:
            from models.building import Building
            self.distance_to_backbone = self.get_distance_to_cell(Building.back_bone_cell)
        return self.distance_to_backbone

    def get_path_to_cell(self, cell_to_connect):
        cells = {}
        i = cell_to_connect.i
        j = cell_to_connect.j
        while self.i != i or self.j != j:
            cell = None
            if i == self.i:
                if j < self.j:
                    cell = Cell.get(i, j + 1)
                else:
                    cell = Cell.get(i, j - 1)
            elif j == self.j:
                if i < self.i:
                    cell = Cell.get(i + 1, j)
                else:
                    cell = Cell.get(i - 1, j)
            elif j < self.j:
                if i < self.i:
                    cell = Cell.get(i + 1, j + 1)
                else:
                    cell = Cell.get(i - 1, j + 1)
            else:
                if i < self.i:
                    cell = Cell.get(i + 1, j - 1)
                else:
                    cell = Cell.get(i - 1, j - 1)

            cells[cell.id] = cell

            i = cell.i
            j = cell.j

        return cells

    def get_neighbors_cells(self, distance=1):
        neighbors_cells = []
        for i in range(self.i - distance, self.i + distance + 1):
            for j in range(self.j - distance, self.j + distance + 1):
                if not (i == self.i and j == self.j) and Cell.is_in_planimetry(i, j):
                    neighbors_cells.append(Cell.get(i, j))

        return neighbors_cells

    def get_nearest_cell(self, cells):
        nearest_cell = cells[0]
        nearest_cell_distance = self.get_distance_to_cell(cells[0])
        for cell in cells[1:]:
            current_cell_distance = self.get_distance_to_cell(cell)
            if current_cell_distance < nearest_cell_distance:
                nearest_cell = cell
                nearest_cell_distance = current_cell_distance

        return nearest_cell
