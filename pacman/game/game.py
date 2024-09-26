import pygame


from maze.maze import Maze
from strategies import Strategy
from view import View


class Game:
    def __init__(self, strategy='DFS', used_map='10x10'):
        pygame.init()
        self.strategy = Strategy.get(strategy.upper())
        self.maze = Maze.from_file(f'./maze/pregenerated/{used_map}.txt')
        self.view = View()
        self.view.draw_labyrinth(self.maze)
        self.show_benchmarking = False

        tmp = self.strategy.setup(self.maze)
        print(tmp)
        self.view.set_initial_state(tmp)

    def mainloop(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_d:
                        self.show_benchmarking = not self.show_benchmarking

            next_step = self.strategy.next_step()
            benchmarking = self.strategy.benchmarking if self.show_benchmarking else {}
            self.view.update_state(next_step, benchmarking)
