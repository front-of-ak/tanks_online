import pygame

from universal_constants import TILE_HEIGHT, TILE_WIDTH
from different_funcs import load_image
from sprite_groups import top_borders_group, left_borders_group, right_borders_group, bottom_borders_group, \
    all_sprites, houses_group

TILE_IMAGES = {
    'wall': load_image('house.png'),
    'empty': load_image('grass.png'),
    'stone': load_image('stone.jpg'),
    'earth': load_image('earth.jpg')
}


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y, *groups):
        super().__init__(all_sprites, *groups)
        self.image = TILE_IMAGES[tile_type]
        self.rect = self.image.get_rect().move(
            TILE_WIDTH * pos_x, TILE_HEIGHT * pos_y)


class Border(pygame.sprite.Sprite):
    def __init__(self, x1, y1, x2, y2, group_type):
        super().__init__(all_sprites, group_type)
        if group_type == top_borders_group:
            self.image = pygame.Surface([x2 - x1, 1])
            self.rect = pygame.Rect(x1, y1, x2, y2)
        if group_type == left_borders_group:
            self.image = pygame.Surface([1, y2 - y1])
            self.rect = pygame.Rect(x1, y1, x2, y2)
        if group_type == right_borders_group:
            self.image = pygame.Surface([1, y2 - y1])
            self.rect = pygame.Rect(x1, y1, x2, y2)
        if group_type == bottom_borders_group:
            self.image = pygame.Surface([x2 - x1, 1])
            self.rect = pygame.Rect(x1, y1, x2, y2)
        self.mask = pygame.mask.from_surface(self.image)


class House(Tile):
    def __init__(self, tile_type, pos_x, pos_y, borders):
        super().__init__(tile_type, pos_x, pos_y, houses_group)
        self.mask = pygame.mask.from_surface(self.image)
        pos_x *= TILE_WIDTH
        pos_y *= TILE_HEIGHT
        if borders['top_border']:
            self.top_border = Border(pos_x, pos_y, pos_x + TILE_WIDTH, pos_y, top_borders_group)
        if borders['left_border']:
            self.left_border = Border(pos_x, pos_y, pos_x, pos_y + TILE_HEIGHT, left_borders_group)
        if borders['bottom_border']:
            self.bottom_border = Border(pos_x, pos_y + TILE_HEIGHT,
                                        pos_x + TILE_WIDTH, pos_y + TILE_HEIGHT,
                                        bottom_borders_group)
        if borders['right_border']:
            self.right_border = Border(pos_x + TILE_WIDTH, pos_y,
                                       pos_x + TILE_WIDTH, pos_y + TILE_HEIGHT,
                                       right_borders_group)
