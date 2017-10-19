from multiprocessing import Pool
from random import shuffle

from genetic_algorithm.main import GeneticAlgorithm
from models.solution import Solution
from reader import Reader
from utils import Utils

reader = Reader()
reader.read()


def first_worker(i):
    alg = GeneticAlgorithm(3, 2, 2, 2)
    solutions = alg.run_parallel()

    return solutions

def second_worker(solutions):
    alg = GeneticAlgorithm(len(solutions), 2, 2, 2)
    solutions = alg.run_parallel(solutions)

    return solutions


if __name__ == '__main__':
    workers_count = 4  # multiprocessing.cpu_count()
    results = []
    with Pool(processes=workers_count) as pool:
        results = pool.map(first_worker, range(workers_count))

    populate = []
    for result in results:
        Utils.log("Best from first rund: ", result[0]["score"])
        for sol_dict in result:
            solution = Solution.get_from_dict(sol_dict)
            populate.append(Solution.get_from_dict(sol_dict))

    Utils.plot(populate[0])

    shuffle(populate)
    chunked_solutions = Utils.chunk_list(populate, workers_count)
    with Pool(processes=workers_count) as pool:
        results = pool.map(second_worker, chunked_solutions)


    populate = []
    for result in results:
        Utils.log("Best second run: ", result[0]["score"])
        for sol_dict in result:
            solution = Solution.get_from_dict(sol_dict)
            populate.append(Solution.get_from_dict(sol_dict))

    Utils.plot(populate[0])

    Utils.log("---------- Running on main process ----------")
    alg = GeneticAlgorithm(len(populate), 4, 2, 2)
    solution = alg.run(populate)[0]
    Utils.plot(solution)

    Utils.plot(solution)
    Utils.log("Best from main process: ", solution.score)
