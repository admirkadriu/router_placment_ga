import random

from models.building import Building
from models.router import Router


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
        random_router = random.choice(self.clone.routers)
        self.clone.remove_router(random_router)
        self.clone.add_router(Router(random.choice(Building.target_cells)))

    def add(self):
        self.clone.add_router(Router(random.choice(Building.target_cells)))

    def remove(self):
        self.clone.add_router(Router(random.choice(Building.target_cells)))

    def run(self):
        for index, person in enumerate(self.individuals):
            self.clone = person.copy()
            random_int = random.randint(0, 10)
            if random_int < 6:
                self.shift()
            elif random_int < 9:
                self.random_move()
            elif random_int == 9:
                self.add()
            elif random_int == 10:
                self.remove()

            self.individuals[index] = self.clone

            # Utils.log("New mutation ", person.get_score())

        return self.individuals
