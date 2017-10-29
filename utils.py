import logging
import pathlib
import sys
import time

import matplotlib.pyplot as plt
import numpy as np


def get_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


class Utils:
    logger = get_logger()

    @staticmethod
    def log(*args):
        # args = args + (time.strftime("%H:%M:%S"),)
        # Utils.logger.info(args)
        pass

    @staticmethod
    def chunk_list(array, num):
        avg = len(array) / float(num)
        out = []
        last = 0.0

        while last < len(array):
            out.append(array[int(last):int(last + avg)])
            last += avg

        for i, inner_list in enumerate(out):
            if len(out[i]) == 0:
                out[i] = out[i + 1]
        return out

    @staticmethod
    def list_to_dict(list, id):
        dict = {}
        for item in list:
            dict[getattr(item, id)] = item

        return dict

    @staticmethod
    def get_cells_tuples(cells):
        tuple_list = []
        for key, cell in cells.items():
            tuple_list.append(cell.position)

        return tuple_list

    @staticmethod
    def plot(solution, cell_to_show=None):
        from models.building import Building
        h = Building.row_count
        w = Building.column_count
        matrix = np.zeros((h, w), dtype=np.int8)

        for i, row in enumerate(Building.planimetry):
            for j, value in enumerate(row):
                if value == '-':
                    matrix[i, j] = 5
                elif value == '#':
                    matrix[i, j] = 1
                else:
                    matrix[i, j] = 8

        for id in solution.covered_cells:
            cell_id_split = id.split(",")
            matrix[int(cell_id_split[0]), int(cell_id_split[1])] = 6

        for key in solution.connected_cells:
            cell = solution.connected_cells[key]
            matrix[cell.i, cell.j] = 4

        for router in solution.routers:
            matrix[router.cell.i, router.cell.j] = 7

        if cell_to_show:
            for cell in cell_to_show.get_neighbor_cells():
                matrix[cell.i, cell.j] = 2

        fig = plt.figure()

        ax = plt.Axes(fig, (0, 0, 1, 1))
        ax.set_axis_off()
        fig.add_axes(ax)
        dpi = 100
        pixel_per_cell = 3
        fig.set_size_inches(pixel_per_cell * w / dpi, pixel_per_cell * h / dpi)
        ax.imshow(matrix, cmap=plt.cm.gist_ncar, extent=(0, 1, 0, 1), aspect='auto', interpolation='none')

        plt.show()

    @staticmethod
    def print_to_csv(path, file_name, content):
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)

        with open(path + "/" + file_name + '.csv', "a") as file:
            file.write('\n\n' + content)

    @staticmethod
    def dict_to_string(dict):
        string = ''
        for key in dict:
            string += str(key) + ',' + str(dict[key]) + '\n'

        return string

    @staticmethod
    def list_to_string(list):
        string = ''
        for i in list:
            string += str(i[0]) + ',' + str(i[1]) + '\n'

        return string

    @staticmethod
    def to_discrete_results(results, step):
        highest_time = results[len(results) - 1][0]

        distinct_score = []
        for i in range(int(highest_time)):
            if i % step == 0:
                distinct_score.append([i, -1])

        search_index = 0
        for i, result in enumerate(distinct_score):
            second = distinct_score[i][0]
            score = distinct_score[i][1]
            j = search_index
            while j < len(results) - 1:
                if int(results[j][0]) == second:
                    score = results[j][1]
                    search_index = j
                    break
                elif int(results[j][0]) <= second < int(results[j + 1][0]):
                    score = results[j][1]
                    search_index = j
                    break
                elif int(results[j][0]) >= second <= int(results[j + 1][0]):
                    score = results[j][1]
                    search_index = j
                    break
                j += 1

            if score == -1:
                score = results[len(results) - 1][1]

            distinct_score[i][1] = score

        distinct_score.append(results[len(results) - 1])

        return distinct_score
