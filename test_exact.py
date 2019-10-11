#!/usr/bin/python3
import sys
import json

from board import *
from exact import *

if (len(sys.argv) < 2) :
    sys.exit("Usage: " + sys.argv[0] + " <problem.json> ")

problem_path = sys.argv[1]

with open(problem_path) as problem_file:
    problem = Problem(json.load(problem_file))

solution = Exact(problem);

solution.run();
