import random

from enums.CellType import CellType
from models.building import Building
from models.cell import Cell
from redis_provider import RedisProvider


class Router:
    radius = 0
    unit_cost = 0

    @classmethod
    def at_position(cls, i, j):
        router = cls(Cell.get(i, j))
        return router

    @classmethod
    def at_random_target(cls):
        random_key = random.choice(list(Building.target_cells))
        router = cls(Building.target_cells[random_key])
        return router

    @classmethod
    def n_at_random_target(cls, n):
        routers = []
        allowed_cells = dict(Building.target_cells)
        while len(routers) < n:
            random_key = random.choice(list(allowed_cells))
            router = cls(allowed_cells[random_key])
            routers.append(router)
            del allowed_cells[random_key]

        return routers

    @classmethod
    def n_at_random_target_clever(cls, n):
        routers = []
        allowed_cells = dict(Building.target_cells)
        while len(routers) < n and len(allowed_cells) > 0:
            random_key = random.choice(list(allowed_cells))
            router = cls(allowed_cells[random_key])
            routers.append(router)
            del allowed_cells[random_key]
            covered_cells = router.get_target_cells_covered()
            for i, cell in enumerate(covered_cells):
                allowed_cells.pop(cell.id, None)

        return routers

    def __init__(self, cell):
        self.cell = cell

    def covers_cell(self, cell):
        return self.cell.is_visible_by(cell)

    def get_target_cells_covered(self):
        if self.cell.covered_cells is None:
            self.cell.covered_cells = RedisProvider.get(self.cell.id)
            if self.cell.covered_cells is None:
                self.cell.covered_cells = []

                top = self.cell.i - self.radius
                if top < 0:
                    top = 0

                bottom = self.cell.i + self.radius
                if bottom >= Building.row_count:
                    bottom = Building.row_count - 1

                left = self.cell.j - self.radius
                if left < 0:
                    left = 0

                right = self.cell.j + self.radius
                if right >= Building.column_count:
                    right = Building.column_count - 1

                for i in range(top, bottom + 1):
                    for j in range(left, right + 1):
                        cell = Cell.get(i, j)
                        if cell.get_type() == CellType.TARGET.value and self.covers_cell(cell):
                            self.cell.covered_cells.append(cell)

                RedisProvider.set(self.cell.id, self.cell.covered_cells)

        return self.cell.covered_cells

    def get_best_path(self, connected_cells):
        nearest_cell = Building.back_bone_cell
        nearest_cell_distance = self.cell.get_distance_to_cell(Building.back_bone_cell)
        for cell in connected_cells:
            current_cell_distance = self.cell.get_distance_to_cell(cell)
            if current_cell_distance < nearest_cell_distance:
                nearest_cell = cell
                nearest_cell_distance = current_cell_distance

        return self.get_path(nearest_cell)

    def get_path(self, connected_cell):
        cells = []
        i = connected_cell.i
        j = connected_cell.j
        while self.cell.i != i or self.cell.j != j:
            if i == self.cell.i:
                if j < self.cell.j:
                    cells.append(Cell.get(i, j + 1))
                else:
                    cells.append(Cell.get(i, j - 1))
            elif j == self.cell.j:
                if i < self.cell.i:
                    cells.append(Cell.get(i + 1, j))
                else:
                    cells.append(Cell.get(i - 1, j))
            elif j < self.cell.j:
                if i < self.cell.i:
                    cells.append(Cell.get(i + 1, j + 1))
                else:
                    cells.append(Cell.get(i - 1, j + 1))
            else:
                if i < self.cell.i:
                    cells.append(Cell.get(i + 1, j - 1))
                else:
                    cells.append(Cell.get(i - 1, j - 1))

            i = cells[-1].i
            j = cells[-1].j

        return cells
