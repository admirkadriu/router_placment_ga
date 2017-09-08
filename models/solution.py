import time
from uuid import uuid4

from models.building import Building
from models.router import Router


class Solution:
    @classmethod
    def generate_feasible(cls):
        t0 = time.time()
        solution = cls()
        bulk_count = int(Building.infrastructure_budget / (Router.unit_cost * Building.back_bone_cost))

        routers = Router.n_at_random_target(bulk_count)
        routers.sort(key=lambda r: r.cell.get_distance_to_backbone())

        can_add = True
        i = 0
        while can_add:
            router = routers[i]
            if not any(r for r in solution.routers if r.cell.id == router.cell.id):
                can_add = solution.add_router(router, False)
            else:
                routers.append(Router.at_random_target())

            i += 1

        t1 = time.time()
        print("Solution Generated: ", solution.is_feasible(), "\n-Time: ", t1 - t0)
        score = solution.get_score()
        t2 = time.time()
        print("-Score: ", score, "; Time: ", t2 - t1)
        return solution

    def __init__(self):
        self.id = uuid4()
        self.routers = []
        self.connected_cells = []
        self.score = None
        self.calculateScore = True

    def connected_cells_count(self):
        return len(self.connected_cells)

    def routers_count(self):
        return len(self.routers)

    def sort_routers(self):
        self.routers.sort(key=lambda r: r.cell.get_distance_to_backbone())
        return

    def get_score(self):
        if self.calculateScore:
            self.calc_score()
        return self.score

    def get_cost(self):
        return self.routers_count() * Router.unit_cost + self.connected_cells_count() * Building.back_bone_cost

    def is_feasible(self):
        return self.get_cost() <= Building.infrastructure_budget

    def calc_score(self):
        budget_for_routers = self.routers_count() * Router.unit_cost
        budget_to_connect_routers = self.connected_cells_count() * Building.back_bone_cost

        remaining_budget_score = Building.infrastructure_budget - budget_for_routers - budget_to_connect_routers
        covered_cells_score = 1000 * len(Building.get_covered_cells(self.routers))

        self.score = covered_cells_score + remaining_budget_score
        self.calculateScore = False
        return self.score

    def add_router(self, router, sort=True):
        cells_to_connect = router.get_best_path(self.connected_cells)
        cost_to_add = len(cells_to_connect) * Building.back_bone_cost + Router.unit_cost

        if (self.get_cost() + cost_to_add) <= Building.infrastructure_budget:
            self.routers.append(router)
            self.connected_cells += cells_to_connect
            if sort:
                self.sort_routers()
            self.calculateScore = True
            return True

        return False

    def reconnect_routers(self):
        self.connected_cells = []
        self.sort_routers()

        for router in self.routers:
            cells_to_connect = router.get_best_path(self.connected_cells)
            self.connected_cells += cells_to_connect

        self.calculateScore = True
        return
