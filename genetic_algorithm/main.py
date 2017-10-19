import random
import time

from genetic_algorithm.crossover import Crossover
from genetic_algorithm.hill_climb import HillClimb
from genetic_algorithm.mutation import Mutation
from models.solution import Solution
from utils import Utils


class GeneticAlgorithm:
    pc = 0.7
    pm = 0.8

    def __init__(self, pop_size, tournament_size, parental_size, minutes):
        self.pop_size = pop_size
        self.tournament_size = tournament_size
        self.parental_size = parental_size
        self.minutes = minutes

    def run(self, populate=None):
        t = 0
        best_score = 0
        if populate is None:
            populate = self.initialize()

        timeout = time.time() + 60 * self.minutes
        while time.time() < timeout:
            parents = self.select(populate)
            children = self.crossover(parents)
            mutated_children = self.mutate(children)

            for index, child in enumerate(mutated_children):
                hill_climb = HillClimb(child)
                mutated_children[index] = hill_climb.run()

            populate = self.populate_update(populate, mutated_children)
            if populate[0].score > best_score:
                best_score = populate[0].score
                Utils.log("Best Updated: ", populate[0].score)
            t += 1

        populate.sort(key=lambda s: s.get_score(), reverse=True)
        return populate

    def run_parallel(self, populate=None):
        solutions = self.run(populate)
        sol_dict_list = []

        for solution in solutions:
            routers = []
            connected_cells = []
            for router in solution.routers:
                routers.append(router.cell.position)

            for key in solution.connected_cells:
                connected_cells.append(solution.connected_cells[key].position)

            sol = dict()
            sol["routers"] = routers
            sol["connected_cells"] = connected_cells
            sol["score"] = solution.score
            sol_dict_list.append(sol)

        return sol_dict_list

    def initialize(self):
        populate = []
        t0 = time.time()

        for i in range(0, self.pop_size):
            populate.append(Solution.generate_feasible())

        t1 = time.time()
        Utils.log("Initialization done ", " -Time: ", t1 - t0)
        return populate

    def select(self, populate):
        parents = []
        available_populate = Utils.list_to_dict(populate, "id")
        while len(parents) < self.parental_size:
            selected = self.tournament_selection(list(available_populate.values()), self.tournament_size,
                                                 lambda current, best: current > best)
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
        new_population = list({i.id: i for i in new_population}.values())  # remove duplicates
        new_population.sort(key=lambda s: s.get_score(), reverse=True)
        new_population = new_population[:self.pop_size]
        # pop = set(x.id for x in populate)
        # mut = set(x.id for x in mutated_children)
        # new = set(x.id for x in mutated_children)
        # Utils.log("In populate and in mutated: ", pop.intersection(mut))
        # Utils.log("Added on populate: ", new.intersection(mut))
        return new_population

    def tournament_selection(self, populate, tournament_size, check_if_accepted):
        best = random.choice(populate)
        for i in range(1, tournament_size):
            solution = random.choice(populate)
            if check_if_accepted(solution.get_score(), best.get_score()):
                best = solution

        return best
