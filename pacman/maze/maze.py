from typing import Dict, List, Set, Tuple


class Maze:
    def __init__(self):
        self.cells: Set[Tuple[int, int]] = set()
        self.edges: Dict[Tuple[int, int], Set[Tuple[int, int]]] = dict()
        self.raw_img: List[str] = []

    def _add_edge(self, cell_from: Tuple[int, int], cell_to: Tuple[int, int]) -> None:
        if self.edges.get(cell_from) is None:
            self.edges[cell_from] = set()
        self.edges[cell_from].add(cell_to)

    def load_from_file(self, filepath: str) -> None:
        with open(filepath) as input_file:
            line_num = 0
            prev_line = ''
            for line in input_file:
                if line == "":
                    break
                self.raw_img.append(line[:-1] if line.endswith('\n') else line)
                for pos in range(len(line) - 1):
                    if line[pos] == ' ':
                        self.cells.add((line_num, pos))
                        if line_num != 0 and prev_line[pos] == ' ':
                            self._add_edge((line_num, pos), (line_num - 1, pos))
                            self._add_edge((line_num - 1, pos), (line_num, pos))
                        if pos != 0 and line[pos - 1] == ' ':
                            self._add_edge((line_num, pos), (line_num, pos - 1))
                            self._add_edge((line_num, pos - 1), (line_num, pos))
                        if pos == 0 and line[-2] == ' ':
                            self._add_edge((line_num, 0), (line_num, len(line) - 2))
                            self._add_edge((line_num, len(line) - 2), (line_num, 0))

                line_num += 1
                prev_line = line

    @classmethod
    def from_file(cls, filepath: str) -> 'Maze':
        maze = cls()
        maze.load_from_file(filepath)
        return maze
