import random
import time
from uuid import uuid4

from enums.CellType import CellType
from models.building import Building
from models.cell import Cell
from models.router import Router
from utils import Utils


class Solution:
    connect_cells_needed = False
    estimated_connection_cost = 0

    @classmethod
    def generate_feasible(cls):
        t0 = time.time()
        solution = cls()
        bulk_count = int(Building.infrastructure_budget / (Router.unit_cost * Building.back_bone_cost))

        routers = Router.n_at_random_target_clever(bulk_count)
        routers.sort(key=lambda r: r.cell.get_distance_to_backbone())  # TODO: insert only when i is %2
        tg = time.time()

        can_add = True
        i = 0
        jump = 2
        while can_add and i < len(routers):
            router = routers[i]
            can_add = solution.add_router(router)

            i += jump

            if i >= len(routers):
                i = jump - 1
                jump = jump * 2

        if Solution.connect_cells_needed and Solution.estimated_connection_cost == 0:
            Solution.estimated_connection_cost = (solution.connected_cells_count() * Building.back_bone_cost) + (
                Router.unit_cost * solution.routers_count() * 0.0045)

        # time_connect = time.time()
        # score = solution.get_score()
        # time_score = time.time()
        # Utils.log("Solution Generated: ", solution.is_feasible(), "\n-Time: ", time_connect - t0)
        # Utils.log("-Score: ", score, "; Time: ", time_score - time_connect)
        # Utils.log("Random router generation time:", tg - t0)
        # Utils.log("Get from redis time:", RedisProvider.get_seconds)
        # sUtils.plot(solution)
        return solution

    def __init__(self):
        self.id = uuid4()
        self.routers = []
        self.connected_cells = {}
        self.covered_cells = {}
        self.uncovered_cells = set(Building.get_target_cells_set())
        self.score = None
        self.score_calculation_needed = True
        self.movable_routers = set()
        self.routers_to_be_movable = set()
        self.routers_to_be_unmovable = set()

    def connected_cells_count(self):
        return len(self.connected_cells)

    def routers_count(self):
        return len(self.routers)

    def is_feasible(self):
        return self.get_cost() <= Building.infrastructure_budget

    def get_score(self):
        if self.score_calculation_needed:
            self.calc_score()
        return self.score

    def rename(self):
        self.id = uuid4()

    def get_cost(self):
        return self.routers_count() * Router.unit_cost + self.connected_cells_count() * Building.back_bone_cost

    def get_available_budget(self):
        if Solution.connect_cells_needed:
            return Building.infrastructure_budget

        return Building.infrastructure_budget - Solution.estimated_connection_cost

    def calc_score(self):
        budget_for_routers = self.routers_count() * Router.unit_cost
        budget_to_connect_routers = self.connected_cells_count() * Building.back_bone_cost

        remaining_budget_score = Building.infrastructure_budget - budget_for_routers - budget_to_connect_routers
        covered_cells_score = 1000 * len(self.covered_cells)

        self.score = covered_cells_score + remaining_budget_score
        self.score_calculation_needed = False
        return self.score

    def set_routers(self, routers):
        r_dict = {}
        for r in routers:
            r_dict[r.cell.id] = r

        self.score = None
        self.score_calculation_needed = True

        self.routers = []
        self.covered_cells = {}
        self.connected_cells = {}

        for router in r_dict.values():
            self.routers.append(router)
            self.update_covered_cells(router.get_target_cells_covered(), True)

        if self.connect_cells_needed:
            self.reconnect_routers()

        while not self.is_feasible():
            self.sort_by_covered_cells()
            self.remove_router(self.routers[0])

        return

    def fix(self):
        self.score_calculation_needed = True
        Solution.connect_cells_needed = True
        self.reconnect_routers()

        while not self.is_feasible():
            self.sort_by_covered_cells()
            self.remove_router(self.routers[0])

        return

    def sort_by_covered_cells(self):
        for router in self.routers:
            router.unique_score = 0
            for key in router.get_target_cells_covered():
                if self.covered_cells[key] == 1:
                    router.unique_score += 1

        self.routers.sort(key=lambda r: r.unique_score)

    def sort_routers(self):
        self.routers.sort(key=lambda r: r.cell.get_distance_to_backbone())
        return

    def add_router(self, router):
        if router.cell.get_type() != CellType.TARGET.value:
            return False

        cells_to_connect = {}

        if Solution.connect_cells_needed:
            cells_to_connect = router.get_best_path(self.connected_cells)

        cost_to_add = len(cells_to_connect) * Building.back_bone_cost + Router.unit_cost

        if (self.get_cost() + cost_to_add) <= self.get_available_budget():
            self.routers.append(router)
            self.movable_routers.add(router.cell.id)
            self.update_covered_cells(router.get_target_cells_covered(), True)
            self.connected_cells.update(cells_to_connect)
            self.score_calculation_needed = True
            return True

        return False

    def remove_router(self, router):
        self.score_calculation_needed = True
        for i, r in enumerate(self.routers):
            if r.cell.id == router.cell.id:
                self.update_covered_cells(r.get_target_cells_covered(), False)
                self.movable_routers.discard(r.cell.id)
                del self.routers[i]
                if Solution.connect_cells_needed:
                    if r.cell.id != Building.back_bone_cell.id:
                        self.connected_cells.pop(r.cell.id, None)
                        cells_to_connect = self.disconnect_neighbor_cells(r.cell, {})
                        self.connect_group_of_cells(cells_to_connect)
                break

    def connect_group_of_cells(self, cells):
        length = len(cells)
        new_cells_to_connect = {}
        if length > 1:
            first_nearest_cell = cells[0].get_nearest_cell(cells[1:])
            new_cells_to_connect = cells[0].get_path_to_cell(first_nearest_cell)
            new_cells_to_connect[cells[0].id] = cells[0]
            new_cells_to_connect[first_nearest_cell.id] = first_nearest_cell
            if length > 2:
                for cell in cells[1:]:
                    if cell.id != first_nearest_cell.id:
                        nearest_cell = cell.get_nearest_cell(list(new_cells_to_connect.values()))
                        new_cells_to_connect.update(cell.get_path_to_cell(nearest_cell))
                        new_cells_to_connect[cell.id] = cell
        elif length == 1:
            new_cells_to_connect[cells[0].id] = cells[0]

        new_cells_to_connect.pop(Building.back_bone_cell.id, None)
        self.connected_cells.update(new_cells_to_connect)

    def contains_router(self, cell):
        for i, r in enumerate(self.routers):
            if r.cell.id == cell.id:
                return True

        return False

    def disconnect_neighbor_cells(self, cell, checked_cells, initial_call=True):
        cells_to_connect = []

        cells_to_check = cell.get_connected_neighbors_cells(self.connected_cells)

        if not initial_call and len(cells_to_check) > 1:
            if len(cells_to_check) == 2:
                if cells_to_check[0].is_neighbor_to(cells_to_check[1]):
                    if not Cell.are_in_same_row_or_column(cells_to_check):
                        self.connected_cells.pop(cell.id, None)
                        return [cells_to_check[0]]
                else:
                    return [cell]
            elif len(cells_to_check) == 3:
                if Cell.are_in_same_row_or_column(cells_to_check):
                    self.connected_cells.pop(cell.id, None)
                    return [cells_to_check[0]]
                else:
                    return [cell]
            else:
                return [cell]

        cells_to_check_dict = {}
        cells_to_remove = []

        for cell in cells_to_check:
            cells_to_check_dict[cell.id] = cell
            if cell.id not in checked_cells and (
                            cell.id in self.connected_cells or cell.id == Building.back_bone_cell.id):
                if self.contains_router(cell) or cell.id == Building.back_bone_cell.id:
                    cells_to_connect.append(cell)
                else:
                    cells_to_remove.append(cell)

        checked_cells.update(cells_to_check_dict)

        for cell in cells_to_remove:
            self.connected_cells.pop(cell.id, None)
            cells_to_connect = cells_to_connect + self.disconnect_neighbor_cells(cell, checked_cells, False)

        return cells_to_connect

    def reconnect_routers(self):
        self.sort_routers()
        if Solution.connect_cells_needed:
            self.connected_cells = {}
            for router in self.routers:
                cells_to_connect = router.get_best_path(self.connected_cells)
                self.connected_cells.update(cells_to_connect)
            self.score_calculation_needed = True

        return

    def get_worst_router(self):
        most_covered_cell_id = None
        most_covered_score = 0
        for cell_id in random.sample(list(self.covered_cells), int(len(self.covered_cells) / 20)):
            if self.covered_cells[cell_id] > most_covered_score:
                most_covered_cell_id = cell_id
                most_covered_score = self.covered_cells[cell_id]

        i, j = Utils.get_position_from_id(most_covered_cell_id)
        routers = self.get_inside_rectangle(i - Router.radius, j - Router.radius, Router.radius * 2 + 1,
                                            Router.radius * 2 + 1)

        return random.choice(routers)

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
        new_solution.id = uuid4()
        new_solution.routers = [] + self.routers
        new_solution.connected_cells = dict(self.connected_cells)
        new_solution.score = self.score
        new_solution.recalculate_score = self.score_calculation_needed
        new_solution.covered_cells = dict(self.covered_cells)
        new_solution.uncovered_cells = set(self.uncovered_cells)
        new_solution.movable_routers = set(self.movable_routers)
        return new_solution

    def update_covered_cells(self, covered_cells, added):
        for cell_id in covered_cells:
            if cell_id in self.covered_cells:
                if added:
                    self.covered_cells[cell_id] = self.covered_cells[cell_id] + 1
                else:
                    self.covered_cells[cell_id] = self.covered_cells[cell_id] - 1
                    if self.covered_cells[cell_id] <= 0:
                        del self.covered_cells[cell_id]
                        self.uncovered_cells.add(cell_id)
            else:
                if added:
                    self.covered_cells[cell_id] = 1
                    self.uncovered_cells.discard(cell_id)
        return

    def set_movable_routers(self, copy_solution=None):
        if copy_solution is None:
            copy_solution = self

        self.movable_routers = self.movable_routers.union(copy_solution.routers_to_be_movable)
        self.movable_routers = self.movable_routers.difference(copy_solution.routers_to_be_unmovable)
        copy_solution.routers_to_be_movable = set()
        copy_solution.routers_to_be_unmovable = set()

    def set_routers_to_be_movable(self, cell):
        routers_to_be_movable = self.get_inside_rectangle(cell.i - (2 * Router.radius),
                                                          cell.j - (2 * Router.radius),
                                                          4 * Router.radius, 4 * Router.radius)
        for router in routers_to_be_movable:
            self.routers_to_be_movable.add(router.cell.id)

    @classmethod
    def get_from_dict(cls, solution_dict):
        solution = cls()
        for position in solution_dict["routers"]:
            solution.routers.append(Router.at_position(position[0], position[1]))

        for position in solution_dict["connected_cells"]:
            solution.connected_cells[str(position[0]) + "," + str(position[1])] = Cell(position[0], position[1])

        solution.score = solution_dict["score"]
        solution.score_calculation_needed = False

        return solution
