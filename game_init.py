import os
import sys
import pygame
import pygame_widgets

from pygame_widgets.button import Button
from math import sin, cos, pi
from screen_attributes import screens

pygame.init()

# constants
FPS = 60
WIDTH = 1080
HEIGHT = 800
BACKGROUND = pygame.color.Color('black')

MAIN_TEXT_FONT_SIZE = 32
TITLE_TEXT_FONT_SIZE = 100
TITLE_TEXT_COORD = TITLE_TEXT_X, TITLE_TEXT_TOP = WIDTH // 2, 20
TEXT_COORD = MAIN_TEXT_X, MAIN_TEXT_TOP = WIDTH // 2, 300
TEXT_BG = (242, 232, 201)
TEXT_COLOR = 'black'

GAME_TITLE = 'WWII: Величайшие танковые битвы'
TITLE_SIZE = (458, 106)
TITLE_COORDINATES = (50, 20)

BUTTON_SIZE = 391, 62
BUTTON_RADIUS = 10

DELTA_ANGLE = 2
DELTA_DISTANCE_FOR_TANK = 3
DELTA_DISTANCE_FOR_BULLET = 12
NUM_OF_FRAMES = 360 // DELTA_ANGLE

OBJECTS = ['.', '/', '-', '@']

# screen and clock init
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption(GAME_TITLE)

# sprite groups
all_sprites = pygame.sprite.Group()
bullets_group = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()


def terminate():
    pygame.quit()
    sys.exit()


# functions, which are used for loading files
def load_image(name, color_key=None):
    fullname = os.path.join('data', 'images', name)
    try:
        image = pygame.image.load(fullname).convert()
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    except FileNotFoundError:
        fullname = os.path.join('data', 'images', 'intro_screen.jpg')
        image = pygame.image.load(fullname).convert()

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


def break_start_screen():
    global start_screen_run
    start_screen_run = False


start_screen_run = True


