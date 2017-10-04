import random

from models.building import Building
from models.router import Router
from models.solution import Solution


class Mutation:
    def __init__(self, individuals):
        self.individuals = individuals
        self.current_person_clone = Solution()
        pass

    def small_shift(self):
        random_router = random.choice(self.current_person_clone.routers)
        self.current_person_clone.remove_router(random_router)
        neighbor_cell = random.choice(random_router.cell.get_neighbors_cells())
        self.current_person_clone.add_router(Router(neighbor_cell))
        return self.current_person_clone

    def big_shift(self):
        random_router = random.choice(self.current_person_clone.routers)
        self.current_person_clone.remove_router(random_router)
        neighbor_cell = random.choice(random_router.cell.get_neighbors_cells(10))
        self.current_person_clone.add_router(Router(neighbor_cell))

    def random_move(self):
        random_router = random.choice(self.current_person_clone.routers)
        self.current_person_clone.remove_router(random_router)
        self.current_person_clone.add_router(Router(random.choice(Building.target_cells)))

    def add_new_one(self):
        self.current_person_clone.add_router(Router(random.choice(Building.target_cells)))

    def run(self):
        for person in self.individuals:
            self.current_person_clone = person.copy()
            random_int = random.randint(0,4)
            if random_int == 0:
                 self.small_shift()
            elif random_int == 1:
                self.big_shift()
            elif random_int == 2:
                self.random_move()
            else:
                self.add_new_one()

            person = self.current_person_clone
            person.rename()

            print("New mutation ", person.get_score())

        return self.individuals
