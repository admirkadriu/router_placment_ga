from genetic_algorithm import GeneticAlgorithm
from reader import Reader
from models.building import Building
from models.cell import Cell
from models.router import Router


reader = Reader()
reader.read()
alg = GeneticAlgorithm()
solution = alg.run()
print(solution.routers)