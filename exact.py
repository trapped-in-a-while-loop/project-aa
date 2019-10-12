from problem import *
from operator import add

def anotherPoint(old_point, angle):
  x = 1000 * math.cos(angle)
  y = 1000 * math.sin(angle)
  new_point = np.array(list(map(add, old_point, [x, y])))
  return new_point

def frange(start, stop, step):
  i = start
  while i < stop:
    yield i
    i += step

def dist(opponents, defense, robot_radius):
  result = True
  for opponent in opponents:
    if (math.hypot(defense[0] - opponent[0], defense[1] - opponent[1]) <
    (robot_radius * 2)):
      result = False
  return result

class Exact:
  def __init__(self, problem):
    self.adj = []

    opponents = []
    for i in range(len(problem.opponents[0])):
      opponents.append([problem.opponents[0][i], problem.opponents[1][i]])

    posts = []
    for i in range(len(problem.goals)):
      posts.append([problem.goals[i].posts[0][0],
      problem.goals[i].posts[1][0]])
      posts.append([problem.goals[i].posts[0][1],
      problem.goals[i].posts[1][1]])

    scoring_kicks = []
    for i in range(len(problem.opponents[0])):
      opponent = [problem.opponents[0][i], problem.opponents[1][i]]
      direction = 0
      while direction < 2 * math.pi:
        for goal in problem.goals:
          if not (goal.kickResult(opponent, direction) is None):
            """ 4 next lines to correct incomprehensible kickResult()'s
                behavior """
            if (direction > math.pi):
              scoring_kicks.append([opponent, direction - math.pi])
            elif (direction < math.pi):
              scoring_kicks.append([opponent, direction + math.pi])
        direction += problem.theta_step

    possible_defs = []
    for x in frange(problem.field_limits[0][0], problem.field_limits[0][1],
    problem.pos_step):
      for y in frange(problem.field_limits[1][0], problem.field_limits[1][1],
      problem.pos_step):
        defense = [x, y]
        adj_line = [0] * len(scoring_kicks)
        if defense not in possible_defs:
          if defense not in posts:
            if dist(opponents, defense, problem.robot_radius):
              for kick in scoring_kicks:
                if not (segmentCircleIntersection(kick[0],
                anotherPoint(kick[0], kick[1]), defense, problem.robot_radius)
                is None):
                  adj_line[scoring_kicks.index(kick)] = 1
                  possible_defs.append(defense)
              if 1 in adj_line:
                self.adj.append(adj_line)

    for i in self.adj:
      print(i)
    print("matrix's size = " + str(len(self.adj)) + ", " +
    str(len(self.adj[0])))

  def run(self):
    return 0
