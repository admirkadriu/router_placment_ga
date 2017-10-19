import random

from models.building import Building
from models.router import Router
from utils import Utils


class Mutation:
    def __init__(self, individuals):
        self.individuals = individuals
        self.clone = None
        pass

    def shift(self):
        random_router = random.choice(self.clone.routers)
        self.clone.remove_router(random_router)
        neighbor_cell = random.choice(random_router.cell.get_neighbors_cells(10))
        self.clone.add_router(Router(neighbor_cell))

    def random_move(self):
        for i in range(0, random.randint(0, 2)):
            random_router = random.choice(self.clone.routers)
            self.clone.remove_router(random_router)
            self.clone.add_router(Router(random.choice(Building.target_cells)))

    def add(self):
        for i in range(0, random.randint(0, 2)):
            added = self.clone.add_router(Router(random.choice(Building.target_cells)))
            if not added:
                break

    def remove(self):
        for i in range(0, random.randint(0, 2)):
            self.clone.add_router(Router(random.choice(Building.target_cells)))

    def run(self):
        for index, person in enumerate(self.individuals):
            self.clone = person.copy()
            random_int = random.randint(0, 2)
            if random_int == 0:
                self.add()
            elif random_int == 1:
                self.random_move()
            elif random_int == 2:
                self.shift()
            elif random_int == 1:
                self.random_move()

            self.individuals[index] = self.clone

            #Utils.log("New mutation ", person.get_score())

        return self.individuals
