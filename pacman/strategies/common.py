import random
import psutil
import typing as t
from functools import wraps

from strategies import Strategy


def format(position, target, ghost=None):
    state = {
        'pacman': position,
        'target': target
    }

    if ghost is not None:
        state['ghosts'] = [ghost]

    return state


def gen_path(path, target):
    for position in path:
        yield format(position, target)
    yield None


def find_free_place(maze) -> t.Tuple[int, int]:
    return random.choice(list(maze.cells))


def measured(func):
    @wraps(func)
    def wrapper(self: Strategy, *args, **kwargs):
        # Before: CPU times and memory usage
        before_cpu = psutil.cpu_times()
        before_memory = psutil.Process().memory_info().rss
        
        res = func(self, *args, **kwargs)

        # After: CPU times and memory usage
        after_cpu = psutil.cpu_times()
        after_memory = psutil.Process().memory_info().rss

        # Update benchmarking with max usage values
        self.benchmarking.update({
            'cpu_user': max(self.benchmarking.get('cpu_user', 0), after_cpu.user - before_cpu.user),
            'cpu_system': max(self.benchmarking.get('cpu_system', 0), after_cpu.system - before_cpu.system),
            'memory': max(self.benchmarking.get('memory', 0), after_memory - before_memory),
        })
        
        return res
    return wrapper
