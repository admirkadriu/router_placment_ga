import random

from models.solution import Solution
from utils import Utils


class GeneticAlgorithm:
    pop_size = 100
    tournament_size = 2
    parental_size = 2

    def run(self):
        t = 0
        populate = self.initialize()
        while t < 100:
            parents = self.select(populate)
            children = self.crossover(parents)
            mutated_children = self.mutate(children)
            populate = self.populate_update(populate, mutated_children)
            t += 1

            populate.sort(key=lambda s: s.get_score(), reverse=True)
        return populate[0]

    def initialize(self):
        populate = []
        for i in range(0, GeneticAlgorithm.pop_size):
            populate.append(Solution.generate_feasible())
        return populate

    def select(self, populate):
        parents = []
        while len(parents) < GeneticAlgorithm.parental_size:
            selected = self.tournament_selection(populate)
            if not any(x for x in parents if x.id == selected.id):
                parents.append(selected)
        return parents

    def crossover(self, parents):
        parent_one = random.choice(parents)
        parent_two = random.choice(parents)
        first_parent_chunk = Utils.chunk_list(parent_one.routers, 4)
        second_parent_chunk = Utils.chunk_list(parent_two.routers, 4)
        solution = Solution()
        routers = first_parent_chunk[2] + first_parent_chunk[0] + second_parent_chunk[3] + second_parent_chunk[1]
        can_add = True
        i = 0
        while can_add and i < len(routers):
            router = routers[i]
            if not any(r for r in solution.routers if r.cell.id == router.cell.id):
                can_add = solution.add_router(router, False)
            i += 1

        solution.reconnect_routers()
        return [solution]

    def mutate(self, children):
        # Variation: Perform mutation on individuals in Ptc with probability p_m; Pmt = Mutate(Pct)
        return children

    def populate_update(self, populate, mutated_children):
        new_population = populate + mutated_children
        new_population.sort(key=lambda s: s.get_score(), reverse=True)
        return new_population[:GeneticAlgorithm.pop_size]

    def tournament_selection(self, populate):
        best = random.choice(populate)
        for i in range(1, GeneticAlgorithm.tournament_size):
            solution = random.choice(populate)
            if solution.get_score() > best.get_score():
                best = solution

        return best