# function for start screen
def start_screen():
    global start_screen_run
    background = pygame.transform.scale(load_image('intro_screen.jpg'), (WIDTH, HEIGHT))
    screen.blit(background, (0, 0))
    logo = pygame.transform.scale(load_image('logo.png', -1), TITLE_SIZE)
    screen.blit(logo, (WIDTH // 2 - logo.get_width() // 2, HEIGHT // 4 - logo.get_height()))

    btn = Button(screen,
                 WIDTH // 2 - BUTTON_SIZE[0] // 2, HEIGHT // 2, *BUTTON_SIZE,
                 radius=BUTTON_RADIUS,
                 image=load_image('play_btn.jpg'),
                 onClick=break_start_screen
                 )

    while start_screen_run:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                terminate()
        events = pygame.event.get()
        pygame_widgets.update(events)
        pygame.display.flip()
        clock.tick(FPS)

    btn.hide()


def check_pressed():
    ds = 0
    da = 0
    if pygame.key.get_pressed()[pygame.K_LEFT]:
        da += DELTA_ANGLE
    elif pygame.key.get_pressed()[pygame.K_RIGHT]:
        da -= DELTA_ANGLE
    elif pygame.key.get_pressed()[pygame.K_UP]:
        ds += DELTA_DISTANCE_FOR_TANK
    elif pygame.key.get_pressed()[pygame.K_DOWN]:
        ds -= DELTA_DISTANCE_FOR_TANK
    if ds or da:
        player_tank.move(ds, da)


class Tank(pygame.sprite.Sprite):
    def __init__(self, sheet, row, col, pos_x, pos_y):
        super().__init__(all_sprites)
        self.frames = {}
        self.cut_sheet(sheet, col, row)

        self.angle = 0
        self.image = self.frames[self.angle]
        self.rect = self.image.get_rect()
        self.rect.centerx = pos_x
        self.rect.centery = pos_y
        self.x = pos_x
        self.y = pos_y

    def move(self, s, a):
        self.angle += a
        self.x += s * cos(self.angle * pi / 180)
        self.y += -s * sin(self.angle * pi / 180)

    def update(self):
        self.image = self.frames[(self.angle + 360) % 360]
        self.rect = self.image.get_rect()
        self.rect.centerx = self.x
        self.rect.centery = self.y

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for i in range(rows):
            for j in range(columns):
                frame_location = (self.rect.w * j, self.rect.h * i)
                self.frames[(columns * i + j) * DELTA_ANGLE] = \
                    sheet.subsurface(pygame.Rect(frame_location, self.rect.size))

    def get_position_and_angle_for_bullet(self):
        # tried to set prettier start position for bullet but smth went wrong
        # x_for_bullet = self.x + self.rect.width / 2 * cos(self.angle)
        # y_for_bullet = self.y + -self.rect.height / 2 * sin(self.angle)
        return self.angle, self.x, self.y


class Bullet(pygame.sprite.Sprite):
    sheet = load_image('bullet_sheet.png', color_key=-1)

    def __init__(self, angle, pos_x, pos_y):
        super().__init__(all_sprites, bullets_group)

        self.angle = angle
        self.set_image_using_angle(angle)
        self.rect = self.image.get_rect()
        self.rect.centerx = pos_x
        self.rect.centery = pos_y
        self.x = pos_x
        self.y = pos_y

    def update(self):
        self.x += DELTA_DISTANCE_FOR_BULLET * cos(self.angle * pi / 180)
        self.y += -DELTA_DISTANCE_FOR_BULLET * sin(self.angle * pi / 180)
        self.rect.centerx = self.x
        self.rect.centery = self.y

        if not self.rect.colliderect(screen.get_rect()):
            self.kill()

    def set_image_using_angle(self, angle):  # getting bullet image from bullet_sheet
        num_of_sprite = (angle // DELTA_ANGLE) % NUM_OF_FRAMES
        self.rect = pygame.Rect(0, 0, self.sheet.get_width() // NUM_OF_FRAMES, self.sheet.get_height() // 1)
        frame_location = (self.rect.w * num_of_sprite, 0)
        self.image = self.sheet.subsurface(pygame.Rect(frame_location, self.rect.size))


class MiddleScreen:
    def __init__(self, title, text, background_image):
        self.title = title
        self.text = text
        self.background_image = background_image
        self.render_screen()

        self.button_next = Button(screen,
                                  WIDTH // 2 - BUTTON_SIZE[0] // 2, HEIGHT // 3 * 2, *BUTTON_SIZE,
                                  radius=BUTTON_RADIUS,
                                  image=load_image('accept.jpg'),
                                  onClick=self.to_level
                                  )

        self.running = True
        while self.running:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    terminate()
            events = pygame.event.get()
            pygame_widgets.update(events)
            pygame.display.flip()
            clock.tick(FPS)
        self.button_next.hide()

    def render_screen(self):
        # bg rendering
        background = pygame.transform.scale(load_image(self.background_image), (WIDTH, HEIGHT))
        screen.blit(background, (0, 0))

        # title rendering
        font_title = pygame.font.Font(None, TITLE_TEXT_FONT_SIZE)
        title_rendered = font_title.render(self.title, True, TEXT_COLOR)
        intro_rect = title_rendered.get_rect()
        intro_rect.centerx = TITLE_TEXT_X
        intro_rect.top = TITLE_TEXT_TOP
        screen.fill(TEXT_BG, intro_rect)
        screen.blit(title_rendered, intro_rect)

        # main text rendering
        font_text = pygame.font.Font(None, MAIN_TEXT_FONT_SIZE)
        text_coord = MAIN_TEXT_TOP
        for line in self.text:
            string_rendered = font_text.render(line, True, TEXT_COLOR)
            intro_rect = string_rendered.get_rect()
            intro_rect.centerx = MAIN_TEXT_X
            text_coord += 10
            intro_rect.top = text_coord
            text_coord += intro_rect.height
            screen.fill(TEXT_BG, intro_rect)
            screen.blit(string_rendered, intro_rect)

    def to_level(self):
        self.running = False


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        pass


class Enemie(Tank):
    def __init__(self):
        pass


class GameLevel:
    def __init__(self, level_file):
        self.level_file = level_file
        self.map = self.load_level_map()
        self.enemies = []

    def load_level_map(self):
        filename = os.path.join("data", 'level_maps', self.level_file)
        with open(filename) as map_file:
            level_map = [line.strip() for line in map_file]
        max_width = max(map(len, level_map))
        return list(map(lambda x: x.ljust(max_width, OBJECTS[0]), level_map))

    def load_level(self):
        for row in range(len(self.map)):
            for column in range(len(self.map[row])):
                if self.map[row][column] == OBJECTS[0]:
                    Tile('empty', column, row)
                elif self.map[row][column] == OBJECTS[1]:
                    Tile('wall', column, row)
                elif self.map[row][column] == OBJECTS[2]:
                    Tile('empty', column, row)
                    self.enemies.append(Enemie(column, row))

    def move_player(self):
        pass

    def move_enemie(self):
        pass

    def loop(self):
        pass


start_screen()

first_screen = MiddleScreen(screens[0]['title'],
                            screens[0]['text'],
                            screens[0]['background'])

first_level = GameLevel('first_level.txt')

# main game cycle
player_tank = Tank(load_image('tank_sheet.png'), 1, NUM_OF_FRAMES, 500, 500)
pygame.mouse.set_visible(False)

terminate()
