from utils import Utils


class Building:
    planimetry = []
    column_count = 0
    row_count = 0
    back_bone_cell = {}
    infrastructure_budget = 0.0
    back_bone_cost = 0.0
    target_cells = []
    target_cells_set = {}

    @staticmethod
    def get_target_cells_set():
        if len(Building.target_cells_set) == 0:
            Building.target_cells_set = Utils.list_to_set(Building.target_cells, "id")

        return Building.target_cells_set
