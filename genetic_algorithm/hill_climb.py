import time

from genetic_algorithm.mutation import Mutation
from redis_provider import RedisProvider
from utils import Utils


class HillClimb:
    t = 100
    minutes = 1

    def __init__(self, solution):
        self.solution = solution
        self.score_history = []

    def run_by_iterations(self):
        for i in range(0, HillClimb.t):
            mutation = Mutation([self.solution].copy())
            mutant = mutation.run()[0]
            if mutant.get_score() >= self.solution.get_score():
                self.solution = mutant
                self.solution.set_movable_routers(mutant)

        return self.solution

    def run_by_time(self):
        timeout = time.time() + 60 * self.minutes
        i = 1
        while time.time() < timeout:
            mutation = Mutation([self.solution])
            mutant = mutation.run()[0]
            if mutant.get_score() >= self.solution.get_score():
                if mutant.get_score() > self.solution.get_score() and i >= HillClimb.t:
                    i=0
                    self.score_history.append([time.time(), mutant.get_score()])
                    Utils.log("Best Updated hc: ", mutant.score)

                self.solution = mutant
                self.solution.set_movable_routers(mutant)
            i += 1

        return self.solution
