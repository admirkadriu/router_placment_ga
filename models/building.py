from models.cell import Cell


class Building:
    planimetry = []
    column_count = 0
    row_count = 0
    back_bone_cell = {}
    infrastructure_budget = 0.0
    back_bone_cost = 0.0
    target_cells = {}

    @staticmethod
    def get_covered_cells(routers):
        covered_cells_map = {}
        for router in routers:
            current_covered_cells = router.get_target_cells_covered()
            for cell in current_covered_cells:
                covered_cells_map[cell.id] = cell

        return covered_cells_map.values()
