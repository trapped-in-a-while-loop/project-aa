import numpy
import math
import networkx as nx
import matplotlib.pyplot as plt
from itertools import chain, combinations

M_full = [
    # Tirs cadrés
    [0, 0, 0, 0, 0, 1, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 1],

    # Positions bloquant les tirs
    [1, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 1, 0, 0, 0, 0],
]

# Partie droite de la matrice d'adjacence (les positions bloquants les tirs)
# TODO: lier les sommets à leurs coordonnées
M = [
    [1, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 1, 0, 0, 0, 0], 
]
nbTirsCadres = 5

class Exact :
    def __init__(self, problem, board):
        self.problem = problem
        self.board = board
        self.possiblePositions = []
        self.blockingPositions = []
        self.subSets = []

    def isDominating(self, subset):
        domination = [False] * nbTirsCadres
        for s in subset:
            for j in range(nbTirsCadres):
                if (s[j] == 1):
                    domination[j] = True

        for d in domination:
            if d == False:
                return False
        return True
        
    def solve(self):
        # Ensemble de tous les sous-ensembles de positions bloquantes triés par taille
        allSubsets = list(chain.from_iterable(combinations(M, r) for r in range(len(M)+1)))
        print("Nombre de sous-ensembles : " + str(len(allSubsets)))

        #for s in allSubsets:
        #    print(s)

        minimalDominantSet = ([])
        
        for s in allSubsets:
            if self.isDominant(s):
                minimalDominantSet = s
                break

        if (minimalDominantSet != ([])):
            print("Le sous ensemble minimal est ")
            print(minimalDominantSet)
        else:
            print("Il n'y a pas de sous ensemble dominant! C'est dommage")

        #self.drawGraph()

    def drawGraph(self):
        G = nx.Graph()
        left_nodes = nx.Graph()
        
        for i in range(len(M_full)):
            G.add_node(i)
            if i < nbTirsCadres:
                left_nodes.add_node(i)

            for j in range(len(M_full[i])):
                if (M_full[i][j] == 1):
                    G.add_edge(i, j)

        nx.draw(G)
        plt.subplot(121)
        print("Drawing graph ...")
        nx.draw_networkx(G, pos = nx.drawing.layout.bipartite_layout(G, left_nodes))
        plt.show()
