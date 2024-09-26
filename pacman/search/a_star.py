from typing import List, Tuple
from queue import PriorityQueue


class TunneledManhattan:
    def __init__(self, dim):
        self.height, self.width = dim

    def apply(self, x, y: Tuple[int, int]):
        direct = abs(x[0] - y[0]) + abs(x[1] - y[1])
        tunneled = min(x[0], y[0]) + self.width - max(x[0], y[0]) + abs(x[1] - y[1])
        return min(direct, tunneled)


def in_queue(v, queue):
    for element in queue.queue:
        if element[1] == v:
            return True
    return False


def restore_path(parent, src, dest) -> List:
    path = []
    current = dest

    while current != src:
        path.append(current)
        current = parent[current]

    return path[::-1]


class AStar:
    def __init__(self, heuristic):
        self.heuristic = heuristic

    def a_star(self, maze, src, dest) -> List:
        queue = PriorityQueue()
        used = set()
        g = {src: 0}
        f = {src: self.heuristic.apply(src, dest)}
        queue.put((f[src], src))

        parent = {}
        while not queue.empty():
            current = queue.get()[1]
            if current == dest:
                return restore_path(parent, src, dest)

            used.add(current)

            for to in maze.edges[current]:
                tentative_score = g[current] + 1

                if to in used and tentative_score >= g[to]:
                    continue

                parent[to] = current
                g[to] = tentative_score
                f[to] = g[to] + self.heuristic.apply(to, dest)
                if not in_queue(to, queue):
                    queue.put((f[to], to))

        return None

    def apply(self, maze, src, dest):
        return self.a_star(maze, src, dest)
