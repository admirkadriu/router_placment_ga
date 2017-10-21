from models.cell import Cell
from utils import Utils


class Building:
    planimetry = []
    column_count = 0
    row_count = 0
    back_bone_cell = {}
    infrastructure_budget = 0.0
    back_bone_cost = 0.0
    target_cells = []
    target_cells_dict = {}

    @staticmethod
    def get_covered_cells(routers):
        covered_cells = {}
        for router in routers:
            current_covered_cells = router.get_target_cells_covered()
            covered_cells.update(current_covered_cells)

        return covered_cells

    @staticmethod
    def get_target_cells_dict():
        if len(Building.target_cells_dict) == 0:
            Building.target_cells_dict = Utils.list_to_dict(Building.target_cells, "id")

        return Building.target_cells_dict
