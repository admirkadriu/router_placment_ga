from config import Config
from reader import Reader
from steiner_tree import computeGSMT, computeGMST
from utils import Utils

reader = Reader()
reader.read()

if __name__ == '__main__':
    solution = reader.read_solution("../wining_team_results/" + Config.input + ".out")

    print(solution.get_score())
    print(len(solution.routers))

    points = solution.get_points_to_connect()


    Utils.log("computing started")
    gsmt = computeGMST(points)

    Utils.log("computing ended")

    solution.fix(gsmt)
    print(len(solution.routers))
    print(solution.get_score())

    Utils.plot(solution)

    solution.fix()
    print(len(solution.routers))
    print(solution.get_score())
    gsmt = gsmt
