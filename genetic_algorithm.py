from random import randint

from models.solution import Solution


class GeneticAlgorithm:
    pop_size = 10
    tournament_size = 2
    parental_size = 2

    def run(self):
        t = 0
        populate = self.initialize()
        while t < 10:
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
        # Variation: Perform crossover on pairs of individuals in Pt with probability p_c; Pct = Cross(Pt)
        return parents

    def mutate(self, children):
        # Variation: Perform mutation on individuals in Ptc with probability p_m; Pmt = Mutate(Pct)
        return children

    def populate_update(self, populate, mutated_children):
        new_population = populate + mutated_children
        new_population.sort(key=lambda s: s.get_score(), reverse=True)
        return new_population[:GeneticAlgorithm.pop_size]

    def tournament_selection(self, populate):
        best = populate[randint(0, GeneticAlgorithm.pop_size - 1)]
        for i in range(1, GeneticAlgorithm.tournament_size):
            solution = populate[randint(0, GeneticAlgorithm.pop_size - 1)]
            if solution.get_score() > best.get_score():
                best = solution

        return best
