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
        score_before = self.clone.get_score()
        random_router = random.choice(self.clone.routers)
        self.clone.remove_router(random_router)
        neighbor_cell = random.choice(random_router.cell.get_neighbor_target_cells(Mutation.radius))
        self.clone.add_router(Router(neighbor_cell))
        self.clone.set_routers_to_be_movable(neighbor_cell)
        if self.clone.get_score() >= score_before:
            Utils.log("shifting")

    def clever_shift(self):
        score_before = self.clone.get_score()
        cell_id = random.sample(self.clone.movable_routers, 1)[0]
        i, j = Utils.get_position_from_id(cell_id)
        random_router = Router.at_position(i, j)
        self.clone.remove_router(random_router)
        neighbor_target_cells = random_router.cell.get_neighbor_target_cells(self.clone.clever_shift_distance)
        for cell in neighbor_target_cells:
            router_to_add = Router(cell)
            added = self.clone.add_router(router_to_add)
            if self.clone.get_score() > score_before \
                    or (self.clone.get_score() == score_before and cell.id == neighbor_target_cells[
                            random.randint(0, len(neighbor_target_cells)) - 1].id):
                self.clone.set_routers_to_be_movable(cell)
                return
            elif added:
                self.clone.remove_router(router_to_add)

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
        cell = random.choice(Building.target_cells)
        self.clone.add_router(Router(cell))
        self.clone.set_routers_to_be_movable(cell)

    def remove(self):
        self.clone.add_router(Router(random.choice(Building.target_cells)))

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
            elif random_int < 95:
                self.add()
            elif random_int < 100:
                self.remove()

            if not self.is_hill_climb:
                self.clone.set_movable_routers()

            self.individuals[index] = self.clone

        return self.individuals
