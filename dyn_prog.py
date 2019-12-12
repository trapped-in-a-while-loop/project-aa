import numpy as np
import math
import itertools
import sys
from util import buildSolutionFile, SOLUTION_FILE_NAME
from itertools import chain, combinations
from geometry import segmentCircleIntersection
from operator import add
from board import maxDist
import array

class DynProg :
    def __init__(self, problem):
        self.problem = problem
        self.adj_mat = []
        self.scoring_kicks = []
        self.opponents_pos = []
        self.possible_defs = []
        self.nb_kicks_per_opponent = [0] * len(self.problem.opponents[0])

        # Key : adjacency line of a vertex
        # Value : list of possible coordinates matching this adjacency line
        self.coord_map = dict()

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
                        self.nb_kicks_per_opponent[i] += 1
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

    def solve_noExtension():
        minimalDominantSet = ([])
        print("number of kick per opponent: ", self.nb_kicks_per_opponent)

        return minimalDominantSet

    def solve(self):
        self.buildAdjacencyMatrix()
        minimalDominantSet = self.solve_noExtension()

        if (minimalDominantSet != ([])):
            print("Le sous ensemble minimal est ")
            print(minimalDominantSet)
            print("Cela correspond aux positions ")
            for i in range(len(minimalDominantSet)):
                print(self.coord_map[str(minimalDominantSet[i])][0])
            buildSolutionFile(self, minimalDominantSet)
        
        else:
            print("Il n'y a pas de sous ensemble dominant! C'est dommage")
