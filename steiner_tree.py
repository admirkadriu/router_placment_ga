#!/usr/local/bin/python
"""Steiner.py
Author: Clint Cooper
Date: 12/15/14
The code that follows is not optimal nor is it well organized but it does work. 
It solves the Minimum Steiner Problem in relatively small time with Rectilinear 
Space in O(n^3 * logn) and Graphical Space in O(n^4 * logn)

Note to self: Add comments and organization to the functions.
Note to reader: Sorry for the lack of comments and organization. See above. 
"""

import math

from enums.CellType import CellType
from models.cell import Cell
from models.router import Router
from utils import Utils


class UnionFind:
    """Union-find data structure.

    Each unionFind instance X maintains a family of disjoint sets of
    hashable objects, supporting the following two methods:

    - X[item] returns a name for the set containing the given item.
      Each set is named by an arbitrarily-chosen one of its members; as
      long as the set remains unchanged it will keep the same name. If
      the item is not yet part of a set in X, a new singleton set is
      created for it.

    - X.union(item1, item2, ...) merges the sets containing each item
      into a single larger set.  If any item is not yet part of a set
      in X, it is added to X as one of the members of the merged set.
    """

    def __init__(self):
        """Create a new empty union-find structure."""
        self.weights = {}
        self.parents = {}

    def __getitem__(self, object):
        """Find and return the name of the set containing the object."""

        # check for previously unknown object
        if object not in self.parents:
            self.parents[object] = object
            self.weights[object] = 1
            return object

        # find path of objects leading to the root
        path = [object]
        root = self.parents[object]
        while root != path[-1]:
            path.append(root)
            root = self.parents[root]

        # compress the path and return
        for ancestor in path:
            self.parents[ancestor] = root
        return root

    def __iter__(self):
        """Iterate through all items ever found or unioned by this structure."""
        return iter(self.parents)

    def union(self, *objects):
        """Find the sets containing the objects and merge them all."""
        roots = [self[x] for x in objects]
        heaviest = max([(self.weights[r], r) for r in roots])[1]
        for r in roots:
            if r != heaviest:
                self.weights[heaviest] += self.weights[r]
                self.parents[r] = heaviest


class Point:
    """Point Class for Steiner.py
    Contains position in x and y values with degree of edges representative of the length of
    the list of edges relative to the MST
    """

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.deg = 0
        self.edges = []
        self.MSTedges = []

    def update(self, edge):
        self.edges.append(edge)

    def reset(self):
        self.edges = []
        self.deg = 0
        self.MSTedges = []

    def MSTupdate(self, edge):
        self.deg += 1
        self.MSTedges.append(edge)


class Line:
    """Line Class for Steiner.py
    Contains the two end points as well as the weight of the line.
    Supports determining the first or last point as well as the other given one.
    """

    def __init__(self, p1, p2, w):
        self.points = []
        self.points.append(Ref(p1))
        self.points.append(Ref(p2))
        self.w = w

    def getOther(self, pt):
        if pt == self.points[0].get():
            return self.points[1]
        elif pt == self.points[1].get():
            return self.points[0]
        else:
            print("This is an Error. The line does not contain points that make sense.")

    def getFirst(self):
        return self.points[0]

    def getLast(self):
        return self.points[1]


class Ref:
    """ref Class for use in Steiner.py
    Satisfies the need for pointers to maintain a constant and updated global list of things.
    """

    def __init__(self, obj):
        self.obj = obj

    def get(self):
        return self.obj

    def set(self, obj):
        self.obj = obj


def kruskal_alg(set_of_points, type):
    """Kruskal's Algorithm
    Sorts edges by weight, and adds them one at a time to the tree while avoiding cycles
    Takes any set of Point instances and converts to a dictionary via edge crawling
    Takes the dictionary and iterates through each level to discover neighbors and weights
    Takes list of point index pairs and converts to list of Lines then returns
    """

    for i in range(0, len(set_of_points)):
        set_of_points[i].reset()
    for i in range(0, len(set_of_points)):
        for j in range(i, len(set_of_points)):
            if i != j:
                if type == "R":
                    dist = (abs(set_of_points[i].x - set_of_points[j].x)
                            + abs(set_of_points[i].y - set_of_points[j].y))
                elif type == "G":
                    dist = math.sqrt(pow((set_of_points[i].x - set_of_points[j].x), 2) +
                                     pow((set_of_points[i].y - set_of_points[j].y), 2))
                else:
                    "All of the Errors!"
                line = Line(set_of_points[i], set_of_points[j], dist)
                set_of_points[i].update(line)
                set_of_points[j].update(line)
            else:
                dist = 100000
                line = Line(set_of_points[i], set_of_points[j], dist)
                set_of_points[i].update(line)

    G = {}
    for i in range(0, len(set_of_points)):
        off = 0
        subset = {}
        for j in range(0, len(set_of_points[i].edges)):
            subset[j] = set_of_points[i].edges[j].w
        G[i] = subset

    subtrees = UnionFind()
    tree = []
    for W, u, v in sorted((G[u][v], u, v) for u in G for v in G[u]):
        if subtrees[u] != subtrees[v]:
            tree.append([u, v])
            subtrees.union(u, v)

    MST = []
    for i in range(0, len(tree)):
        point1 = set_of_points[tree[i][0]]
        point2 = set_of_points[tree[i][1]]
        for j in range(0, len(point1.edges)):
            if point2 == point1.edges[j].getOther(point1).get():
                point1.MSTupdate(point1.edges[j])
                point2.MSTupdate(point1.edges[j])
                MST.append(point1.edges[j])
    return MST


