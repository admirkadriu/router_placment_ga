import random

from enums.mutation_type import MutationType
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
        self.mutation_type = None

    def shift(self):
        self.mutation_type = MutationType.SHIFT.value
        random_router = random.choice(self.clone.routers)
        self.clone.remove_router(random_router)
        neighbor_cell = random.choice(random_router.cell.get_neighbor_target_cells(Mutation.radius))
        self.clone.add_router(Router(neighbor_cell))
        self.clone.make_near_routers_movable(neighbor_cell)

    def clever_shift(self):
        self.mutation_type = MutationType.CLEVER_SHIFT.value
        score_before = self.clone.get_score()
        cell_with_same_score = None

        cell_id = random.sample(self.clone.movable_routers, 1)[0]
        i, j = Utils.get_position_from_id(cell_id)
        random_router = Router.at_position(i, j)

        self.clone.remove_router(random_router)

        neighbor_target_cells = random_router.cell.get_neighbor_target_cells(self.clone.clever_shift_distance)
        random.shuffle(neighbor_target_cells)
        for cell in neighbor_target_cells:
            router_to_add = Router(cell)
            added = self.clone.add_router(router_to_add)

            if self.clone.get_score() > score_before:
                self.clone.make_near_routers_movable(cell)
                self.clone.make_near_routers_movable(random_router.cell)
                # Utils.log("Found better")
                return
            elif added:
                if self.clone.get_score() == score_before:
                    cell_with_same_score = router_to_add.cell

                self.clone.remove_router(router_to_add)

        if cell_with_same_score is not None:
            self.clone.add_router(Router(cell_with_same_score))
            self.clone.make_near_routers_movable(random_router.cell)
            # Utils.log("Same score",random_router.cell.id,cell_with_same_score.id)
        else:
            self.clone.routers_to_be_unmovable.add(cell_id)

    def random_move(self):
        self.mutation_type = MutationType.RANDOM_MOVE.value
        score_before = self.clone.get_score()
        random_router = random.choice(self.clone.routers)

        self.clone.remove_router(random_router)

        if len(self.clone.uncovered_cells) > 0 and random.random() < 0.75:
            cell_id = random.sample(self.clone.uncovered_cells, 1)[0]
            i, j = Utils.get_position_from_id(cell_id)
            cell = Cell(i, j)
        else:
            cell = random.choice(Building.target_cells)

        self.clone.add_router(Router(cell))

        if not self.is_hill_climb or self.clone.get_score() >= score_before:
            self.clone.make_near_routers_movable(random_router.cell)
            self.clone.make_near_routers_movable(cell)

    def add(self):
        self.mutation_type = MutationType.ADD_ROUTER.value
        if len(self.clone.uncovered_cells) > 0:
            cell_id = random.sample(self.clone.uncovered_cells, 1)[0]
            i, j = Utils.get_position_from_id(cell_id)
            cell = Cell(i, j)
        else:
            cell = random.choice(Building.target_cells)

        self.clone.add_router(Router(cell))
        self.clone.make_near_routers_movable(cell)

    def remove(self):
        self.mutation_type = MutationType.REMOVE_ROUTER.value
        random_router = random.choice(self.clone.routers)
        self.clone.remove_router(random_router)

    def run(self):
        for index, person in enumerate(self.individuals):
            self.clone = person.copy()
            random_int = random.randint(0, 100)

            if random_int < 45:
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
                self.clone.refresh_movable_routers()

            self.individuals[index] = self.clone

        return self.individuals
