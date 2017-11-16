from config import Config
from reader import Reader
from steiner_tree import computeGSMT, computeGMST
from utils import Utils

reader = Reader()
reader.read()

if __name__ == '__main__':
    solution = reader.read_solution("wining_team_results/" + Config.input + ".out")

    print(solution.get_score())
    print(len(solution.routers))
    print(len(solution.covered_cells))

    # points = solution.get_points_to_connect()
    #
    #
    #
    # gsmt = computeGMST(points)

    Utils.log("computing started")
    solution.fix()
    Utils.log("computing ended")
    print(len(solution.routers))
    print(solution.get_score())

    Utils.plot(solution)