import typing as t
import pygame

from maze.maze import Maze
from view.strawberry import Strawberry
from view.dot import Dot
from view.ghost import Ghost
from view.pacman import Pacman

MAX_DISPLAY_WIDTH = 1000
MAX_DISPLAY_HEIGHT = 500



class View:
    cell_size: int
    sprites: t.Dict[str, pygame.sprite.Sprite]
    sprites_group: pygame.sprite.Group
    labyrinth: Maze = None
    mode_set = False

    SMOOTH_MOVEMENT = ['pacman', 'ghosts']
    SPRITES_Z_INDEX = {
        'pacman': 0,
        'target': -1,
        'ghosts': 1,
    }
    REGULAR_SPRITES = ['pacman', 'target']
    LIST_SPRITES = ['ghosts']
    STATIC_SPRITES = ['dots']

    def __init__(self):
        pygame.init()
        self.sprites_group = pygame.sprite.Group()
        self.display_info = pygame.display.Info()
        self.sprites: t.Dict[t.Union[pygame.sprite.Sprite, t.List[pygame.sprite.Sprite]]] = {}
        self.benchmarking = {}

        self.screen = pygame.display.set_mode([MAX_DISPLAY_WIDTH, MAX_DISPLAY_HEIGHT])
        self.clock = pygame.time.Clock()

    def draw_labyrinth(self, labyrinth: t.Optional[Maze] = None):
        self.labyrinth = labyrinth or self.labyrinth
        labyrinth = self.labyrinth

        cell_size = min(
            self.display_info.current_h // len(labyrinth.raw_img),
            self.display_info.current_w // len(labyrinth.raw_img[0])
        )
        if self.mode_set == False:
            self.screen = pygame.display.set_mode([cell_size * len(labyrinth.raw_img[0]), cell_size * len(labyrinth.raw_img)])
            self.mode_set = True
        self.cell_size = cell_size

        for line_no, line in enumerate(labyrinth.raw_img):
            for char_no, char in enumerate(line):
                color = (0, 0, 0) if char == ' ' else (0, 0, 200)
                pygame.draw.rect(
                    self.screen, color,
                    (char_no * cell_size, line_no * cell_size, cell_size, cell_size)
                )

    def set_initial_state(self, state: t.Dict[str, t.Any]):
        self.state = state
        if 'pacman' in state:
            x, y = state['pacman']
            pacman = Pacman(size=self.cell_size)
            self.sprites['pacman'] = pacman
            pacman.rect.move_ip(y * self.cell_size, x * self.cell_size)
        if 'target' in state:
            x, y = state['target']
            target = Strawberry(size=self.cell_size)
            self.sprites['target'] = target
            target.rect.move_ip(y * self.cell_size, x * self.cell_size)
        if 'ghosts' in state:
            self.sprites['ghosts'] = [
                Ghost(size=self.cell_size)
                for _ in state['ghosts']
            ]
            for i, (x, y) in enumerate(state['ghosts']):
                self.sprites['ghosts'][i].rect.move_ip(y * self.cell_size, x * self.cell_size)
        if 'dots' in state:
            self.sprites['dots'] = [
                Dot(size=self.cell_size)
                for _ in state['dots']
            ]
            for i, (x, y) in enumerate(state['dots']):
                sprite: Dot = self.sprites['dots'][i]
                sprite.rect.move_ip(y * self.cell_size + sprite.offset, x * self.cell_size + sprite.offset)

        self.sprites_group.add(*self.sorted_sprites)
        self.render()

    def update_state(self, state: t.Dict[str, t.Any], benchmarking: t.Dict[str, t.Any]):
        self.benchmarking = benchmarking
        self.update_rotations(self.state, state)
        steps = 5 if self.cell_size > 8 else 1
        for int_state in self._generate_intermediate_states(steps, self.state, state):
            self.state.update(int_state)
            self.sync()
            self.render()
        self.state.update(state)
        self.sync()
        self.render()

    def sync(self):
        if 'pacman' in self.sprites:
            pacman = self.sprites['pacman']
            x, y = self.state['pacman']
            pacman.rect.update([y * self.cell_size, x * self.cell_size, self.cell_size, self.cell_size])
        if 'target' in self.sprites:
            target = self.sprites['target']
            x, y = self.state['target']
            target.rect.update([y * self.cell_size, x * self.cell_size, self.cell_size, self.cell_size])
        if 'ghosts' in self.sprites:
            for source, target in zip(self.state['ghosts'], self.sprites['ghosts']):
                x, y = source
                target.rect.update([y * self.cell_size, x * self.cell_size, self.cell_size, self.cell_size])
        if 'dots' in self.state:
            self.sprites['dots'] = [
                Dot(size=self.cell_size)
                for _ in self.state['dots']
            ]
            for i, (x, y) in enumerate(self.state['dots']):
                sprite: Dot = self.sprites['dots'][i]
                sprite.rect.move_ip(y * self.cell_size + sprite.offset, x * self.cell_size + sprite.offset)

    def render(self):
        # print(1)
        self.draw_labyrinth()
        self.draw_dots()
        self.sprites_group.draw(self.screen)
        self.show_benchmarking()
        pygame.display.flip()
        self.clock.tick(30)

    @property
    def sorted_sprites(self):
        res = sorted(
            [
                (key, value)
                for key, value in self.sprites.items()
                if key in self.REGULAR_SPRITES
            ],
            key=lambda kv: self.SPRITES_Z_INDEX.get(kv[0])
        )
        res = list(map(lambda kv: kv[1], res))
        for sprite_list in sorted(
                [
                    (key, value)
                    for key, value in self.sprites.items()
                    if key in self.LIST_SPRITES
                ],
                key=lambda kv: self.SPRITES_Z_INDEX.get(kv[0])
        ):
            res += sprite_list[1]
        return res

    def update_rotations(self, from_state, to_state):
        pacman = self.sprites['pacman']
        pacman.rotation = self._get_rotation(from_state['pacman'], to_state['pacman'])

    def show_benchmarking(self):
        font = pygame.font.Font(None, 36)
        for i, (key, value) in enumerate(self.benchmarking.items()):
            if isinstance(value, float):
                text = f'{key} : {value:.5f}'
            else:
                text = f'{key}: {value}'
            text = font.render(text, True, (0, 140, 0))
            place = text.get_rect(topleft=(10, 10 + i * 36))
            self.screen.blit(text, place)

    @classmethod
    def _generate_intermediate_states(cls, count: int, state_from: t.Dict[str, t.Any], state_to: t.Dict[str, t.Any])\
            -> t.List[t.Dict[str, t.Any]]:
        # TODO: fix teleports - need some complex logic
        intermediate_states = []
        for i in range(count):
            intermediate_state = {}
            for key, value in state_from.items():
                if key not in cls.SMOOTH_MOVEMENT:
                    intermediate_state[key] = value if i == 0 or key not in state_to else state_to[key]
                elif (
                        (key not in state_to)
                        or (not isinstance(value, list) and not isinstance(value, tuple))
                        or len(value) != 2
                ):
                    intermediate_state[key] = value
                else:
                    if key in cls.REGULAR_SPRITES:
                        intermediate_state[key] = (
                            value[0] + (state_to[key][0] - value[0]) * i / count,
                            value[1] + (state_to[key][1] - value[1]) * i / count
                        )
                    else:
                        intermediate_state[key] = [
                            (
                                source[0] + (dest[0] - source[0]) * i / count,
                                source[1] + (dest[1] - source[1]) * i / count
                            )
                            for source, dest in zip(value, state_to[key])
                        ]
            intermediate_states.append(intermediate_state)
        return intermediate_states

    @staticmethod
    def _get_rotation(from_xy, to_xy):
        x_f, y_f = from_xy
        x_t, y_t = to_xy
        if x_t < x_f:
            return 3
        if x_t > x_f:
            return 1
        if y_t < y_f:
            return 0
        return 2

    def draw_dots(self):
        if 'dots' not in self.sprites:
            return
        sprites = self.sprites['dots']
        sprites_group = pygame.sprite.Group()
        sprites_group.add(*sprites)
        sprites_group.draw(self.screen)
