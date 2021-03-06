import numpy as np
import math
import itertools
import sys
import time
from util import buildSolutionFile, SOLUTION_FILE_NAME
from itertools import chain, combinations
from geometry import segmentCircleIntersection
from operator import add
from board import maxDist
import array

class Exact :
    def __init__(self, problem):
        self.problem = problem
        self.adj_mat = []
        self.scoring_kicks = []
        self.opponents_pos = []
        self.possible_defs = []

        # Key : adjacency line of a vertex
        # Value : list of possible coordinates matching this adjacency line
        self.coord_map = dict()

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

    # Returns true if <subset> is a dominating set, false otherwise
    def isDominating(self, subset, nbFramedShots):
        domination = [False] * nbFramedShots

        for s in subset:
            for j in range(nbFramedShots):
                if (s[j] == 1):
                    domination[j] = True

        for d in domination:
            if d == False:
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

    # Returns the best possible positions of this set of defenders
    def getBestDefendersPosition(self, defenders):
        # Store the possible cooordinates of each defender according to their adjacency line
        possible_coords = [[] for i in range(len(defenders))]

        # Number of possible coordinates for each defender according to their adjacency line
        nb_coord = []

        # Search all the possible coordinates that match the adjacency lines of the defenders
        for d in range(len(defenders)):
            defender = defenders[d]
            for coord in self.coord_map[str(defender)]:
                possible_coords[d].append(coord)
            nb_coord.append(len(possible_coords[d]))

        defenders_pos = np.zeros((len(defenders), 2))
        best_defenders_pos = []
        max_dist = sys.maxsize

        numLoops = 1
        for i in range(len(defenders)):
            numLoops *= len(possible_coords[i])

        # Fill an array with all possible combinations between the possible coordinates
        for i in range(numLoops):
            for j in range(len(defenders)):
                defenders_pos[j] = possible_coords[j][i % nb_coord[j]]

            # Generate all permutations possible for this set of defenders positions
            all_permut = np.array(list(itertools.permutations(defenders_pos)))

            # Loop though all possible permutations to find the one with a minimum distance between 
            # initial defenders position and solution's defenders position
            for permut in all_permut:
                # Compute the maximum distance that a solution's defender will have to travel to place himself
                dist = maxDist(self.problem.defenders, permut.transpose())

                # Check if this permutation is the best for now
                if dist < max_dist:
                    max_dist = dist
                    best_defenders_pos = permut
                    print("new max dist: " + str(max_dist))

        return (best_defenders_pos, max_dist)

    def solve_noExtension(self):
        # Try to find a minimal dominating set among all possible subsets of blocking positions
        minimalDominantSet = ([])

        # Size of the dominating subset we are looking for
        cpt = 0

        solutionFound = False

        while (not solutionFound and cpt < len(self.adj_mat)+1) :
            print("SEARCHING FOR SUBSETS OF SIZE " + str(cpt))

            # Check if each subset's combination of size <cpt> is a dominating set
            pool = tuple(self.adj_mat)
            n = len(pool)
            if cpt > n:
                return
            indices = list(range(cpt))

            while True:
                subset = tuple(pool[i] for i in indices)
                # If this subset is a dominating set, we found a minimal dominating set, stop the function
                if (self.isDominating(subset, len(self.adj_mat[0]))):
                    minimalDominantSet = subset
                    solutionFound = True
                    break

                for i in reversed(range(cpt)):
                    if indices[i] != i + n - cpt:
                        break
                else:
                    break   # previously return
                indices[i] += 1
                for j in range(i+1, cpt):
                    indices[j] = indices[j-1] + 1

            cpt += 1

        if (solutionFound):
            buildSolutionFile(self, minimalDominantSet)
            return True
        else:
            print("There is no solution!")
            return False
    
    def solve_initialPosDefenders(self):
        dominating_sets = []
        max_dist = sys.maxsize
        best_defenders_pos = []
        # Size of the dominating subset we are looking for
        subsetSize = self.problem.getNbDefenders()

        print("SEARCHING FOR SUBSETS OF SIZE " + str(self.problem.getNbDefenders()))

        # Check if each subset's combination that has the same size as the number of defenders is a dominating set
        pool = tuple(self.adj_mat)
        n = len(pool)
        if subsetSize > n:
            return
        indices = list(range(subsetSize))

        while True:
            subset = tuple(pool[i] for i in indices)
            # If this subset is a dominating set, check if it will minimize 
            # the distance between the initial positions and the blocking positions
            if (self.isDominating(subset, len(self.adj_mat[0]))):
                if subset not in dominating_sets:
                    dominating_sets.append(subset)
                     # Look for the best defenders' positions matching this adjacency line
                    (defenders_pos, dist) = self.getBestDefendersPosition(subset)

                    # Update the solution if we found a better one
                    if dist < max_dist:
                        max_dist = dist
                        best_defenders_pos = defenders_pos

            for i in reversed(range(subsetSize)):
                if indices[i] != i + n - subsetSize:
                    break
            else:
                break   # previously return
            indices[i] += 1
            for j in range(i+1, subsetSize):
                indices[j] = indices[j-1] + 1  

        if (best_defenders_pos == []):
            print("there is no solution with this configuration :-(")
            return False

        else:
            # Write in the solution file
            solFile = open(SOLUTION_FILE_NAME, "w+")
            solFile.write("{\"defenders\":[")
            for i in range(len(best_defenders_pos)):
                coordinates = [ best_defenders_pos[i][0], best_defenders_pos[i][1] ]
                solFile.write("[" + str(coordinates[0]) + "," + str(coordinates[1]) + "]")
                if i < len(best_defenders_pos) - 1:
                    solFile.write(",")
            solFile.write("]}")
            solFile.close()
            return True

    def solve_minDist(self):
        # Try to find a minimal dominating set among all possible subsets of blocking positions
        minimalDominantSet = ([])

        # Size of the dominating subset we are looking for
        cpt = 0
        
        solutionFound = False

        while (not solutionFound and cpt < len(self.adj_mat)+1) :
            print("SEARCHING FOR SUBSETS OF SIZE " + str(cpt))
            
            # Check if each subset's combination of size <cpt> is a dominating set and respects the minimum
            # distance between robots
            pool = tuple(self.adj_mat)
            n = len(pool)
            if cpt > n:
                return
            indices = list(range(cpt))

            while True:
                subset = tuple(pool[i] for i in indices)
                # If this subset is a dominating set and it respects the minimum distance, we found a minimal dominating set, stop the function
                if (self.isDominatingAndRespectMinDist(subset, len(self.adj_mat[0]), self.problem.min_dist)):
                    minimalDominantSet = subset
                    solutionFound = True
                    break

                for i in reversed(range(cpt)):
                    if indices[i] != i + n - cpt:
                        break
                else:
                    break   # previously return
                indices[i] += 1
                for j in range(i+1, cpt):
                    indices[j] = indices[j-1] + 1
         
            cpt += 1

        if (solutionFound):
            buildSolutionFile(self, minimalDominantSet)
            return True
        else:
            print("There is no solution!")
            return False

    def solve(self):
        start = time.clock()
        result = 0
        self.buildAdjacencyMatrix()
        print("generation = ", time.clock() - start)
                
        # Pick the correct algorithm to solve the problem depending on the parameters of the problem
        if (not self.problem.min_dist is None):
            result = self.solve_minDist()
        elif (not self.problem.defenders is None):
            result = self.solve_initialPosDefenders()
        else:
            result = self.solve_noExtension()
        print("solution = ", time.clock() - start)
        return result
