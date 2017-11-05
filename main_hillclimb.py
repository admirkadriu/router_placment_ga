from genetic_algorithm.hill_climb import HillClimb
from models.solution import Solution
from reader import Reader
from utils import Utils

reader = Reader()
reader.read()

Utils.log("Pre-processing..")
Solution.connect_cells_needed = True
solution = Solution.generate_feasible()
solution.reset_movable_routers()
Solution.connect_cells_needed = False
Utils.log("Pre-processing ended..")
# print(solution.get_score())
#
# solution.remove_router(solution.routers[0])
# solution.remove_router(solution.routers[0])
# solution.remove_router(solution.routers[0])

solution.connected_cells = {}
solution.score_calculation_needed = True

HillClimb.minutes = 10
hill_climb = HillClimb(solution)
solution = hill_climb.run_by_time()
solution.fix()

print(solution.get_score())
