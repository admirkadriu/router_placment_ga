import random

from models.building import Building
from models.cell import Cell
from models.router import Router
from utils import Utils


class Mutation:
    radius = 5

    def __init__(self, individuals, is_hill_climb=False):
        self.individuals = individuals
        self.clone = None
        self.is_hill_climb = is_hill_climb

    def shift(self):
        random_router = random.choice(self.clone.routers)
        self.clone.remove_router(random_router)
        neighbor_cell = random.choice(random_router.cell.get_neighbor_target_cells(Mutation.radius))
        self.clone.add_router(Router(neighbor_cell))
        self.clone.set_routers_to_be_movable(neighbor_cell)

    def clever_shift(self):
        score_before = self.clone.get_score()
        router_with_same_score = None

        cell_id = random.sample(self.clone.movable_routers, 1)[0]
        i, j = Utils.get_position_from_id(cell_id)
        random_router = Router.at_position(i, j)

        self.clone.remove_router(random_router)

        neighbor_target_cells = random_router.cell.get_neighbor_target_cells(self.clone.clever_shift_distance)
        for cell in neighbor_target_cells:
            router_to_add = Router(cell)
            added = self.clone.add_router(router_to_add)

            if self.clone.get_score() > score_before:
                self.clone.set_routers_to_be_movable(cell)
                return
            elif added:
                self.clone.remove_router(router_to_add)
                if self.clone.get_score() == score_before and router_with_same_score is not None:
                    router_with_same_score = router_to_add

        if router_with_same_score is not None:
            self.clone.add_router(router_with_same_score)
            self.clone.set_routers_to_be_movable(router_with_same_score.cell)
        else:
            self.clone.routers_to_be_unmovable.add(cell_id)

    def random_move(self):
        score_before = self.clone.get_score()
        random_router = random.choice(self.clone.routers)

        self.clone.remove_router(random_router)

        cell_id = random.sample(self.clone.uncovered_cells, 1)[0]
        i, j = Utils.get_position_from_id(cell_id)
        cell = Cell(i, j)

        self.clone.add_router(Router(cell))

        if not self.is_hill_climb or self.clone.get_score() >= score_before:
            self.clone.set_routers_to_be_movable(random_router.cell)
            self.clone.set_routers_to_be_movable(cell)

    def add(self):
        cell_id = random.sample(self.clone.uncovered_cells, 1)[0]
        i, j = Utils.get_position_from_id(cell_id)
        cell = Cell(i, j)

        self.clone.add_router(Router(cell))
        self.clone.set_routers_to_be_movable(cell)

    def remove(self):
        random_router = random.choice(self.clone.routers)
        self.clone.remove_router(random_router)

    def run(self):
        for index, person in enumerate(self.individuals):
            self.clone = person.copy()
            random_int = random.randint(0, 100)
            if random_int < 65:
                if len(self.clone.movable_routers) == 0:
                    self.random_move()
                else:
                    self.clever_shift()
            elif random_int < 85:
                self.random_move()
            elif random_int < 94:
                self.add()
            elif random_int < 100:
                self.remove()

            if not self.is_hill_climb:
                self.clone.set_movable_routers()

            self.individuals[index] = self.clone

        return self.individuals
