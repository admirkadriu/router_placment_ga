from random import randint

from models.building import Building
from models.cell import Cell


class Router:
    radius = 0
    unit_cost = 0

    @classmethod
    def at_position(cls, i, j):
        router = cls(Cell(i, j))
        return router

    @classmethod
    def at_random_target(cls):
        router = cls(Building.target_cells[randint(0, len(Building.target_cells) - 1)])
        return router

    @classmethod
    def n_at_random_target(cls, n):
        routers = []
        while len(routers) < n:
            router = cls(Building.target_cells[randint(0, len(Building.target_cells) - 1)])
            if not any(r for r in routers if r.cell.id == router.cell.id):
                routers.append(router)

        return routers

    def __init__(self, cell):
        self.cell = cell

    def covers_cell(self, cell):  # TODO: check if wall between router an cell
        return self.cell.get_distance_to_cell(cell) <= Router.radius

    def get_covered_cells(self):
        covered_cells = []
        for x in range(self.cell.i - self.radius, self.cell.i + self.radius + 1):
            for y in range(self.cell.j - self.radius, self.cell.j + self.radius + 1):
                cell = Cell(x, y)
                if x >= 0 and y >= 0 and self.covers_cell(cell):
                    covered_cells.append(cell)

        return covered_cells

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
                    cells.append(Cell(i, j + 1))
                else:
                    cells.append(Cell(i, j - 1))
            elif j == self.cell.j:
                if i < self.cell.i:
                    cells.append(Cell(i + 1, j))
                else:
                    cells.append(Cell(i - 1, j))
            elif j < self.cell.j:
                if i < self.cell.i:
                    cells.append(Cell(i + 1, j + 1))
                else:
                    cells.append(Cell(i - 1, j + 1))
            else:
                if i < self.cell.i:
                    cells.append(Cell(i + 1, j - 1))
                else:
                    cells.append(Cell(i - 1, j - 1))

            i = cells[-1].i
            j = cells[-1].j

        return cells
