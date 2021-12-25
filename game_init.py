import os
import sys

import pygame

pygame.init()

# constants
FPS = 60
WIDTH = 1080
HEIGHT = 800
BACKGROUND = pygame.color.Color('black')

# screen and clock init
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption('WWII: Величайшие танковые битвы')
# sprite groups
all_sprites = pygame.sprite.Group()


def terminate():
    pygame.quit()
    sys.exit()


# functions, which are used for loading files
def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname).convert()
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


# main game cycle
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BACKGROUND)

    all_sprites.draw(screen)
    all_sprites.update()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
terminate()
