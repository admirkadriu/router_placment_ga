from uuid import uuid4

from automated_runs import runs_params_1
from config import Config
from genetic_algorithm.hill_climb import HillClimb
from genetic_algorithm.main import GeneticAlgorithm
from genetic_algorithm.mutation import Mutation
from reader import Reader
from utils import Utils

reader = Reader()
reader.read()


def execute_alg(run_params):
    run_params['id'] = uuid4()
    GeneticAlgorithm.pc = run_params['p_c']
    GeneticAlgorithm.pm = run_params['p_m']
    HillClimb.t = run_params['t_h']
    Mutation.radius = run_params['r']

    Utils.log("Genetic algorithm started..")
    alg = GeneticAlgorithm(run_params['p_s'], run_params['t_s'], run_params['n_ch'], run_params['time'])
    best = alg.perform()
    run_params['score'] = best.get_score()

    string_results = Utils.dict_to_string(run_params)
    Utils.print_to_csv("experiments/" + Config.input, "run_" + str(run_params['id']), string_results)
    string_results = Utils.list_to_string(alg.score_history)
    Utils.print_to_csv("experiments/" + Config.input + "/plots", "run_" + str(run_params['id']), string_results)


if __name__ == '__main__':
    GeneticAlgorithm.multi_process = True
    for run_params in runs_params_1:
        execute_alg(run_params)
