from typing import List


class DFS:
    def dfs(self, maze, path, used, src, dest) -> List:
        if src == dest:
            return path

        used.add(src)
        for to in maze.edges[src]:
            if to not in used:
                path.append(to)
                result = self.dfs(maze, path, used, to, dest)
                if result is not None:
                    return result
                path.pop(-1)
        used.pop()

    def apply(self, maze, src, dest):
        return self.dfs(maze, [], set(), src, dest)