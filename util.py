import networkx as nx
import matplotlib.pyplot as plt

SOLUTION_FILE_NAME = "solution.json"

def buildSolutionFile(exact, minSet):
    solFile = open(SOLUTION_FILE_NAME, "w+")
    solFile.write("{\"defenders\":[")
    for i in range(len(minSet)):
        coordinates = exact.coord_map[str(minSet[i])]
        solFile.write("[" + str(coordinates[0]) + "," + str(coordinates[1]) + "]")
        if i < len(minSet) - 1:
            solFile.write(",")
    solFile.write("]}")
    solFile.close()

def drawGraph(exact):
    G = nx.Graph()
    left_nodes = nx.Graph()
    
    for i in range(len(exact.adj_mat)):
        G.add_node(i)
        if i < len(exact.adj_mat[0]):
            left_nodes.add_node(i)
        for j in range(len(exact.adj_mat[i])):
            if (exact.adj_mat[i][j] == 1):
                G.add_edge(i, j)
    nx.draw(G)
    plt.subplot(121)
    print("Drawing graph ...")
    nx.draw_networkx(G, pos = nx.drawing.layout.bipartite_layout(G, left_nodes))
    plt.show()