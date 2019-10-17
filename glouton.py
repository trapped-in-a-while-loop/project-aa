import numpy as np
import math
from geometry import segmentCircleIntersection
from operator import add

SOLUTION_FILE_NAME = "solution.json"

class Glouton:
    def __init__(self, problem):
        self.adj_mat = []
        self.problem = problem
        self.coord_map = dict()

    def anotherPoint(self, old_point, angle):
        x = 1000 * math.cos(angle)
        y = 1000 * math.sin(angle)
        new_point = np.array(list(map(add, old_point, [x, y])))
        return new_point

    def frange(self, start, stop, step):
        i = start
        while i < stop:
            yield i
            i += step

    def dist(self, opponents, defense, robot_radius):
        result = True
        for opponent in opponents:
            if (math.hypot(defense[0] - opponent[0], defense[1] - opponent[1]) <
                (robot_radius * 2)):
                result = False
        return result

    def buildAdjacencyMatrix(self):
        opponents = []
        for i in range(len(self.problem.opponents[0])):
            opponents.append([self.problem.opponents[0][i], self.problem.opponents[1][i]])

        posts = []
        for i in range(len(self.problem.goals)):
            posts.append([self.problem.goals[i].posts[0][0],
            self.problem.goals[i].posts[1][0]])
            posts.append([self.problem.goals[i].posts[0][1],
            self.problem.goals[i].posts[1][1]])

        scoring_kicks = []
        for i in range(len(self.problem.opponents[0])):
            opponent = [self.problem.opponents[0][i], self.problem.opponents[1][i]]
            direction = 0
            while direction < 2 * math.pi:
                for goal in self.problem.goals:
                    if not (goal.kickResult(opponent, direction) is None):
                        """ 4 next lines to correct incomprehensible kickResult()'s
                            behavior """
                        if (direction > math.pi):
                            scoring_kicks.append([opponent, direction - math.pi])
                        elif (direction < math.pi):
                            scoring_kicks.append([opponent, direction + math.pi])
                direction += self.problem.theta_step

        possible_defs = []
        for x in self.frange(self.problem.field_limits[0][0], self.problem.field_limits[0][1],
        self.problem.pos_step):
            for y in self.frange(self.problem.field_limits[1][0], self.problem.field_limits[1][1],
            self.problem.pos_step):
                defense = [x, y]
                adj_line = [0] * len(scoring_kicks)
                if defense not in possible_defs:
                    if defense not in posts:
                        if self.dist(opponents, defense, self.problem.robot_radius):
                            for kick in scoring_kicks:
                                if not (segmentCircleIntersection(kick[0],
                                self.anotherPoint(kick[0], kick[1]), defense, self.problem.robot_radius)
                                is None):
                                    adj_line[scoring_kicks.index(kick)] = 1
                                    possible_defs.append(defense)
                            if 1 in adj_line:
                                self.adj_mat.append(adj_line)
                                self.coord_map[str(adj_line)] = (x, y)

    def solve(self):
        self.buildAdjacencyMatrix()

        non_black_unsorted = list()
        self.dominating_set = list()
        colours = ["White"] * (len(self.adj_mat) + len(self.adj_mat[0]))
        color = list()

        for i in range(len(self.adj_mat)):
            non_black_unsorted.append(self.adj_mat[i].count(1) + 1)

        non_black_sorted = non_black_unsorted
        non_black_sorted.sort()

        coloured = 0
        current_degree = -1
        all_coloured = False
        while coloured < len(self.adj_mat):

            current_node = non_black_unsorted.index(non_black_sorted[current_degree])
            all_coloured = True
            for i in range(len(self.adj_mat[0])):
                if self.adj_mat[current_node][i] == 1 and colours[len(self.adj_mat) + i] == "White":
                    colours[i] = "Grey"
                    coloured += 1
                    all_coloured = False
            if not all_coloured:
                if colours[current_node] == "White":
                    coloured += 1
                colours[current_node] = "Black"
            non_black_unsorted[current_node] = -1
            current_degree -= 1

        dominantSet = []

        print("The dominating set is: ")
        for i in range(len(self.adj_mat)):
            if colours[i] == "Black":
                print(str(i + 1) + " ")
                dominantSet.append(self.adj_mat[i])

        print("size dom set: " + str(len(dominantSet)))
        self.buildSolutionFile(dominantSet)

    def buildSolutionFile(self, minSet):
        solFile = open(SOLUTION_FILE_NAME, "w+")
        solFile.write("{\"defenders\":[")
        for i in range(len(minSet)):
            coordinates = self.coord_map[str(minSet[i])]
            solFile.write("[" + str(coordinates[0]) + "," + str(coordinates[1]) + "]")
            if i < len(minSet) - 1:
                solFile.write(",")
        solFile.write("]}")
        solFile.close()