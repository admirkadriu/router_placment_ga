import time

import automated_runs
from config import Config
from genetic_algorithm.hill_climb import HillClimb
from genetic_algorithm.main import GeneticAlgorithm
from genetic_algorithm.mutation import Mutation
from models.cell import Cell
from reader import Reader
from utils import Utils

reader = Reader()
reader.read()


def execute_alg(run_params):
    run_params['id'] = time.time()

    GeneticAlgorithm.pc = run_params['p_c']
    GeneticAlgorithm.pm = run_params['p_m']
    HillClimb.t = run_params['t_h']
    Mutation.radius = run_params['r']

    Cell.cells_map = {}

    Utils.log("Genetic algorithm started..")
    alg = GeneticAlgorithm(run_params['p_s'], run_params['t_s'], run_params['n_ch'], run_params['time'])
    best = alg.perform()
    run_params['score'] = best.get_score()

    string_results = Utils.dict_to_string(run_params)
    Utils.print_to_csv("experiments/" + Config.input, "result" + str(run_params['id']), string_results)

    for i, score_item in enumerate(alg.score_history):
        alg.score_history[i][0] -= run_params['id']

    discrete_score_history = Utils.to_discrete_results(alg.score_history, 10)

    string_results = Utils.list_to_string(discrete_score_history)
    Utils.print_to_csv("experiments/" + Config.input + "/plots", "run_" + str(run_params['id']), string_results)


if __name__ == '__main__':
    GeneticAlgorithm.multi_process = True
    for run_params in automated_runs.runs_params_1:
        execute_alg(run_params)
