import typing as t

from maze.maze import Maze


class Strategy:
    NAME: str
    STORAGE_REGISTRY: t.Dict[str, 'Strategy'] = dict()

    maze: Maze

    def __init__(self):
        self.benchmarking = {
            'cpu_user': 0,
            'cpu_system': 0,
            'memory': 0,
        }

    def __init_subclass__(cls, **kwargs):
        cls.STORAGE_REGISTRY[cls.NAME] = cls

    @classmethod
    def get(cls, name):
        return cls.STORAGE_REGISTRY[name]()

    def setup(self, maze: Maze) -> t.Dict[str, t.Any]:
        self.maze = maze
        return {}

    def next_step(self) -> t.Dict[str, t.Any]:
        raise NotImplementedError()
