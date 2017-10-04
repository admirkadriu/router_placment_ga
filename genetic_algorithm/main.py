import random

from genetic_algorithm.crossover import Crossover
from genetic_algorithm.mutation import Mutation
from models.solution import Solution
from utils import Utils


class GeneticAlgorithm:
    pop_size = 100
    tournament_size = 10
    parental_size = 2
    pc = 0.5
    pm = 0.5

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
        available_populate = Utils.list_to_dict(populate, "id")
        while len(parents) < GeneticAlgorithm.parental_size:
            selected = self.tournament_selection(list(available_populate.values()))
            parents.append(selected)
            del available_populate[selected.id]
        return parents

    def crossover(self, parents):
        if random.random() < GeneticAlgorithm.pc:
            crossover = Crossover(parents)
            children = crossover.rectangle()
        else:
            children = parents

        return children

    def mutate(self, individuals):
        if random.random() < GeneticAlgorithm.pm:
            mutation = Mutation(individuals)
            mutants = mutation.run()
        else:
            mutants = individuals

        return mutants

    def populate_update(self, populate, mutated_children):
        new_population = populate + mutated_children
        new_population = list({i.id: i for i in new_population}.values())
        new_population.sort(key=lambda s: s.get_score(), reverse=True)
        return new_population[:GeneticAlgorithm.pop_size]

    def tournament_selection(self, populate):
        best = random.choice(populate)
        for i in range(1, GeneticAlgorithm.tournament_size):
            solution = random.choice(populate)
            if solution.get_score() > best.get_score():
                best = solution

        return best
