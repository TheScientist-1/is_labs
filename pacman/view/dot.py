import pygame


class Dot(pygame.sprite.Sprite):
    SIZE_MULTIPLIER = 4

    def __init__(self, size):
        super(Dot, self).__init__()

        if size >= 8:
            size /= self.SIZE_MULTIPLIER
        self.size = size
        self.surf = pygame.Surface((size, size))
        self.surf.fill((255, 255, 255))
        self.rect = self.surf.get_rect()
        self.rotation = 0
        self.image = self.surf

    @property
    def offset(self):
        if self.size < 8:
            return 0
        return (self.SIZE_MULTIPLIER - 1) * self.size / 2
