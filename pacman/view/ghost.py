import pygame

class Colors:
    RED = (255, 0, 0)

    COLOR_TO_SPRITE_MAPPING = {
        RED: 'ghost_red.png',
    }


class Ghost(pygame.sprite.Sprite):
    def __init__(self, size, color=Colors.RED):
        super(Ghost, self).__init__()
        image = pygame.image.load(f"view/sprites/{Colors.COLOR_TO_SPRITE_MAPPING.get(color, 'ghost_red.png')}")
        image = pygame.transform.scale(image, (size, size))
        self.image = image

        self.surf = pygame.Surface((size, size))
        self.surf.fill(color)
        self.rect = self.surf.get_rect()
        self.rotation = 0

        if size < 8:
            self.image = self.surf
