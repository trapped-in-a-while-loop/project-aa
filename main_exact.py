#!/usr/bin/python3
import pygame
import sys
import json

from board import *
from exact import *

if (len(sys.argv) != 2 and len(sys.argv) != 3):
    sys.exit("Usage: \n- To test a solution: " + sys.argv[0] 
    + " <problem.json> <solution.json>\n- To generate a solution: " 
    + sys.argv[0] + " <problem.json>")

problem_path = sys.argv[1]
solution_path = SOLUTION_FILE_NAME

with open(problem_path) as problem_file:
    problem = Problem(json.load(problem_file))

if (len(sys.argv) == 3):
    solution_path = sys.argv[2]

else:
    e = Exact(problem)
    solution_found = e.solve()

    if not solution_found:
        sys.exit()
    
with open(solution_path) as solution_file:
    solution = Solution(json.load(solution_file))

b = Board(problem, solution)
b.run()

sys.exit()
