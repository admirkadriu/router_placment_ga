import random

import numpy as np
import scipy.spatial as spatial

from enums.CellType import CellType
from models.building import Building
from models.cell import Cell
from redis_provider import RedisProvider
from utils import Utils


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
        routers = {}
        while len(routers) < n:
            router = random.choice(Building.target_cells)
            if router.cell.id not in routers:
                routers[router.cell.id] = router

        return list(routers)

    @classmethod
    def n_at_random_target_clever(cls, n):
        routers = []
        used_cells = set()
        while len(routers) < n and (len(Building.target_cells) - len(used_cells) > 5):
            cell = random.choice(Building.target_cells)
            if cell.id not in used_cells:
                router = Router(cell)
                routers.append(router)
                used_cells.add(cell.id)

                covered_cells = router.get_target_cells_covered()
                for cell, key in enumerate(covered_cells):
                    cell = covered_cells[key]
                    used_cells.add(cell.id)

        return routers

    def __init__(self, cell):
        self.cell = cell

    def covers_cell(self, cell):
        return self.cell.is_visible_by(cell)

    def get_target_cells_covered(self):
        if self.cell.covered_cells is None:
            self.cell.covered_cells = RedisProvider.get(self.cell.id)
            if self.cell.covered_cells is None:
                self.cell.covered_cells = {}

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
                            self.cell.covered_cells[cell.id] = cell

                RedisProvider.set(self.cell.id, self.cell.covered_cells)

        return self.cell.covered_cells

    def get_best_path(self, connected_cells):
        tuples = Utils.get_cells_tuples(connected_cells)
        tuples.append(Building.back_bone_cell.position)
        points = np.array(tuples)
        point_tree = spatial.cKDTree(points)
        index = point_tree.query([self.cell.i, self.cell.j], 1)[1]
        nearest_cell = Cell.get(tuples[index][0], tuples[index][1])

        return self.cell.get_path_to_cell(nearest_cell)
