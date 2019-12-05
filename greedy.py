import numpy as np
import math
import time
from util import buildSolutionFile, SOLUTION_FILE_NAME
from geometry import segmentCircleIntersection
from operator import add

SOLUTION_FILE_NAME = "solution.json"

class Glouton:
    def __init__(self, problem):
        self.adj_mat = []
        self.problem = problem
        self.opponents_pos = []
        self.possible_defs = []

        # Key : adjacency line of a vertex
        # Value : list of possible coordinates matching this adjacency line
        self.coord_map = dict()

        # Store the degrees of every vertex. The index corresponds to the index in the adjacency matrix
        self.degrees = ([])

    def anotherPoint(self, old_point, angle):
        x = 1000 * math.cos(angle)
        y = 1000 * math.sin(angle)
        new_point = np.array(list(map(add, old_point, [x, y])))
        return new_point

    def frange(self, start, min, max, step):
        i = start
        result = list()
        while i < max:
            if (i > min):
                result.append(i)
            i += step
        return result

    def dist(self, opponents, defense, robot_radius):
        result = True
        for opponent in opponents:
            if (math.hypot(defense[0] - opponent[0], defense[1] - opponent[1]) <
                (robot_radius * 2)):
                result = False
        return result

    def buildAdjacencyMatrix(self):
        field_min = [min(np.concatenate((self.problem.opponents[0], self.problem.goals[0].posts[0]))), min(np.concatenate((self.problem.opponents[1], self.problem.goals[0].posts[1])))]
        field_max = [max(np.concatenate((self.problem.opponents[0], self.problem.goals[0].posts[0]))), max(np.concatenate((self.problem.opponents[1], self.problem.goals[0].posts[1])))]

        for i in range(len(self.problem.opponents[0])):
            self.opponents_pos.append([self.problem.opponents[0][i], self.problem.opponents[1][i]])

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

        rangeX = self.frange(self.problem.field_limits[0][0], field_min[0], field_max[0] + self.problem.pos_step, self.problem.pos_step)
        rangeY = self.frange(self.problem.field_limits[1][0], field_min[1], field_max[1] + self.problem.pos_step, self.problem.pos_step)

        for x in rangeX:
            for y in rangeY:
                defense = [x, y]
                adj_line = [0] * len(scoring_kicks)
                #adj_line = array.array('B', [0] * len(scoring_kicks))
                if self.dist(self.possible_defs, defense, self.problem.robot_radius):
                    if self.dist(self.opponents_pos, defense, self.problem.robot_radius):
                        for kick in scoring_kicks:
                            if not (segmentCircleIntersection(kick[0],
                            self.anotherPoint(kick[0], kick[1]), defense, self.problem.robot_radius) is None):
                                if segmentCircleIntersection(np.array(posts[0]), np.array(posts[1]),
                                defense, self.problem.robot_radius) is None:
                                    adj_line[scoring_kicks.index(kick)] = 1
                                    self.possible_defs.append(defense)

                        if 1 in adj_line:
                            self.adj_mat.append(adj_line)
    
                            if (str(adj_line) in self.coord_map):
                                self.coord_map[str(adj_line)].append([x, y])
                                            
                            else:
                                self.coord_map[str(adj_line)] = [[x,y]]

        print("matrix's size = " + str(len(self.adj_mat)) + ", " + str(len(self.adj_mat[0])))

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
        dominating_set = ([])

        for i in range(len(self.adj_mat)):
            self.degrees.append(self.adj_mat[i].count(1))

        while (not self.isDominating(dominating_set, len(self.adj_mat[0])) and len(dominating_set) < len(self.adj_mat)):
            # s = vertex with the highest degree
            s = self.degrees.index(max(self.degrees))

            # if this vertex is not in the dominating set, add it
            if not self.adj_mat[s] in dominating_set:
                dominating_set.append(self.adj_mat[s])

            # Set its degree to 0 so it won't be picked again
            self.degrees[s] = 0

            for i in range(len(self.adj_mat[s])):
                if self.adj_mat[s][i] == 1:
                    for j in range(len(self.adj_mat)):
                        if self.adj_mat[j][i] == 1:
                            self.degrees[j] -= 1 

        print("size dom set: " + str(len(dominating_set)))
        for i in dominating_set:
            print(str(i.count(1)) + ", ")

        if (dominating_set != ([])):
            print("Le sous ensemble dominant est ")
            print(dominating_set)
            print("Cela correspond aux positions ")
            for s in dominating_set:
                print(self.coord_map[str(s)])
            buildSolutionFile(self, dominating_set)