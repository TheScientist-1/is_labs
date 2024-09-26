import typing as t
import random

from maze.maze import Maze
from .base_strategy import Strategy
from .common import find_free_place, measured


class DumbStrategy(Strategy):
    NAME = 'DUMB'

    pacman: t.Tuple[int, int]

    def setup(self, maze: Maze) -> t.Dict[str, t.Any]:
        super(DumbStrategy, self).setup(maze)
        self.pacman = find_free_place(self.maze)
        return dict(pacman=self.pacman)

    @measured
    def next_step(self) -> t.Dict[str, t.Any]:
        self.pacman = random.choice(list(self.maze.edges[self.pacman]))
        return dict(pacman=self.pacman)
