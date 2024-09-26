from typing import List, Tuple, Dict, Any
from queue import PriorityQueue
from .common import find_free_place, gen_path, format, measured
from .base_strategy import Strategy
from maze.maze import Maze


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


class AStar(Strategy):
    NAME = 'A*'

    def setup(self, maze: Maze) -> Dict[str, Any]:
        super(AStar, self).setup(maze)
        dimensions = len(maze.raw_img), len(maze.raw_img[0])
        self.heuristic = TunneledManhattan(dimensions)
        self.path = None
        self.src = find_free_place(self.maze)
        self.ghost = find_free_place(self.maze)
        self.set_new_target()
        return format(self.src, self.target, self.ghost)

    @measured
    def a_star(self, maze, src, dest) -> List:
        queue = PriorityQueue()
        used = set()
        g = {src: 0}
        f = {src: self.heuristic.apply(src, dest)}
        queue.put((f[src], src))

        parent = {}
        while not queue.empty():
            self.benchmarking['ops'] += 1
            current = queue.get()[1]
            if current == dest:
                return restore_path(parent, src, dest)

            used.add(current)

            for to in maze.edges[current]:
                self.benchmarking['ops'] += 1
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
        self.benchmarking['ops'] = 0
        path = self.a_star(maze, src, dest)
        if path is None:
            raise ValueError(f"Destination {dest} is unreachable from source {src}")
        self.path = gen_path(path, self.target)

    def set_new_target(self):
        self.target = find_free_place(self.maze)
        self.apply(self.maze, self.src, self.target)

    def next_step(self) -> Dict[str, Any]:
        next_position = next(self.path)
        while next_position is None:
            self.src = self.target
            self.set_new_target()
            next_position = next(self.path)
        return next_position

