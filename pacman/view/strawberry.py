import pygame


class Strawberry(pygame.sprite.Sprite):
    def __init__(self, size):
        super(Strawberry, self).__init__()
        image = pygame.image.load('view/sprites/strawberry.png')
        image = pygame.transform.scale(image, (size, size))
        self.image = image

        self.surf = pygame.Surface((size, size))
        self.surf.fill((255, 255, 0))
        self.rect = self.surf.get_rect()
        self.rotation = 0

        if size < 8:
            self.image = self.surf


