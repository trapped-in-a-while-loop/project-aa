
SOLUTION_FILE_NAME = "solution.json"

def buildSolutionFile(exact, minSet):
    solFile = open(SOLUTION_FILE_NAME, "w+")
    solFile.write("{\"defenders\":[")

    print("The minimal dominating set is")
    print(minSet)
    print("It matches the positions ")
    if isinstance(minSet[0], list):
        for i in range(len(minSet)):
            print(exact.coord_map[str(minSet[i])][0])
            coordinates = exact.coord_map[str(minSet[i])][0]
            solFile.write("[" + str(coordinates[0]) + "," + str(coordinates[1]) + "]")
            if i < len(minSet) - 1:
                solFile.write(",")
    else:
        print(exact.coord_map[str(minSet)][0])
        coordinates = exact.coord_map[str(minSet)][0]
        solFile.write("[" + str(coordinates[0]) + "," + str(coordinates[1]) + "]")

    solFile.write("]}")
    solFile.close()
