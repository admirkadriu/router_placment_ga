import random
import time
from functools import partial
from multiprocessing import Pool

from genetic_algorithm.crossover import Crossover
from genetic_algorithm.hill_climb import HillClimb
from genetic_algorithm.mutation import Mutation
from models.solution import Solution
from utils import Utils


class GeneticAlgorithm:
    multi_process = False
    pc = 0.4
    pm = 0.8

    def __init__(self, pop_size, tournament_size, parental_size, minutes):
        self.score_history = []

        self.pop_size = pop_size
        self.tournament_size = tournament_size
        self.parental_size = parental_size
        self.minutes = 0.8 * minutes
        HillClimb.minutes = 0.2 * minutes

        self.timeout = time.time() + 60 * self.minutes
        self.best_score = 0

    def run(self, populate=None):
        t = 0
        if populate is None:
            populate = self.initialize()
        self.populate_update(populate)

        while time.time() < self.timeout:
            parents = self.select(populate)
            children = self.crossover(parents)
            mutated_children = self.mutate(children)

            mutated_children = self.hill_climb(mutated_children)
            populate = self.populate_update(populate, mutated_children)

            t += 1

        populate.sort(key=lambda s: s.get_score(), reverse=True)
        return populate

    def perform(self):
        self.timeout = time.time() + 60 * self.minutes

        Utils.log("Pre-processing..")
        Solution.connect_cells_needed = True
        Solution.generate_feasible()
        Solution.connect_cells_needed = False
        Utils.log("Pre-processing ended..")

        best_individual = self.run()[0]

        HillClimb.minutes *= 0.85
        hill_climb = HillClimb(best_individual)
        best_individual = hill_climb.run_by_time()

        self.score_history += hill_climb.score_history

        time_before_fix = time.time()
        score_before_fix = best_individual.get_score()

        best_individual.fix()

        score_difference = score_before_fix - best_individual.get_score()

        for i, record in enumerate(self.score_history):
            self.score_history[i][1] -= score_difference

        time_difference = time.time() - time_before_fix

        HillClimb.minutes /= 0.85
        HillClimb.minutes *= 0.15
        hill_climb = HillClimb(best_individual)
        best_individual = hill_climb.run_by_time()

        for item in hill_climb.score_history:
            item[0] -= time_difference

        self.score_history += hill_climb.score_history

        return best_individual

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
            mutation = Mutation(individuals, True)
            mutants = mutation.run()
        else:
            mutants = individuals

        return mutants

    def populate_update(self, populate, mutated_children=[]):
        mutated_children = self.get_only_diverse_individuals(populate, mutated_children)

        new_population = populate + mutated_children
        new_population.sort(key=lambda s: s.get_score(), reverse=True)

        new_population = new_population[:self.pop_size]

        if populate[0].score > self.best_score:
            self.best_score = populate[0].score
            self.score_history.append([time.time(), self.best_score])
            Utils.log("Best Updated: ", populate[0].score)

        return new_population

    def get_only_diverse_individuals(self, populate, mutated_children):
        children_to_get = Utils.list_to_dict(mutated_children, "id")
        for children in mutated_children:
            for person in populate:
                if children.id == person.id:
                    children_to_get.pop(children.id)
                    break

                if abs(children.get_score() - person.get_score()) < 10:
                    common = len(children.routers_set.intersection(person.routers_set))
                    if common / len(children.routers_set) > 0.95:
                        children_to_get.pop(children.id)
                        Utils.log("Same solution")
                        break

        return list(children_to_get.values())

    def tournament_selection(self, populate, tournament_size, check_if_accepted):
        best = random.choice(populate)
        for i in range(1, tournament_size):
            solution = random.choice(populate)
            if check_if_accepted(solution.get_score(), best.get_score()):
                best = solution

        return best

    def hill_climb(self, mutated_children):
        if HillClimb.t != 0:
            if len(mutated_children) > 1 and GeneticAlgorithm.multi_process:
                func = partial(self.do_hill_climb, Solution.estimated_connection_cost, HillClimb.t, Mutation.radius)
                with Pool(processes=len(mutated_children)) as pool:
                    result = pool.map(func, mutated_children)
                    mutated_children = list(result)
            else:
                for index, child in enumerate(mutated_children):
                    hill_climb = HillClimb(child)
                    mutated_children[index] = hill_climb.run_by_iterations()

        return mutated_children

    def do_hill_climb(self, estimated_connection_cost, t, radius, mutated_children):
        Solution.estimated_connection_cost = estimated_connection_cost
        HillClimb.t = t
        Mutation.radius = radius
        hill_climb = HillClimb(mutated_children)
        child = hill_climb.run_by_iterations()
        return child
