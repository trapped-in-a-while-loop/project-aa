import numpy as np
import math
import time
from geometry import *
from operator import add

SOLUTION_FILE_NAME = "solution.json"

class Glouton:
    def __init__(self, problem):
        self.adj_mat = list()
        self.problem = problem
        self.coord_map = dict()

    def anotherPoint(self, old_point, angle):
        x = 1000 * math.cos(angle)
        y = 1000 * math.sin(angle)
        new_point = np.array([old_point[0] + x, old_point[1] + y])
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

        self.possible_defs = []
        for x in self.frange(self.problem.field_limits[0][0], self.problem.field_limits[0][1],
        self.problem.pos_step):
            for y in self.frange(self.problem.field_limits[1][0], self.problem.field_limits[1][1],
            self.problem.pos_step):
                defense = [x, y]
                adj_line = [0] * len(scoring_kicks)
                if self.dist(self.possible_defs, defense, self.problem.robot_radius):
                    if self.dist(opponents, defense, self.problem.robot_radius):
                        for kick in scoring_kicks:
                            i = segmentCircleIntersection(kick[0],
                            self.anotherPoint(kick[0], kick[1]), defense, self.problem.robot_radius)
                            if not (i is None):
                                 if i[0] < goal.posts[0][0]:
                                    adj_line[scoring_kicks.index(kick)] = 1
                                    self.possible_defs.append(defense)
                                    
                        if 1 in adj_line:
                            self.adj_mat.append(adj_line)
                            self.coord_map[str(adj_line)] = (x, y)

    # Returns true if <subset> is a dominating set, false otherwise
    def isDominating(self, subset, nbPotentialGoals):
        domination = [False] * nbPotentialGoals

        for s in subset:
            for j in range(nbPotentialGoals):
                if (s[j] == 1):
                    domination[j] = True

        for d in domination:
            if d == False:
                return False
        return True

    def solve(self):
        self.buildAdjacencyMatrix()
        print(self.adj_mat)

        degrees = ([])
        dominating_set = ([])

        for i in range(len(self.adj_mat)):
            degrees.append(self.adj_mat[i].count(1))

            print(len(dominating_set))

        while (not self.isDominating(dominating_set, len(self.adj_mat[0]))) and (len(dominating_set) < len(self.adj_mat)):
            s = degrees.index(max(degrees))
            if not self.adj_mat[s] in dominating_set:
                dominating_set.append(self.adj_mat[s])
            degrees[s] = 0

            for i in range(len(self.adj_mat[s])):
                if self.adj_mat[s][i] == 1:
                    for j in range(len(self.adj_mat)):
                        if self.adj_mat[j][i] == 1:
                            degrees[j] -= 1 

        print("size dom set: " + str(len(dominating_set)))
        for i in dominating_set:
            print(str(i.count(1)) + ", ")

        if (dominating_set != ([])):
            print("Le sous ensemble dominant est ")
            print(dominating_set)
            print("Cela correspond aux positions ")
            for s in dominating_set:
                print(self.coord_map[str(s)])
            self.buildSolutionFile(dominating_set)
            
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