import random
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

        routers = Router.n_at_random_target_clever(bulk_count)
        routers.sort(key=lambda r: r.cell.get_distance_to_backbone())  # TODO: insert only when i is %2

        can_add = True
        i = 0
        while can_add and i < len(routers):
            router = routers[i]
            if not any(r for r in solution.routers if r.cell.id == router.cell.id):  # TODO: check if this is needed
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

    def is_feasible(self):
        return self.get_cost() <= Building.infrastructure_budget

    def get_score(self):
        if self.calculateScore:
            self.calc_score()
        return self.score

    def get_cost(self):
        return self.routers_count() * Router.unit_cost + self.connected_cells_count() * Building.back_bone_cost

    def calc_score(self):
        budget_for_routers = self.routers_count() * Router.unit_cost
        budget_to_connect_routers = self.connected_cells_count() * Building.back_bone_cost

        remaining_budget_score = Building.infrastructure_budget - budget_for_routers - budget_to_connect_routers
        covered_cells_score = 1000 * len(Building.get_covered_cells(self.routers))

        self.score = covered_cells_score + remaining_budget_score
        self.calculateScore = False
        return self.score

    def set_routers(self, routers):
        r_dict = {}
        for r in routers:
            r_dict[r.cell.id] = r

        routers = list(r_dict.values())

        self.connected_cells = []
        self.score = None
        self.calculateScore = True

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

    def remove_router(self, router):
        for i, r in enumerate(self.routers):
            if r.cell.id == router.cell.id:
                del self.routers[i]
                self.reconnect_routers()

    def reconnect_routers(self):
        self.connected_cells = []
        self.sort_routers()

        for router in self.routers:
            cells_to_connect = router.get_best_path(self.connected_cells)
            self.connected_cells += cells_to_connect

        self.calculateScore = True
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
