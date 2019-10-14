import numpy as np
import math
import networkx as nx
import matplotlib.pyplot as plt
from itertools import chain, combinations
from geometry import segmentCircleIntersection
from operator import add

SOLUTION_FILE_NAME = "solution.json"

class Exact :
    def __init__(self, problem):
        self.problem = problem
        self.adj_mat = []
        self.scoring_kicks = []
        self.possible_defs = []
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

        for i in self.adj_mat:
            print(i)
        
        print("matrix's size = " + str(len(self.adj_mat)) + ", " +
        str(len(self.adj_mat[0])))


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
        M = self.adj_mat

        # Try to find a minimal dominating set among all possible subsets of blocking positions
        minimalDominantSet = ([])
        i = 1
        solutionFound = False

        while (not solutionFound and i < len(M)+1) :
            # Set of all subsets of blocking positions of size i-1 (sorted by size)
            subsets = list(chain.from_iterable(combinations(M, r) for r in range(i-1, i)))

            for s in subsets:
                # Break the loop if a dominating set is found
                if (self.isDominating(s, len(M[0]))):
                    minimalDominantSet = s
                    solutionFound = True
                    break
            i += 1

        if (minimalDominantSet != ([])):
            print("Le sous ensemble minimal est ")
            print(minimalDominantSet)
            print("Cela correspond aux positions ")
            for s in minimalDominantSet:
                print(self.coord_map[str(s)])
            self.buildSolutionFile(minimalDominantSet)
       
        else:
            print("Il n'y a pas de sous ensemble dominant! C'est dommage")

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

    def drawGraph(self):
        G = nx.Graph()
        left_nodes = nx.Graph()
        
        for i in range(len(self.adj_mat)):
            G.add_node(i)
            if i < self.adj_mat[0]:
                left_nodes.add_node(i)

            for j in range(len(self.adj_mat[i])):
                if (self.adj_mat[i][j] == 1):
                    G.add_edge(i, j)

        nx.draw(G)
        plt.subplot(121)
        print("Drawing graph ...")
        nx.draw_networkx(G, pos = nx.drawing.layout.bipartite_layout(G, left_nodes))
        plt.show()
