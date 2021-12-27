# running = True
# while running:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False
#         if event.type == pygame.MOUSEBUTTONDOWN:
#             if event.button == 1:  # make bullet if you press left mouse button
#                 angle, x, y = player_tank.get_position_and_angle_for_bullet()
#                 Bullet(angle, x, y)
#
#     screen.fill(BACKGROUND)
#
#     check_pressed()
#
#     all_sprites.draw(screen)
#     all_sprites.update()
#
#     pygame.display.flip()
#     clock.tick(FPS)
for i in range(30):
    for j in range(30):
        print('.', end='')
    print(import os
import sys

import pygame

FPS = 50
SIZE = WIDTH, HEIGHT = 550, 550
BACKGROUND = pygame.color.Color('black')
GRASS = '.'
BOX = '#'
PLAYER = '@'

# Изображение не получится загрузить
# без предварительной инициализации pygame
pygame.init()
screen = pygame.display.set_mode(SIZE)
clock = pygame.time.Clock()


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if color_key is not None:
        image = image.convert()
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


def load_level(filename):
    filename = os.path.join("data", filename)
    # читаем уровень, убирая символы перевода строки
    with open(filename) as map_file:
        level_map = [line.strip() for line in map_file]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, GRASS), level_map))


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["ЗАСТАВКА",
                  "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]

    background = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(background, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, True, 'black')
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.fill('white', intro_rect)
        screen.blit(string_rendered, intro_rect)

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                terminate()
            elif ev.type == pygame.KEYDOWN or \
                    ev.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


TILE_IMAGES = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png')
}
PLAYER_IMAGE = load_image('mario.png')

TILE_WIDTH = TILE_HEIGHT = 50


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = TILE_IMAGES[tile_type]
        self.rect = self.image.get_rect().move(
            TILE_WIDTH * pos_x, TILE_HEIGHT * pos_y)


class Player(pygame.sprite.Sprite):
    dx = (TILE_WIDTH - PLAYER_IMAGE.get_width()) // 2
    dy = (TILE_HEIGHT - PLAYER_IMAGE.get_height()) // 2

    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = PLAYER_IMAGE
        self.x = pos_x
        self.y = pos_y
        self.rect = self.image.get_rect().move(TILE_WIDTH * self.x + Player.dx,
                                               TILE_HEIGHT * self.y + Player.dy)

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.rect = self.rect.move(TILE_WIDTH * dx, TILE_HEIGHT * dy)


# группы спрайтов
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()


class Level:
    def __init__(self, filename):
        self.player = None
        self.map = load_level(filename)
        for row in range(len(self.map)):
            for column in range(len(self.map[row])):
                if self.map[row][column] == GRASS:
                    Tile('empty', column, row)
                elif self.map[row][column] == BOX:
                    Tile('wall', column, row)
                elif self.map[row][column] == PLAYER:
                    Tile('empty', column, row)
                    self.player = Player(column, row)

    def move_player(self, dx, dy):
        new_row = self.player.y + dy
        new_column = self.player.x + dx
        if self.map[new_row][new_column] in (GRASS, PLAYER):
            self.player.move(dx, dy)


start_screen()
level = Level('map.txt')
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            dx = 0
            dy = 0
            if event.key == pygame.K_LEFT:
                dx -= 1
            elif event.key == pygame.K_RIGHT:
                dx += 1
            elif event.key == pygame.K_UP:
                dy -= 1
            elif event.key == pygame.K_DOWN:
                dy += 1
            level.move_player(dx, dy)
    screen.fill(BACKGROUND)
    all_sprites.update()
    tiles_group.draw(screen)
    player_group.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)
terminate()
)