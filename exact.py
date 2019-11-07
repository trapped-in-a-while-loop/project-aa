import numpy as np
import math
import itertools
import sys
from util import buildSolutionFile, SOLUTION_FILE_NAME
from itertools import chain, combinations
from geometry import segmentCircleIntersection
from operator import add
from board import maxDist

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
                if self.dist(possible_defs, defense, self.problem.robot_radius):
                    if self.dist(self.opponents_pos, defense, self.problem.robot_radius):
                        for kick in scoring_kicks:
                            i = segmentCircleIntersection(kick[0],
                            self.anotherPoint(kick[0], kick[1]), defense, self.problem.robot_radius)
                            if not (i is None):
                                if i[0] < goal.posts[0][0]:
                                    adj_line[scoring_kicks.index(kick)] = 1
                                    possible_defs.append(defense)
                        if 1 in adj_line:
                            self.adj_mat.append(adj_line)
                             #self.coord_map[str(adj_line)] = [x, y]

                            if (str(adj_line) in self.coord_map):
                                #print("ah shit, here we go again")
                                self.coord_map[str(adj_line)].append([x, y])
                                    
                            else:
                                self.coord_map[str(adj_line)] = [[x,y]]
        
        print("matrix's size = " + str(len(self.adj_mat)) + ", " +
        str(len(self.adj_mat[0])))

        
    def buildAdjacencyMatrix2(self):
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
                                #self.coord_map[str(adj_line)] = [x, y]

                                if (str(adj_line) in self.coord_map):
                                    #print("ah shit, here we go again")
                                    self.coord_map[str(adj_line)].append([x, y])
                                            
                                else:
                                    self.coord_map[str(adj_line)] = [[x,y]]
            
        print("matrix's size = " + str(len(self.adj_mat)) + ", " +
        str(len(self.adj_mat[0])))

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

            coord_i = self.coord_map[str(subset[i])][0]

            # Check if the min distance is respected between all defenders
            for j in range(i, len(subset)):
                coord_j = self.coord_map[str(subset[j])][0]
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

    def initialDefendersPosition_rec(self, possible_coords, def_num, sol, i, n):
        if (i > n):
            print(sol)
            return

        print(possible_coords[0][i])

        for i in range(len(possible_coords[0])):
            for j in range(len(possible_coords[1])):
                for k in range(len(possible_coords[2])):
                    print("(" + str(possible_coords[0][i]) + "," + str(possible_coords[1][j]) + "," + str(possible_coords[2][k]) + ")")

        


    def initialDefendersPosition(self, defenders):
        # Generate all permutations possible for this set of defenders
        all_permut = list(itertools.permutations(defenders))

        # Store the possible cooordinates of each defender according to their adjacency line
        possible_coords = [[] for i in range(len(defenders))]

        # Number of coordinates possible for each defender according to their adjacency line
        nb_coord = []

        print("nombre de coordonnees possible avec ces défenseurs")
        for d in range(len(defenders)):
            print("défenseur " + str(d) + ": ")
            defender = defenders[d]
            for coord in self.coord_map[str(defender)]:
                print(coord)
                possible_coords[d].append(coord)
            nb_coord.append(len(possible_coords[d]))
            print()

        #print("len all_permut")
        #print(len(all_permut))

        #print(possible_coords)
        
        defenders_pos = np.zeros((len(defenders), 2))

        print(len(possible_coords[0]))

        # j numéro défenseur
        # k numéro coordonnées
        for i in range(len(possible_coords[0])):
            defenders_pos[0] = possible_coords[0][i]
            for j in range(1, len(defenders)):
                for k in range(len(possible_coords[j])):
                    #print("pos: " + str(possible_coords[j][k]))
                    defenders_pos[j] = possible_coords[j][k]

                print("defenders_pos: " + str(defenders_pos))

        print("nb_coord")
        print(nb_coord)

        numLoops = 1
        for i in range(len(defenders)):
            numLoops *= len(possible_coords[i])

        print("numloop: " + str(numLoops))

        for i in range(numLoops):
            for j in range(len(defenders)):
                print(str(possible_coords[j][i % nb_coord[j]]) )
            
        
        
        
        
        # Indexes of the better coordinates 
        indexes_coords = []
        
        best_permut = []
        max_dist = sys.maxsize

        # Loop though all possible permutations to find the one with a minimum distance between 
        # initial defenders position and solution's defenders position
        for permut in all_permut:

            # Retrieve the coordinates of the defender thanks to his adjencency line
            for i in range(len(permut)):
                defenders_pos[i] = self.coord_map[str(permut[i])][0]

            # Compute the maximum distance that a solution's defender will have to travel to place himself
            dist = maxDist(self.problem.defenders, defenders_pos.transpose())
            # Check if this permutation is the best for now
            if dist < max_dist:
                max_dist = dist
                best_permut = permut
                indexes_coords = [0, 0, 0]
                #print("new max dist: " + str(max_dist))
        
        return (best_permut, max_dist, indexes_coords)

    def solve_noExtension(self):
        # Try to find a minimal dominating set among all possible subsets of blocking positions
        minimalDominantSet = ([])
        cpt = 0
        solutionFound = False

        while (not solutionFound and cpt < len(self.adj_mat)+1) :
            print("SEARCHING FOR SUBSETS OF SIZE " + str(cpt))

            # Check if each subset's combination of size <cpt> is a dominanting set
            pool = tuple(self.adj_mat)
            n = len(pool)
            if cpt > n:
                return
            indices = list(range(cpt))

            while True:
                dominating_set = tuple(pool[i] for i in indices)
                if (self.isDominating(dominating_set, len(self.adj_mat[0]))):
                    minimalDominantSet = dominating_set
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

        return minimalDominantSet

    def solve_initialPosDefenders(self):
        # Try to find a minimal dominating set among all possible subsets of blocking positions
        minimalDominantSet = ([])
        i = 1
        solutionFound = False
        max_dist = sys.maxsize

        while (not solutionFound and i < len(self.adj_mat)+1) :
            print("SEARCHING FOR SUBSETS OF SIZE " + str(i-1))
            # Set of all subsets of blocking positions of size i-1 (sorted by size)
            subsets = list(chain.from_iterable(combinations(self.adj_mat, r) for r in range(i-1, i)))

            for s in subsets:
                # Break the loop if a dominating set is found
                if (self.isDominating(s, len(self.adj_mat[0]))):
                    #print("test")
                    #print(s)
                    (optimalDominantSet, dist, indexes_coords) = self.initialDefendersPosition(s)
                    if (dist < max_dist):
                        max_dist = dist
                        minimalDominantSet = optimalDominantSet
                    solutionFound = True
                
            i += 1

        return (minimalDominantSet, indexes_coords)

    def solve_minDist(self):
        # Try to find a minimal dominating set among all possible subsets of blocking positions
        minimalDominantSet = ([])
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
                dominating_set = tuple(pool[i] for i in indices)
                if (self.isDominatingAndRespectMinDist(dominating_set, len(self.adj_mat[0]), self.problem.min_dist)):
                    minimalDominantSet = dominating_set
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

        return minimalDominantSet

    def solve(self):
        self.buildAdjacencyMatrix2()
        minimalDominantSet = ([])
        indexes_coords = []
                
        # Pick the correct algorithm to solve the problem depending on the parameters of the problem
        if (not self.problem.min_dist is None):
            minimalDominantSet = self.solve_minDist()
        elif (not self.problem.defenders is None):
            (minimalDominantSet, indexes_coords) = self.solve_initialPosDefenders()
        else:
            minimalDominantSet = self.solve_noExtension()

        if (minimalDominantSet != ([])):
            #domination = [False] * nbFramedShots
            indexes_coords = [0] * len(minimalDominantSet)
            print("Le sous ensemble minimal est ")
            print(minimalDominantSet)
            print("Cela correspond aux positions ")
            for i in range(len(minimalDominantSet)):
                print(self.coord_map[str(minimalDominantSet[i])][indexes_coords[i]])
            buildSolutionFile(self, minimalDominantSet, indexes_coords)
       
        else:
            print("Il n'y a pas de sous ensemble dominant! C'est dommage")

