import pygame


class Pacman(pygame.sprite.Sprite):
    def __init__(self, size):
        super(Pacman, self).__init__()
        self.size = size
        image = pygame.image.load('view/sprites/pacman.png')
        image = pygame.transform.scale(image, (size, size))
        self._images = [
            pygame.transform.rotate(image, 90 * i)
            for i in range(4)
        ]

        self.surf = pygame.Surface((size, size))
        self.surf.fill((255, 255, 0))
        self.rect = self.surf.get_rect()
        self.rotation = 0

    @property
    def image(self):
        if self.size < 8:
            return self.surf
        return self._images[self.rotation % 4]

