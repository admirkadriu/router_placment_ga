import random
import time
from uuid import uuid4

from enums.CellType import CellType
from models.building import Building
from models.router import Router


class Solution:
    @classmethod
    def generate_feasible(cls):
        t0 = time.time()
        solution = cls()
        bulk_count = int(Building.infrastructure_budget / (Router.unit_cost * Building.back_bone_cost))

        routers = Router.n_at_random_target_clever(bulk_count)
        routers.sort(key=lambda r: r.cell.get_distance_to_backbone())  # TODO: insert only when i is %2

        can_add = True
        i = 0
        jump = 2
        while can_add and i < len(routers):
            router = routers[i]
            can_add = solution.add_router(router, False)

            i += jump

            if i >= len(routers):
                i = jump - 1
                jump = jump * 2

        t1 = time.time()
        print("Solution Generated: ", solution.is_feasible(), "\n-Time: ", t1 - t0)
        score = solution.get_score()
        t2 = time.time()
        print("-Score: ", score, "; Time: ", t2 - t1)
        return solution

    def __init__(self):
        self.id = uuid4()
        self.routers = []
        self.connected_cells = {}
        self.score = None
        self.scoreCalculationNeeded = True

    def connected_cells_count(self):
        return len(self.connected_cells)

    def routers_count(self):
        return len(self.routers)

    def is_feasible(self):
        return self.get_cost() <= Building.infrastructure_budget

    def get_score(self):
        if self.scoreCalculationNeeded:
            self.calc_score()
        return self.score

    def rename(self):
        self.id = uuid4()

    def get_cost(self):
        return self.routers_count() * Router.unit_cost + self.connected_cells_count() * Building.back_bone_cost

    def calc_score(self):
        budget_for_routers = self.routers_count() * Router.unit_cost
        budget_to_connect_routers = self.connected_cells_count() * Building.back_bone_cost

        remaining_budget_score = Building.infrastructure_budget - budget_for_routers - budget_to_connect_routers
        covered_cells_score = 1000 * len(Building.get_covered_cells(self.routers))

        self.score = covered_cells_score + remaining_budget_score
        self.scoreCalculationNeeded = False
        return self.score

    def set_routers(self, routers):
        r_dict = {}
        for r in routers:
            r_dict[r.cell.id] = r

        routers = list(r_dict.values())

        self.connected_cells = {}
        self.score = None
        self.scoreCalculationNeeded = True

        self.routers = routers
        self.reconnect_routers()

        while not self.is_feasible():
            random_router = random.choice(self.routers)
            self.remove_router(random_router)

        return

    def sort_routers(self):
        self.routers.sort(key=lambda r: r.cell.get_distance_to_backbone())
        return

    def add_router(self, router, sort=True):
        if router.cell.get_type() != CellType.TARGET.value:
            return False

        cells_to_connect = router.get_best_path(self.connected_cells)
        cost_to_add = len(cells_to_connect) * Building.back_bone_cost + Router.unit_cost

        if (self.get_cost() + cost_to_add) <= Building.infrastructure_budget:
            self.routers.append(router)
            self.connected_cells.update(cells_to_connect)
            if sort:
                self.sort_routers()
            self.scoreCalculationNeeded = True
            return True

        return False

    def remove_router(self, router):
        self.scoreCalculationNeeded = True
        for i, r in enumerate(self.routers):
            if r.cell.id == router.cell.id:
                del self.routers[i]
                if r.cell.id != Building.back_bone_cell.id:
                    self.connected_cells.pop(r.cell.id, None)
                    cells_to_connect = self.disconnect_neighbor_cells(r.cell, {})
                    self.connect_group_of_cells(cells_to_connect)
                break

    def connect_group_of_cells(self, cells):
        length = len(cells)
        if length > 1:
            connected_cells = {}
            for index, cell in enumerate(cells):
                if cell.id not in connected_cells:
                    nearest_cell = cell.get_nearest_cell(cells[0:index] + cells[(index + 1): length])
                    connected_cells[cell.id] = cell
                    connected_cells[nearest_cell.id] = nearest_cell
                    self.connected_cells.update(nearest_cell.get_path_to_cell(cell))

    def contains_router(self, cell):
        for i, r in enumerate(self.routers):
            if r.cell.id == cell.id:
                return True

        return False

    def disconnect_neighbor_cells(self, cell, checked_cells):
        cells_to_connect = []

        cells_to_check = cell.get_neighbors_cells()

        cells_to_check_dict = {}
        cells_to_remove = []

        for cell in cells_to_check:
            cells_to_check_dict[cell.id] = cell
            if cell.id not in checked_cells and (
                            cell.id in self.connected_cells or cell.id == Building.back_bone_cell.id):
                if (self.contains_router(cell) or cell.id == Building.back_bone_cell.id):
                    cells_to_connect.append(cell)
                else:
                    cells_to_remove.append(cell)

        checked_cells.update(cells_to_check_dict)

        for cell in cells_to_remove:
            self.connected_cells.pop(cell.id, None)
            cells_to_connect = cells_to_connect + self.disconnect_neighbor_cells(cell, checked_cells)

        return cells_to_connect

    def reconnect_routers(self):
        self.connected_cells = {}
        self.sort_routers()

        for router in self.routers:
            cells_to_connect = router.get_best_path(self.connected_cells)
            self.connected_cells.update(cells_to_connect)

        self.scoreCalculationNeeded = True
        return

    def split_routers_with_rectangle(self, top, left, width, height):
        bottom = top + height - 1
        right = left + width - 1

        inside = []
        outside = []
        for r in self.routers:
            if top <= r.cell.i <= bottom and left <= r.cell.j <= right:
                inside.append(r)
            else:
                outside.append(r)

        return [inside, outside]

    def get_inside_rectangle(self, top, left, width, height):
        bottom = top + height - 1
        right = left + width - 1

        inside = []
        for r in self.routers:
            if top <= r.cell.i <= bottom and left <= r.cell.j <= right:
                inside.append(r)

        return inside

    def get_midpoint(self):
        i_list = list(map(lambda router: router.cell.i, self.routers))
        j_list = list(map(lambda router: router.cell.j, self.routers))
        i_list.sort()
        j_list.sort()
        middle = int((len(i_list) - 1) / 2)
        i = i_list[middle]
        j = j_list[middle]

        return i, j

    def copy(self):
        new_solution = Solution()
        new_solution.routers = [] + self.routers
        new_solution.connected_cells = dict(self.connected_cells)
        new_solution.score = self.score
        new_solution.recalculate_score = self.scoreCalculationNeeded
        return new_solution
