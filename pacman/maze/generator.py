import json
import random
from typing import Dict, List, Tuple


def _get_figure_params(figure: List[List[int]]) -> Tuple[int, int, int]:
    height = len(figure)
    width = len(figure[0])
    for i in range(width):
        if figure[0][i] == 1:
            return height, width, i


def _cell_free(grid: List[List[int]],
               i: int,
               j: int) -> bool:
    if i < 0 or j < 0:
        return False
    if i >= len(grid) or j >= len(grid[0]):
        return False
    return grid[i][j] == 0


def _add_figure_to_grid(grid: List[List[int]],
                        counter: int,
                        pos_i: int,
                        pos_j: int,
                        figure: List[List[int]]) -> bool:
    figure_height, figure_width, figure_start_pos = _get_figure_params(figure)
    for i in range(figure_height):
        for j in range(figure_width):
            if figure[i][j] == 1 and not _cell_free(grid, pos_i + i, pos_j + j - figure_start_pos):
                return False
    for i in range(figure_height):
        for j in range(figure_width):
            if figure[i][j] == 1:
                grid[pos_i + i][pos_j + j - figure_start_pos] = counter
    return True


def _add_to_map(half_map: List[List[int]],
                grid: List[List[int]],
                i: int,
                j: int):
    if i + 1 == len(grid) or grid[i + 1][j] != grid[i][j]:
        half_map[2 * i + 2][2 * j] = 1
        half_map[2 * i + 2][2 * j + 1] = 1
        half_map[2 * i + 2][2 * j + 2] = 1
    if j + 1 == len(grid[0]) or grid[i][j + 1] != grid[i][j]:
        half_map[2 * i][2 * j + 2] = 1
        half_map[2 * i + 1][2 * j + 2] = 1
        half_map[2 * i + 2][2 * j + 2] = 1


def generate_maze(height: int,
                       width: int,
                       output_path: str) -> None:
    grid: List[List[int]] = [[0 for _ in range(width)] for _ in range(height)]
    with open("figures.json") as figures_file:
        figures: Dict[str, List[List[List[int]]]] = json.load(figures_file)

    counter = 0
    for i in range(height):
        for j in range(width):
            for _, figures_list in figures.items():
                if grid[i][j] != 0:
                    break
                random.shuffle(figures_list)
                for figure in figures_list:
                    if _add_figure_to_grid(grid, counter, i, j, figure):
                        counter += 1
    half_map: List[List[int]] = [[0 for _ in range(2 * width + 1)] for _ in range(2 * height + 1)]
    half_map[0] = [1 for _ in range(2 * width + 1)]
    for i in range(height):
        for j in range(width):
            _add_to_map(half_map, grid, i, j)

    with open(output_path, "w+") as out_file:
        for i in range(2 * height + 3):
            if i == 0 or i == 2 * height + 2:
                out_file.write('#' * (4 * width + 4) + '\n')
                continue
            is_tunnel = random.randint(1, 10) == 1
            out_file.write(' ' if is_tunnel else '#')
            for j in range(2 * width + 1):
                out_file.write(' ' if half_map[i - 1][2 * width - j] else '#')
            for j in range(2 * width + 1):
                out_file.write(' ' if half_map[i - 1][j] else '#')
            out_file.write(' ' if is_tunnel else '#')
            out_file.write('\n')


if __name__ == '__main__':
    generate_maze(15, 15, "out.txt")

