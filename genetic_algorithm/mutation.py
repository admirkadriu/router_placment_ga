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
        for i in range(0, random.randint(0, 4)):
            random_router = random.choice(self.clone.routers)
            self.clone.remove_router(random_router)
            self.clone.add_router(Router(random.choice(Building.target_cells)))

    def add(self):
        for i in range(0, random.randint(0, 4)):
            self.clone.add_router(Router(random.choice(Building.target_cells)))

    def remove(self):
        for i in range(0, random.randint(0, 4)):
            self.clone.add_router(Router(random.choice(Building.target_cells)))

    def run(self):
        for person in self.individuals:
            self.clone = person.copy()
            random_int = random.randint(0, 3)
            if random_int == 0:
                self.add()
            elif random_int == 1:
                self.remove()
            elif random_int == 2:
                self.random_move()
            elif random_int == 3:
                self.shift()

            person = self.clone

            print("New mutation ", person.get_score())

        return self.individuals
