import numpy as np
import math
import time
from util import buildSolutionFile, SOLUTION_FILE_NAME
from geometry import segmentCircleIntersection
from operator import add

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

        rangeX = self.frange(self.problem.field_limits[0][0], field_min[0], field_max[0], self.problem.pos_step)
        rangeY = self.frange(self.problem.field_limits[1][0], field_min[1], field_max[1], self.problem.pos_step)

        for x in rangeX:
            for y in rangeY:
                defense = [x, y]
                adj_line = [0] * len(scoring_kicks)
                if self.dist(self.opponents_pos, defense, self.problem.robot_radius):
                    for kick in scoring_kicks:
                        if not (segmentCircleIntersection(kick[0],
                        self.anotherPoint(kick[0], kick[1]), defense, self.problem.robot_radius) is None):
                            if segmentCircleIntersection(np.array(posts[0]), np.array(posts[1]),
                            defense, self.problem.robot_radius) is None:
                                adj_line[scoring_kicks.index(kick)] = 1
                                if defense not in self.possible_defs:
                                    self.possible_defs.append(defense)

                    if 1 in adj_line:

                        if (adj_line not in self.adj_mat):
                            self.adj_mat.append(adj_line)
    
                        if (str(adj_line) in self.coord_map):
                            self.coord_map[str(adj_line)].append([x, y])
                                            
                        else:
                            self.coord_map[str(adj_line)] = [[x,y]]

        print("matrix's size = " + str(len(self.adj_mat)) + ", " + str(len(self.adj_mat[0])))
        print(self.coord_map)

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

    def getNeighbours(self, adj_mat, vertex):
        nbFramedShots = len(adj_mat[0])
        neighbours = []

        for i in range(nbFramedShots):
            if vertex[i] == 1:
                neighbours.append(i)

        return neighbours

    def removeNeighbours(self, adj_mat, vertex):
        neighboursToRemove = self.getNeighbours(adj_mat, vertex)

        # Remove his neighbors
        a = np.array(adj_mat)
        a = np.delete(a, neighboursToRemove, axis=1)

        return a.tolist()

    '''
    def getMaxDegreeVertex(self, adj_mat):
        max_degrees = 0
        max_degrees_vertex = []

        for v in adj_mat:
            degrees_nb = v.count(1)
            if (degrees_nb > max_degrees):
                max_degrees_vertex = v
                max_degrees = degrees_nb

        return max_degrees_vertex
    '''

    def getMaxDegreeVertexIndex(self, adj_mat):
        max_degrees = 0
        max_degrees_index = -1

        for i in range(len(adj_mat)):
            degrees_nb = adj_mat[i].count(1)
            if (degrees_nb >= max_degrees):
                max_degrees_index = i
                max_degrees = degrees_nb

        if max_degrees == 0:
            return -1
        return max_degrees_index

    def solve_noExtension(self):
        dominating_set = ([])
        nbFramedShots = len(self.adj_mat[0])
        solutionFound = True

        # Make a copy of the graph
        adj_mat_copy = self.adj_mat.copy()

        while (not self.isDominating(dominating_set, nbFramedShots)):
            # Retrieve the index of the vertex with the highest degree, s
            imax = self.getMaxDegreeVertexIndex(adj_mat_copy)

            # If all vertices have a degree of 0, no solution
            if (imax == -1):
                print("There is no solution!")
                solutionFound = False
                break

            # Remove s and his neighbours
            adj_mat_copy = self.removeNeighbours(adj_mat_copy, adj_mat_copy[imax])

            # Add s to the solution set
            dominating_set.append(self.adj_mat[imax])

        if solutionFound:
            print("Size of the greedy dominating set: " + str(len(dominating_set)))
            for i in range(len(dominating_set)):
                print("Number of shots blocked by the defender ", i, " : ", dominating_set[i].count(1))
            buildSolutionFile(self, dominating_set)
            return True

        return False

    def solve_old(self):
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

        print("Size of the greedy dominating set: " + str(len(dominating_set)))
        for i in range(len(dominating_set)):
            print("Number of shots blocked by the defender ", i, " : ", dominating_set[i].count(1))

        if (dominating_set != ([])):
            buildSolutionFile(self, dominating_set)

    def solve_minDist(self):
        dominating_set = ([])
        nbFramedShots = len(self.adj_mat[0])

        for i in range(len(self.adj_mat)):
            self.degrees.append(self.adj_mat[i].count(1))

        adj_mat_copy = self.adj_mat.copy()

        #while (not self.isDominating(dominating_set, nbFramedShots) and len(dominating_set) < len(self.adj_mat)):
        while (True):
            # Pick vertex with max degree, v
            imax = self.getMaxDegreeVertexIndex(adj_mat_copy)
            vmax = adj_mat_copy[imax]

            if (imax == -1):
                print("mhm")
                break

            #if (self.respectsMinDist(dominating_set, nbFramedShots, self.problem.min_dist)):


            # Remove v and his neighbours
            adj_mat_copy = self.removeNeighbours(adj_mat_copy, adj_mat_copy[imax])

            # Add v to the solution set
            #if self.respectsMinDist(vmax, nbFramedShots, self.problem.min_dist):

            #dominating_set.append(self.adj_mat[imax])

            # Check if solution set is dominant
            if (self.isDominatingAndRespectMinDist(dominating_set, nbFramedShots, self.problem.min_dist)):
                print("Solution found!")
                break

        print("Size of the greedy dominating set: " + str(len(dominating_set)))
        for i in range(len(dominating_set)):
            print("Number of shots blocked by the defender ", i, " : ", dominating_set[i].count(1))

        if (dominating_set != ([])):
            buildSolutionFile(self, dominating_set)

    def solve(self):
        start = time.clock()
        self.buildAdjacencyMatrix()
        print("generation = ", time.clock() - start)
                
        # Pick the correct algorithm to solve the problem depending on the parameters of the problem
        if (not self.problem.min_dist is None):
            return self.solve_minDist()
        else:
            return self.solve_noExtension()
        print("solution = ", time.clock() - start)

    def respectsMinDist(self, subset, nbFramedShots, minDist):
        for i in range(len(subset)):
            # Coordinates 
            coord_i = self.coord_map[str(subset[i])][0]

            # Check if the min distance is respected between all defenders
            for j in range(i, len(subset)):
                coord_j = self.coord_map[str(subset[j])][0]
                if i != j and math.hypot(coord_j[0] - coord_i[0], coord_j[1] - coord_i[1]) <= minDist + 1e-15:
                    return False

             # Check if the min distance isrespected between defenders and opponents
            for o in self.opponents_pos:
                if math.hypot(o[0] - coord_i[0], o[1] - coord_i[1]) <= minDist + 1e-15:
                    return False
 
        return True

    def respectsMinDist2(self, subset, nbFramedShots, minDist):
        for i in range(len(subset)):
            # Coordinates 
            coord_i = self.coord_map[str(subset[i])]
            
            for c_i in coord_i:
                # Check if the min distance is respected between all defenders
                for j in range(i, len(subset)):
                    coord_j = self.coord_map[str(subset[j])][0]
                    for c_j in coord_j:
                        if i != j and math.hypot(coord_j[0] - coord_i[0], coord_j[1] - coord_i[1]) <= minDist + 1e-15:
                            return False

                # Check if the min distance isrespected between defenders and opponents
                for o in self.opponents_pos:
                    if math.hypot(o[0] - coord_i[0], o[1] - coord_i[1]) <= minDist + 1e-15:
                        return False
 
        return True


    # Check if a set is dominating and respect minimum distance in one loop. Returns true if
    # that's the case.
    def isDominatingAndRespectMinDist(self, subset, nbFramedShots, minDist):
        domination = [False] * nbFramedShots

        for i in range(len(subset)):
            for j in range(nbFramedShots):
                if (subset[i][j] == 1):
                    domination[j] = True

            # Coordinates 
            coord_i = self.coord_map[str(subset[i])][0]

            # Check if the min distance is respected between all defenders
            for j in range(i, len(subset)):
                coord_j = self.coord_map[str(subset[j])][0]
                if i != j and math.hypot(coord_j[0] - coord_i[0], coord_j[1] - coord_i[1]) <= minDist + 1e-15:
                    return False

             # Check if the min distance isrespected between defenders and opponents
            for o in self.opponents_pos:
                if math.hypot(o[0] - coord_i[0], o[1] - coord_i[1]) <= minDist + 1e-15:
                    return False

        # Check if it's a dominating set
        for d in domination:
            if d == False:
                return False
 
        return True