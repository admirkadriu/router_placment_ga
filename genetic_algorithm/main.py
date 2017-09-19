import random

from genetic_algorithm.crossover import Crossover
from models.solution import Solution


class GeneticAlgorithm:
    pop_size = 200
    tournament_size = 20
    parental_size = 2

    def run(self):
        t = 0
        populate = self.initialize()
        while t < 1000:
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
        crossover = Crossover(parents)
        children = crossover.rectangle()
        return children

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
