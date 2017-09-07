from uuid import uuid4

from models.building import Building
from models.router import Router


class Solution:

    @classmethod
    def generate_feasible(cls):
        solution = cls()
        bulk_count = int(Building.infrastructure_budget / (Router.unit_cost * Building.back_bone_cost))

        routers = Router.n_at_random_target(bulk_count)
        routers.sort(key=lambda r: r.cell.get_distance_to_backbone())

        can_add = True
        i = 0
        while can_add:
            router = routers[i]
            if not any(r for r in solution.routers if r.cell.id == router.cell.id):
                can_add = solution.add_router(router)
            else:
                routers.append(Router.at_random_target())

            i += 1

        return solution

    def __init__(self):
        self.id = uuid4()
        self.routers = []
        self.connected_cells = []
        self.score = None
        self.calculateScore = True

    def get_score(self):
        if self.calculateScore:
            self.calc_score()
        return self.score

    def connected_cells_count(self):
        return len(self.connected_cells)

    def routers_count(self):
        return len(self.routers)

    def calc_score(self):
        covered_cells_score = 1000 * len(Building.get_covered_cells(self.routers))
        remaining_budget_score = Building.infrastructure_budget - (
            self.connected_cells_count() * Building.back_bone_cost + self.routers_count() * Router.unit_cost)
        self.score = covered_cells_score + remaining_budget_score
        self.calculateScore = False
        return self.score

    def get_cost(self):
        return self.routers_count() * Router.unit_cost + self.connected_cells_count() * Building.back_bone_cost

    def is_feasible(self):
        return self.get_cost() <= Building.infrastructure_budget

    def connect_routers(self):
        self.connected_cells = []
        self.routers.sort(key=lambda r: r.cell.get_distance_to_backbone())

        for router in self.routers:
            cells_to_connect = router.get_best_path(self.connected_cells)
            self.connected_cells += cells_to_connect

        self.calculateScore = True
        return

    def add_router(self, router):
        cells_to_connect = router.get_best_path(self.connected_cells)
        cost_to_add = len(cells_to_connect) * Building.back_bone_cost + Router.unit_cost

        if (self.get_cost() + cost_to_add) <= Building.infrastructure_budget:
            self.routers.append(router)
            self.connected_cells += cells_to_connect
            self.calculateScore = True
            return True

        return False
