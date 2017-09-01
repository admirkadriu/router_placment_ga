from uuid import uuid4

from models.building import Building
from models.router import Router


class Solution:
    @classmethod
    def generate_feasible(cls):
        solution = cls()
        can_add = True
        while can_add:
            router = Router.at_random_target()
            if not any(r for r in solution.routers if r.cell.id == router.cell.id):
                can_add = solution.add_router(router)
        return solution

    def __init__(self):
        self.routers = []
        self.connected_cells = []
        self.score = None
        self.id = uuid4()

    def get_score(self):
        if self.score is None:
            self.calc_score()
        return self.score

    def get_connected_cells_count(self):
        return len(self.connected_cells)

    def get_routers_count(self):
        return len(self.routers)

    def calc_score(self):
        covered_cells_score = 1000 * len(Building.get_covered_cells(self.routers))
        remaining_budget_score = Building.infrastructure_budget - (
            len(self.connected_cells) * Building.back_bone_cost + len(self.routers) * Router.unit_cost)
        self.score = covered_cells_score + remaining_budget_score
        return self.score

    def get_cost(self):
        return len(self.routers) * Router.unit_cost + len(self.connected_cells) * Building.back_bone_cost

    def is_feasible(self):
        return self.get_cost() <= Building.infrastructure_budget

    def connect_routers(self):
        self.connected_cells = []
        self.routers.sort(key=lambda r: r.cell.get_distance_to_backbone())

        for router in self.routers:
            cells_to_connect = router.get_best_path(self.connected_cells)
            self.connected_cells.append(cells_to_connect)

        return

    def add_router(self, router):
        cells_to_connect = router.get_best_path(self.connected_cells)
        cost_to_add = len(cells_to_connect) * Building.back_bone_cost + Router.unit_cost
        if (self.get_cost() + cost_to_add) <= Building.infrastructure_budget:
            self.routers.append(router)
            self.connected_cells = self.connected_cells + cells_to_connect
            return True
        return False

    def add_routers(self, routers):
        routers.sort(key=lambda r: r.cell.get_distance_to_backbone())
        connected_cells = self.connected_cells
        cells_to_connect = []
        cost_to_add = 0
        for router in routers:
            router_cells_to_connect = router.get_best_path(connected_cells)
            cells_to_connect += router_cells_to_connect
            connected_cells += router_cells_to_connect
            cost_to_add += len(router_cells_to_connect) * Building.back_bone_cost + Router.unit_cost

        if (self.get_cost() + cost_to_add) <= Building.infrastructure_budget:
            self.routers = self.routers + routers
            self.connected_cells = self.connected_cells + cells_to_connect
            return True
        return False
