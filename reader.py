from config import Config
from enums.CellType import CellType
from models.building import Building
from models.cell import Cell
from models.router import Router
from models.solution import Solution


class Reader:
    @staticmethod
    def read():
        file = open(Config.file_path, "r")
        Building.planimetry = []
        Building.target_cells = []

        for index, line in enumerate(file):
            if index < 3:
                line_split = line.split()
                if index == 0:
                    Building.row_count = int(line_split[0])
                    Building.column_count = int(line_split[1])
                    Router.radius = int(line_split[2])
                elif index == 1:
                    Building.back_bone_cost = float(line_split[0])
                    Router.unit_cost = float(line_split[1])
                    Building.infrastructure_budget = float(line_split[2])
                else:
                    i, j = map(int, line_split)
                    Building.back_bone_cell = Cell.get(i, j)
            else:
                cells_row = list(line)
                cells_row = cells_row[:Building.column_count]
                Building.planimetry.append(cells_row)
                for column, cell_type in enumerate(cells_row):
                    if cell_type == CellType.TARGET.value:
                        cell = Cell.get(index - 3, column)
                        Building.target_cells.append(cell)

        file.close()
        return

    @staticmethod
    def read_solution(file_path):
        file = open(file_path, "r")
        number_of_connected_cells = 0
        solution = Solution()
        for index, line in enumerate(file):
            if index == 0:
                number_of_connected_cells = int(line)
            elif index <= number_of_connected_cells:
                line_split = line.split()
                cell = Cell.get(int(line_split[0]), int(line_split[1]))
                solution.connected_cells[cell.id] = cell
            elif index == number_of_connected_cells + 1:
                number_of_routes = int(line)
            else:
                line_split = line.split()
                cell = Cell.get(int(line_split[0]), int(line_split[1]))
                router = Router(cell)
                solution.routers.append(router)
                solution.update_covered_cells(router.get_target_cells_covered(), True)

        return solution
