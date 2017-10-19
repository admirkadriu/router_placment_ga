from genetic_algorithm.mutation import Mutation
from utils import Utils


class HillClimb:
    t = 1000

    def __init__(self,solution):
        self.solution = solution

    def run(self):
        for i in range(0, HillClimb.t):
            mutation = Mutation([self.solution])
            mutant = mutation.run()[0]
            if mutant.get_score() >= self.solution.get_score():
                #Utils.log("Solution improved: ", mutant.get_score())
                self.solution = mutant

        return self.solution