import random

from models.building import Building
from models.solution import Solution


class Crossover:
    def __init__(self, parents):
        self.parents = parents
        self.defaultHeight = random.randint(3, int(Building.row_count / 3))
        self.defaultWidth = random.randint(3, int(Building.column_count / 3))
        self.couples = []
        self.make_couples()

    def make_couples(self):
        available_parents = {key: parent for key, parent in enumerate(self.parents)}

        while len(available_parents) > 1:
            key1 = random.choice(list(available_parents))
            p1 = available_parents[key1]
            del available_parents[key1]
            key2 = random.choice(list(available_parents))
            p2 = available_parents[key2]
            del available_parents[key2]
            self.couples.append([p1, p2])

        if len(available_parents) == 1:
            p1 = list(available_parents.values())[0]
            other_parents = list(filter(lambda p: p.id != p1.id, self.parents))
            p2 = random.choice(other_parents)
            self.couples.append([p1, p2])

    def rectangle(self, height=None, width=None):
        children = []
        if height is None:
            height = self.defaultHeight
        if width is None:
            width = self.defaultWidth

        i = random.randint(0, Building.row_count - height)
        j = random.randint(0, Building.column_count - width)

        for couple in self.couples:
            p1, p2 = couple

            inside_rp1, outside_rp1 = p1.split_routers_with_rectangle(i, j, height, width)
            inside_rp2, outside_rp2 = p2.split_routers_with_rectangle(i, j, height, width)

            child1 = Solution()
            child1.set_routers(inside_rp1 + outside_rp2)
            if child1.get_score() > p1.get_score() and child1.get_score() > p2.get_score():
                children.append(child1)
                print("New child", child1.get_score())

            child2 = Solution()
            child2.set_routers(inside_rp2 + outside_rp1)
            if child2.get_score() > p2.get_score() and child2.get_score() > p1.get_score():
                children.append(child2)
                print("New child", child2.get_score())

        return children

    def mid_point(self):
        children = []
        for couple in self.couples:
            p1, p2 = couple
            i1, j1 = p1.get_midpoint()
            i2, j2 = p2.get_midpoint()
            i = (i1 + i2) / 2
            j = (j1 + j2) / 2

            first_quarter = p1.get_inside_rectangle(0, 0, i + 1, j + 1)
            second_quarter = p2.get_inside_rectangle(0, j, i + 1, Building.column_count - j)
            third_quarter = p1.get_inside_rectangle(i, 0, Building.row_count - i, j + 1)
            fourth_quarter = p2.get_inside_rectangle(i, j, Building.row_count - i, Building.column_count - j)

            child1 = Solution()
            child1.set_routers(first_quarter + second_quarter + third_quarter + fourth_quarter)
            if child1.get_score() > p1.get_score() or child1.get_score() > p2.get_score():
                children.append(child1)
                print("New child", child1.get_score())

        return children
