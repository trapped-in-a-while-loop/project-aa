from problem import *
from operator import add

def anotherPoint(old_point, angle):
  x = 1000 * math.cos(angle)
  y = 1000 * math.sin(angle)
  new_point = np.array(list(map(add, old_point, [x, y])))
  return new_point

class Exact:
  def __init__(self, problem):
    self.adj = []
    possible_defs = []
    scoring_kicks = []

    for i in range(len(problem.opponents[0])):
      opponent = [problem.opponents[0][i], problem.opponents[1][i]]
      direction = 0
      while direction < 2 * math.pi:
        opponent = np.array(opponent)
        if not (problem.goals[0].kickResult(opponent, direction) is None):
          scoring_kicks.append([opponent, direction])
        direction += problem.theta_step

    for x in range(int(problem.getFieldWidth().item() / problem.pos_step)):
      for y in range(int(problem.getFieldHeight().item() / problem.pos_step)):
        defense = [problem.pos_step * x, problem.pos_step * y]
        adj_line = [0] * len(scoring_kicks)
        for kick in scoring_kicks:
          if not (segmentCircleIntersection(kick[0],
            anotherPoint(kick[0], kick[1]), defense, problem.robot_radius)
            is None):
            adj_line[scoring_kicks.index(kick)] = 1
            possible_defs.append(defense)
        if 1 in adj_line:
          self.adj.append(adj_line)
    print(str(len(self.adj)) + ", " + str(len(self.adj[0])))
    print(len(possible_defs))

  def run(self):
    return 0
