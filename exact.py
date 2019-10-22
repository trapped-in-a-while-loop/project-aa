import numpy as np
import math
from util import buildSolutionFile, SOLUTION_FILE_NAME
from itertools import chain, combinations
from geometry import segmentCircleIntersection
from operator import add

class Exact :
    def __init__(self, problem):
        self.problem = problem
        self.adj_mat = []
        self.scoring_kicks = []
        self.opponents_pos = []
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

        possible_defs = []
        for x in self.frange(self.problem.field_limits[0][0], self.problem.field_limits[0][1],
        self.problem.pos_step):
            for y in self.frange(self.problem.field_limits[1][0], self.problem.field_limits[1][1],
            self.problem.pos_step):
                defense = [x, y]
                adj_line = [0] * len(scoring_kicks)
                if defense not in possible_defs:
                    if defense not in posts:
                        if self.dist(self.opponents_pos, defense, self.problem.robot_radius):
                            for kick in scoring_kicks:
                                if not (segmentCircleIntersection(kick[0],
                                self.anotherPoint(kick[0], kick[1]), defense, self.problem.robot_radius)
                                is None):
                                    adj_line[scoring_kicks.index(kick)] = 1
                                    possible_defs.append(defense)
                            if 1 in adj_line:
                                self.adj_mat.append(adj_line)
                                self.coord_map[str(adj_line)] = (x, y)

        #for i in self.adj_mat:
        #    print(i)
        
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

    # Not used
    def respectMinDist(self, subset, minDist):
        for i in range(len(subset)):
            coord = self.coord_map[str(subset[i])]

            # Check if the min distance is respected between all defenders
            for j in range(i, len(subset)):
                coord2 = self.coord_map[str(subset[j])]
                if i != j and math.hypot(coord2[0] - coord[0], coord2[1] - coord[1]) < minDist:
                    return False

             # Check if the min distance isrespected between defenders and opponents
            for o in self.opponents_pos:
                if math.hypot(o[0] - coord[0], o[1] - coord[1]) < minDist:
                    return False
        return True

    # Check if a set is dominating and respect minimum distance in one loop. Returns true if
    # that's the case.
    def isDominatingAndRespectMinDist(self, subset, nbPotentialGoals, minDist):
        domination = [False] * nbPotentialGoals

        for i in range(len(subset)):
            for j in range(nbPotentialGoals):
                if (subset[i][j] == 1):
                    domination[j] = True

            coord_i = self.coord_map[str(subset[i])]

            # Check if the min distance is respected between all defenders
            for j in range(i, len(subset)):
                coord_j = self.coord_map[str(subset[j])]
                if i != j and math.hypot(coord_j[0] - coord_i[0], coord_j[1] - coord_i[1]) < minDist:
                    return False

             # Check if the min distance isrespected between defenders and opponents
            for o in self.opponents_pos:
                if math.hypot(o[0] - coord_i[0], o[1] - coord_i[1]) < minDist:
                    return False

        # Check if it's a dominating set
        for d in domination:
            if d == False:
                return False
 
        return True

    def solve_noExtension(self):
        # Try to find a minimal dominating set among all possible subsets of blocking positions
        minimalDominantSet = ([])
        i = 1
        solutionFound = False

        while (not solutionFound and i < len(self.adj_mat)+1) :
            print("SEARCHING FOR SUBSETS OF SIZE " + str(i-1))
            # Set of all subsets of blocking positions of size i-1 (sorted by size)
            subsets = list(chain.from_iterable(combinations(self.adj_mat, r) for r in range(i-1, i)))

            for s in subsets:
                # Break the loop if a dominating set is found
                if (self.isDominating(s, len(self.adj_mat[0]))):
                    minimalDominantSet = s
                    solutionFound = True
                    break
            i += 1

        return minimalDominantSet

    def solve_minDist(self):
        # Try to find a minimal dominating set among all possible subsets of blocking positions
        minimalDominantSet = ([])
        i = 1
        solutionFound = False

        while (not solutionFound and i < len(self.adj_mat)+1) :
            print("SEARCHING FOR SUBSETS OF SIZE " + str(i-1))
            # Set of all subsets of blocking positions of size i-1 (sorted by size)
            subsets = list(chain.from_iterable(combinations(self.adj_mat, r) for r in range(i-1, i)))

            for s in subsets:
                # Break the loop if a set is dominating and respect minimum distance
                if (self.isDominatingAndRespectMinDist(s, len(self.adj_mat[0]), self.problem.min_dist)):
                    minimalDominantSet = s
                    solutionFound = True
                    break
            i += 1

        return minimalDominantSet

    def solve(self):
        self.buildAdjacencyMatrix()
        minimalDominantSet = ([])
                
        # Pick the correct algorithm to solve the problem depending on the parameters of the problem
        if self.problem.min_dist is None:
            minimalDominantSet = self.solve_noExtension()
        else:
            minimalDominantSet = self.solve_minDist()

        if (minimalDominantSet != ([])):
            print("Le sous ensemble minimal est ")
            print(minimalDominantSet)
            print("Cela correspond aux positions ")
            for s in minimalDominantSet:
                print(self.coord_map[str(s)])
            buildSolutionFile(self, minimalDominantSet)
       
        else:
            print("Il n'y a pas de sous ensemble dominant! C'est dommage")

