import logging
import sys
import time

import matplotlib.pyplot as plt
import numpy as np

from models.cell import Cell


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
        args = args + (time.strftime("%H:%M:%S"),)
        Utils.logger.info(args)

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
            for cell in cell_to_show.get_neighbors_cells():
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
