import os
import sys
import pygame

from universal_constants import TILE_WIDTH, TILE_HEIGHT


# functions, which are used for loading files
def load_image(name, color_key=None):
    full_name = os.path.join('data', 'images', name)
    try:
        image = pygame.image.load(full_name).convert()
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    except FileNotFoundError:
        full_name = os.path.join('data', 'images', 'intro_screen.jpg')
        image = pygame.image.load(full_name).convert()

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


def position_count(column, row):
    pos_x = (column + 1) * TILE_WIDTH - TILE_WIDTH // 2
    pos_y = (row + 1) * TILE_HEIGHT - TILE_HEIGHT // 2
    return pos_x, pos_y


def terminate():
    pygame.quit()
    sys.exit()