def delta_mst(set_of_points, test_point, type):
    """DeltaMST
    Determines the difference in a MST's total weight after adding a point.
    """

    if type == "R":
        MST = kruskal_alg(set_of_points, "R")
    else:
        MST = kruskal_alg(set_of_points, "G")

    cost1 = 0
    for i in range(0, len(MST)):
        cost1 += MST[i].w

    combo = set_of_points + [test_point]

    if type == "R":
        MST = kruskal_alg(combo, "R")
    else:
        MST = kruskal_alg(combo, "G")

    cost2 = 0
    for i in range(0, len(MST)):
        cost2 += MST[i].w
    return cost1 - cost2


def get_cost(set_of_points):
    lines = kruskal_alg(set_of_points, "G")

    cost1 = 0
    for i in range(0, len(lines)):
        cost1 += lines[i].w

    return cost1


def hanan_points(SetOfPoints):
    """HananPoints
    Produces a set of HananPoints of type Points
    """
    totalSet = SetOfPoints
    SomePoints = []
    for i in range(0, len(totalSet)):
        for j in range(i, len(totalSet)):
            if i != j:
                SomePoints.append(Point(totalSet[i].x, totalSet[j].y))
                SomePoints.append(Point(totalSet[j].x, totalSet[i].y))
    return SomePoints


def brute_points(SetOfPoints):
    """BrutePoints
    Produces points with spacing 10 between x values and y values between maximal and minimal
    existing points.
    This could use some work...
    """
    if SetOfPoints != []:
        some_points = set()
        xmax = (max(SetOfPoints, key=lambda x: x.x)).x
        xmin = (min(SetOfPoints, key=lambda x: x.x)).x
        ymax = (max(SetOfPoints, key=lambda x: x.y)).y
        ymin = (min(SetOfPoints, key=lambda x: x.y)).y

        rangex = range(xmin, xmax)
        rangey = range(ymin, ymax)
        for i in rangex[::Router.radius]:
            for j in rangey[::Router.radius]:
                if Cell.get(i, j).get_type() == CellType.TARGET.value:
                    point = Point(i, j)
                    some_points.add(get_point_id(point))
        return some_points
    else:
        return set()


def get_point_id(point):
    return str(point.x) + "," + str(point.y)


def computeGSMT(original_points):
    """computeGSMT
    Computes the Euclidean Graphical Steiner Minimum Spanning Tree
    Uses BrutePoints as a candidate set of points for possible steiner points. (Approximation factor of <= 2)
    DeltaMST is used to determine which points are beneficial to the final tree.
    Any point with less than two degree value (two or fewer edges) is not helpful and is removed.
    All final points are printed to the canvas.
    """
    graph_steiner_points = get_steiner_points(original_points)
    gsmt = kruskal_alg(original_points + graph_steiner_points, "G")

    return gsmt


def get_steiner_points(original_points):
    Utils.log("Points to consider: ", len(original_points))
    graph_steiner_points = []

    candidate_set_len = 1
    blacklisted_points = set()
    initial_cost = None
    while candidate_set_len > 0:
        best_point = Point(0, 0)

        candidate_set_len = 0
        best_cost = 0
        if initial_cost is None:
            initial_cost = get_cost(original_points + graph_steiner_points)

        brute_points_set = brute_points(original_points + graph_steiner_points)
        brute_points_set = brute_points_set.difference(blacklisted_points)
        if len(blacklisted_points) > 0:
            print(len(blacklisted_points))
        for key in brute_points_set:
            i, j = Utils.get_position_from_id(key)
            point = Point(i, j)
            after_cost = get_cost(original_points + graph_steiner_points + [point])
            delta_cost = initial_cost - after_cost
            if (get_point_id(point)) in blacklisted_points:
                continue

            if delta_cost > 0:
                candidate_set_len += 1
            elif delta_cost < -Router.radius:
                blacklisted_points.add(key)

            if delta_cost > best_cost:
                best_point = point
                best_cost = delta_cost

        if best_point.x != 0 and best_point.y != 0:
            graph_steiner_points.append(best_point)
            initial_cost = None

        for point in graph_steiner_points:
            if point.deg <= 2:
                graph_steiner_points.remove(point)
                blacklisted_points.add(get_point_id(point))
                initial_cost = None

        Utils.log("steiner len:", len(graph_steiner_points), candidate_set_len)

    Utils.log("Steiner points added: ", len(graph_steiner_points))

    return points_to_list(graph_steiner_points)

def points_to_list(points):
    ls = []
    for point in points:
        ls.append([point.x, point.y])
    return ls



def computeGMST(original_points):
    """computeGMST
    Computes the Euclidean (Graphical) Minimum Spanning Tree
    Uses Kruskals to determine the MST of some set of global points and prints to canvas
    """
    return kruskal_alg(original_points, "G")
