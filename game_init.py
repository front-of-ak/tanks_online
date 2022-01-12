import math
import os
import random
import sys

import pygame
import pygame_widgets

from pygame_widgets.button import Button
from math import sin, cos, pi
from screen_attributes import screens

# from level_generator import generate

pygame.init()

# constants
FPS = 60
WIDTH = 1080
HEIGHT = 800
LEVEL_WIDTH, LEVEL_HEIGHT = 27, 20
TILE_WIDTH = WIDTH / LEVEL_WIDTH
TILE_HEIGHT = HEIGHT / LEVEL_HEIGHT
BACKGROUND = pygame.color.Color('white')
PAUSE_COLOR = pygame.Color(81, 144, 174)

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
D_X_FOR_SHOOTING = 15
NUM_OF_FRAMES = 360 // DELTA_ANGLE
BOOM_FPS = 60
RELOAD_TIME = 2

OBJECTS = {'empty': '.', 'wall': '/', 'enemy': '-', 'player': '@'}

LEVELS = [[(screens[0]['title'], screens[0]['text'], screens[0]['background']),
           '1_level.txt'],
          [(screens[1]['title'], screens[1]['text'], screens[1]['background']),
           '2_level.txt'],
          [(screens[2]['title'], screens[2]['text'], screens[2]['background']),
           '3_level.txt'],
          [(screens[3]['title'], screens[3]['text'], screens[3]['background']),
           '4_level.txt'],
          [(screens[4]['title'], screens[4]['text'], screens[4]['background']),
           '5_level.txt']]
MAX_LEVEL = 5

# screen and clock init
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption(GAME_TITLE)
current_level = 0

# music init
back_sound = pygame.mixer.Sound(file=os.path.join("data", 'sounds', 'hoi4mainthemeallies.wav'))
shot_sound = pygame.mixer.Sound(file='data/sounds/shot.wav')
player_tank_dead_sound = pygame.mixer.Sound(file='data/sounds/player_tank_dead.wav')
penetration_sound = pygame.mixer.Sound(file='data/sounds/penetration.wav')
no_penetration_sound = pygame.mixer.Sound(file='data/sounds/no_penetration.wav')

shot_sound.set_volume(0.3)
back_sound.play(loops=-1, fade_ms=100)

# sprite groups
all_sprites = pygame.sprite.Group()
bullets_group = pygame.sprite.Group()
houses_group = pygame.sprite.Group()

top_borders_group = pygame.sprite.Group()
left_borders_group = pygame.sprite.Group()
right_borders_group = pygame.sprite.Group()
bottom_borders_group = pygame.sprite.Group()

player_group = pygame.sprite.Group()
enemies_group = pygame.sprite.Group()
boom_group = pygame.sprite.Group()


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


TILE_IMAGES = {
    'wall': load_image('house.png'),
    'empty': load_image('grass.png')
}
TANKS_IMAGES = {
    'player': load_image('tank_sheet.png', -1),
    'enemy': load_image('enemy_tank_sheet.png', -1)
}
BOOM_SHEET = load_image('boom_sheet.png', color_key=-1)
BULLET_SHEET = load_image('bullet_sheet.png', color_key=-1)


class Game:
    def __init__(self):
        self.won_screen_run = False
        self.lost_screen_run = False
        self.start_screen_run = True
        self.current_level = 0
        self.game_process()

    def game_process(self):
        player_won = False
        while self.current_level < MAX_LEVEL:
            if not player_won:
                self.current_level = 0
                start_screen = StartScreen()
                while start_screen.is_running():
                    pass

            middle_screen = MiddleScreen(*LEVELS[self.current_level][0])
            while middle_screen.is_running():
                pass
            game_level = GameLevel(LEVELS[self.current_level][1])
            player_won = None
            while player_won is None:
                player_won = game_level.is_player_won()
            pygame.mouse.set_visible(True)

            if player_won:
                win_or_lose_screen = WonScreen()
            else:
                win_or_lose_screen = LoseScreen()

            while win_or_lose_screen.is_running():
                pass

            self.current_level += 1

        terminate()


class Screen:
    def __init__(self, background_image):
        background = pygame.transform.scale(load_image(background_image), (WIDTH, HEIGHT))
        screen.blit(background, (0, 0))
        self.running = True
        self.btn = None

    def screen_loop(self):
        while self.running:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    terminate()
            events = pygame.event.get()
            pygame_widgets.update(events)
            pygame.display.flip()
            clock.tick(FPS)
        self.btn.hide()

    def is_running(self):
        return self.running

    def stop_screen(self):
        self.running = False


# start screen class
class StartScreen(Screen):
    def __init__(self):
        super().__init__(background_image='intro_screen.jpg')
        logo = pygame.transform.scale(load_image('logo.png', -1), TITLE_SIZE)
        screen.blit(logo, (WIDTH // 2 - logo.get_width() // 2, HEIGHT // 4 - logo.get_height()))

        self.btn = Button(screen,
                          WIDTH // 2 - BUTTON_SIZE[0] // 2, HEIGHT // 2, *BUTTON_SIZE,
                          radius=BUTTON_RADIUS,
                          image=load_image('play_btn.jpg'),
                          onClick=self.stop_screen
                          )

        self.screen_loop()


class MiddleScreen(Screen):
    def __init__(self, title, text, background_image):
        super().__init__(background_image=background_image)
        self.title = title
        self.text = text
        self.render_screen()

        self.btn = Button(screen,
                          WIDTH // 2 - BUTTON_SIZE[0] // 2, HEIGHT // 3 * 2, *BUTTON_SIZE,
                          radius=BUTTON_RADIUS,
                          image=load_image('accept.jpg'),
                          onClick=self.stop_screen
                          )
        self.screen_loop()

    def render_screen(self):
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


class WonScreen(Screen):
    def __init__(self):
        super().__init__(background_image='won_screen.jpg')

        self.btn = Button(screen,
                          WIDTH // 2 - BUTTON_SIZE[0] // 2, 3 * HEIGHT // 4, *BUTTON_SIZE,
                          radius=BUTTON_RADIUS,
                          image=load_image('go_forward.jpg'),
                          onClick=self.stop_screen
                          )

        self.render_screen()
        self.screen_loop()

    def render_screen(self):
        # title rendering
        font_title = pygame.font.Font(None, TITLE_TEXT_FONT_SIZE)
        title_rendered = font_title.render('ПОБЕДА!', True, TEXT_COLOR)
        intro_rect = title_rendered.get_rect()
        intro_rect.centerx = TITLE_TEXT_X
        intro_rect.top = TITLE_TEXT_TOP
        screen.fill(TEXT_BG, intro_rect)
        screen.blit(title_rendered, intro_rect)

        # main text rendering
        font_text = pygame.font.Font(None, MAIN_TEXT_FONT_SIZE)
        text_coord = MAIN_TEXT_TOP
        text = ['Это сражение удалось победить.', 'Вперёд, к следующим битвам.']
        for line in text:
            string_rendered = font_text.render(line, True, TEXT_COLOR)
            intro_rect = string_rendered.get_rect()
            intro_rect.centerx = MAIN_TEXT_X
            text_coord += 10
            intro_rect.top = text_coord
            text_coord += intro_rect.height
            screen.fill(TEXT_BG, intro_rect)
            screen.blit(string_rendered, intro_rect)


class LoseScreen(Screen):
    def __init__(self):
        super().__init__(background_image='lost_screen.jpg')

        self.btn = Button(screen,
                          WIDTH // 2 - BUTTON_SIZE[0] // 2, 3 * HEIGHT // 4, *BUTTON_SIZE,
                          radius=BUTTON_RADIUS,
                          image=load_image('back_to_main_menu.jpg'),
                          onClick=self.stop_screen
                          )

        self.render_screen()
        self.screen_loop()

    def render_screen(self):
        # title rendering
        font_title = pygame.font.Font(None, TITLE_TEXT_FONT_SIZE)
        title_rendered = font_title.render('Вы проиграли!', True, TEXT_COLOR)
        intro_rect = title_rendered.get_rect()
        intro_rect.centerx = TITLE_TEXT_X
        intro_rect.top = TITLE_TEXT_TOP
        screen.fill(TEXT_BG, intro_rect)
        screen.blit(title_rendered, intro_rect)

        # main text rendering
        font_text = pygame.font.Font(None, MAIN_TEXT_FONT_SIZE)
        text_coord = MAIN_TEXT_TOP
        text = ['Ваша страна понесла невосполнимые потери.', 'Теперь командованию придется репрессировать Вас...']
        for line in text:
            string_rendered = font_text.render(line, True, TEXT_COLOR)
            intro_rect = string_rendered.get_rect()
            intro_rect.centerx = MAIN_TEXT_X
            text_coord += 10
            intro_rect.top = text_coord
            text_coord += intro_rect.height
            screen.fill(TEXT_BG, intro_rect)
            screen.blit(string_rendered, intro_rect)


class Tank(pygame.sprite.Sprite):
    def __init__(self, sheet, row, col, pos_x, pos_y, game_level, *groups):
        super().__init__(all_sprites, *groups)
        self.frames = {}
        self.cut_sheet(sheet, col, row)
        self.game_level = game_level

        self.angle = 0
        self.image = self.frames[self.angle]
        self.rect = self.image.get_rect()
        self.rect.centerx = pos_x
        self.rect.centery = pos_y
        self.x = pos_x
        self.y = pos_y
        self.max_counter = RELOAD_TIME * FPS
        self.counter = 0
        self.is_reloaded = True

    def move(self, s, a, move_enable_string='00'):
        self.angle += a
        if move_enable_string in '00':
            self.x += s * cos(self.angle * pi / 180)
            self.y += -s * sin(self.angle * pi / 180)
        if move_enable_string == '+0':
            if self.x >= self.x + s * cos(self.angle * pi / 180):
                self.x += s * cos(self.angle * pi / 180)
            self.y += -s * sin(self.angle * pi / 180)
        if move_enable_string == '0+':
            if self.y >= self.y + -s * sin(self.angle * pi / 180):
                self.y += -s * sin(self.angle * pi / 180)
            self.x += s * cos(self.angle * pi / 180)
        if move_enable_string == '++':
            if self.x >= self.x + s * cos(self.angle * pi / 180):
                self.x += s * cos(self.angle * pi / 180)
            if self.y >= self.y + -s * sin(self.angle * pi / 180):
                self.y += -s * sin(self.angle * pi / 180)
        if move_enable_string == '-0':
            if self.x <= self.x + s * cos(self.angle * pi / 180):
                self.x += s * cos(self.angle * pi / 180)
            self.y += -s * sin(self.angle * pi / 180)
        if move_enable_string == 'n0':
            self.y += -s * sin(self.angle * pi / 180)
        if move_enable_string == '-+':
            if self.x <= self.x + s * cos(self.angle * pi / 180):
                self.x += s * cos(self.angle * pi / 180)
            if self.y >= self.y + -s * sin(self.angle * pi / 180):
                self.y += -s * sin(self.angle * pi / 180)
        if move_enable_string == 'n+':
            if self.y >= self.y + -s * sin(self.angle * pi / 180):
                self.y += -s * sin(self.angle * pi / 180)
        if move_enable_string == '0-':
            if self.y <= self.y + -s * sin(self.angle * pi / 180):
                self.y += -s * sin(self.angle * pi / 180)
            self.x += s * cos(self.angle * pi / 180)
        if move_enable_string == '+-':
            if self.x >= self.x + s * cos(self.angle * pi / 180):
                self.x += s * cos(self.angle * pi / 180)
            if self.y <= self.y + -s * sin(self.angle * pi / 180):
                self.y += -s * sin(self.angle * pi / 180)
        if move_enable_string == '0n':
            self.x += s * cos(self.angle * pi / 180)
        if move_enable_string == '+n':
            if self.x >= self.x + s * cos(self.angle * pi / 180):
                self.x += s * cos(self.angle * pi / 180)
        if move_enable_string == '--':
            if self.x <= self.x + s * cos(self.angle * pi / 180):
                self.x += s * cos(self.angle * pi / 180)
            if self.y <= self.y + -s * sin(self.angle * pi / 180):
                self.y += -s * sin(self.angle * pi / 180)
        if move_enable_string == 'n-':
            if self.y <= self.y + -s * sin(self.angle * pi / 180):
                self.y += -s * sin(self.angle * pi / 180)
        if move_enable_string == '-n':
            if self.x <= self.x + s * cos(self.angle * pi / 180):
                self.x += s * cos(self.angle * pi / 180)

    def update(self):
        if not self.is_reloaded:
            self.counter += 1
        if self.counter == self.max_counter:
            self.is_reloaded = True
            self.counter = 0
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
        x_for_bullet = self.x + 1 * self.rect.width / 2 * cos(self.angle * pi / 180)
        y_for_bullet = self.y + 1 * -self.rect.height / 2 * sin(self.angle * pi / 180)
        return self.angle, x_for_bullet, y_for_bullet

    def already_reloaded(self):
        return self.is_reloaded

    def reloading(self):
        self.is_reloaded = False


class Bullet(pygame.sprite.Sprite):
    def __init__(self, angle, pos_x, pos_y):
        super().__init__(all_sprites, bullets_group)

        self.angle = angle
        self.mask = None
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

        explode = False
        if not self.rect.colliderect(screen.get_rect()) or self.x > WIDTH or self.y > HEIGHT:
            explode = True

        for i in houses_group:
            if pygame.sprite.collide_mask(self, i):
                explode = True
        for i in enemies_group:
            if pygame.sprite.collide_mask(self, i):
                explode = True
                i.kill()
        for i in player_group:
            if pygame.sprite.collide_mask(self, i):
                explode = True
                i.kill()
                i.game_level.player_is_alive = False

        if explode:
            Boom(self.x, self.y)
            self.kill()

    def set_image_using_angle(self, angle):  # getting bullet image from bullet_sheet
        num_of_sprite = (angle // DELTA_ANGLE) % NUM_OF_FRAMES
        self.rect = pygame.Rect(0, 0, BULLET_SHEET.get_width() // NUM_OF_FRAMES, BULLET_SHEET.get_height() // 1)
        frame_location = (self.rect.w * num_of_sprite, 0)
        self.image = BULLET_SHEET.subsurface(pygame.Rect(frame_location, self.rect.size))
        self.mask = pygame.mask.from_surface(self.image)


class Boom(pygame.sprite.Sprite):
    rows, columns, = 6, 8

    def __init__(self, pos_x, pos_y):
        super().__init__(all_sprites, boom_group)
        self.frames = []
        self.cut_sheet()

        self.rect.centerx = pos_x
        self.rect.centery = pos_y

        self.limit = FPS // BOOM_FPS
        self.counter = 0
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]

    def update(self):
        self.counter += 1
        if self.counter == self.limit:
            self.counter = 0
            self.cur_frame += 1
            if self.cur_frame == len(self.frames):
                self.kill()
                return
            self.image = self.frames[self.cur_frame]

    def cut_sheet(self):
        self.rect = pygame.Rect(0, 0, BOOM_SHEET.get_width() // self.columns,
                                BOOM_SHEET.get_height() // self.rows)
        for i in range(self.rows):
            for j in range(self.columns):
                frame_location = (self.rect.w * j, self.rect.h * i)
                new_image = BOOM_SHEET.subsurface(pygame.Rect(frame_location, self.rect.size))
                self.frames.append(new_image)


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


def position_count(column, row):
    pos_x = (column + 1) * TILE_WIDTH - TILE_WIDTH // 2
    pos_y = (row + 1) * TILE_HEIGHT - TILE_HEIGHT // 2
    return pos_x, pos_y


class Enemy(Tank):
    def __init__(self, col, row, game_level):
        pos_x, pos_y = position_count(col, row)
        super().__init__(TANKS_IMAGES['enemy'], 1, NUM_OF_FRAMES, pos_x, pos_y, game_level, enemies_group)
        self.angle = random.randrange(2, 360, 2)
        self.angle_to_have = self.angle
        self.have_to_move_off_the_wall_a_bit = 0

    def rotated_to_needed_angle(self):
        return self.angle == self.angle_to_have

    def move(self, s, a, move_enable_string='00'):
        move_off_const = 2

        if self.angle < 0:
            self.angle += 360
        if self.angle >= 360:
            self.angle -= 360
        if self.angle_to_have < 0:
            self.angle_to_have += 360
        if self.angle_to_have >= 360:
            self.angle_to_have -= 360

        if self.angle != self.angle_to_have:
            # self.angle += DELTA_ANGLE
            if self.angle_to_have <= self.angle:
                if (self.angle - self.angle_to_have) <= 360 - abs(self.angle - self.angle_to_have):
                    self.angle -= DELTA_ANGLE
                else:
                    self.angle += DELTA_ANGLE
            else:
                if (self.angle - self.angle_to_have) > 360 - abs(self.angle - self.angle_to_have):
                    self.angle -= DELTA_ANGLE
                else:
                    self.angle += DELTA_ANGLE

        else:
            if self.have_to_move_off_the_wall_a_bit > 0:
                s = DELTA_DISTANCE_FOR_TANK
                self.x += s * cos(self.angle * pi / 180)
                self.y += -s * sin(self.angle * pi / 180)
                self.have_to_move_off_the_wall_a_bit -= 1

            else:
                if move_enable_string == '00':
                    self.x += s * cos(self.angle * pi / 180)
                    self.y += -s * sin(self.angle * pi / 180)
                if move_enable_string == '+0':
                    if self.x >= self.x + s * cos(self.angle * pi / 180):
                        self.x += s * cos(self.angle * pi / 180)
                        self.y += -s * sin(self.angle * pi / 180)
                    else:
                        self.angle_to_have = random.randrange(90, 270, 2)
                        self.have_to_move_off_the_wall_a_bit = move_off_const
                if move_enable_string == '0+':
                    if self.y >= self.y + -s * sin(self.angle * pi / 180):
                        self.y += -s * sin(self.angle * pi / 180)
                        self.x += s * cos(self.angle * pi / 180)
                    else:
                        self.angle_to_have = random.randrange(0, 180, 2)
                        self.have_to_move_off_the_wall_a_bit = move_off_const
                if move_enable_string == '++':
                    if self.x >= self.x + s * cos(self.angle * pi / 180) and \
                            self.y >= self.y + -s * sin(self.angle * pi / 180):
                        self.x += s * cos(self.angle * pi / 180)
                        self.y += -s * sin(self.angle * pi / 180)
                    else:
                        self.angle_to_have = random.randrange(90, 180, 2)
                        self.have_to_move_off_the_wall_a_bit = move_off_const
                if move_enable_string == '-0':
                    if self.x <= self.x + s * cos(self.angle * pi / 180):
                        self.x += s * cos(self.angle * pi / 180)
                        self.y += -s * sin(self.angle * pi / 180)
                    else:
                        self.angle_to_have = random.randrange(270, 450, 2)
                        self.have_to_move_off_the_wall_a_bit = move_off_const
                if move_enable_string == 'n0':
                    self.y += -s * sin(self.angle * pi / 180)
                if move_enable_string == '-+':
                    if self.x <= self.x + s * cos(self.angle * pi / 180) and \
                            self.y >= self.y + -s * sin(self.angle * pi / 180):
                        self.x += s * cos(self.angle * pi / 180)
                        self.y += -s * sin(self.angle * pi / 180)
                    else:
                        self.angle_to_have = random.randrange(0, 90, 2)
                        self.have_to_move_off_the_wall_a_bit = move_off_const
                if move_enable_string == 'n+':
                    if self.y >= self.y + -s * sin(self.angle * pi / 180):
                        self.y += -s * sin(self.angle * pi / 180)
                    else:
                        self.angle_to_have = 90
                        self.have_to_move_off_the_wall_a_bit = move_off_const
                if move_enable_string == '0-':
                    if self.y <= self.y + -s * sin(self.angle * pi / 180):
                        self.y += -s * sin(self.angle * pi / 180)
                        self.x += s * cos(self.angle * pi / 180)
                    else:
                        self.angle_to_have = random.randrange(180, 360, 2)
                        self.have_to_move_off_the_wall_a_bit = move_off_const
                if move_enable_string == '+-':
                    if self.x >= self.x + s * cos(self.angle * pi / 180) and \
                            self.y <= self.y + -s * sin(self.angle * pi / 180):
                        self.x += s * cos(self.angle * pi / 180)
                        self.y += -s * sin(self.angle * pi / 180)
                    else:
                        self.angle_to_have = random.randrange(180, 270, 2)
                        self.have_to_move_off_the_wall_a_bit = move_off_const
                if move_enable_string == '0n':
                    self.x += s * cos(self.angle * pi / 180)
                if move_enable_string == '+n':
                    if self.x >= self.x + s * cos(self.angle * pi / 180):
                        self.x += s * cos(self.angle * pi / 180)
                    else:
                        self.angle_to_have = 180
                        self.have_to_move_off_the_wall_a_bit = move_off_const
                if move_enable_string == '--':
                    if self.x <= self.x + s * cos(self.angle * pi / 180) and \
                            self.y <= self.y + -s * sin(self.angle * pi / 180):
                        self.x += s * cos(self.angle * pi / 180)
                        self.y += -s * sin(self.angle * pi / 180)
                    else:
                        self.angle_to_have = random.randrange(270, 360, 2)
                        self.have_to_move_off_the_wall_a_bit = move_off_const
                if move_enable_string == 'n-':
                    if self.y <= self.y + -s * sin(self.angle * pi / 180):
                        self.y += -s * sin(self.angle * pi / 180)
                    else:
                        self.angle_to_have = 270
                        self.have_to_move_off_the_wall_a_bit = move_off_const
                if move_enable_string == '-n':
                    if self.x <= self.x + s * cos(self.angle * pi / 180):
                        self.x += s * cos(self.angle * pi / 180)
                    else:
                        self.angle_to_have = 0
                        self.have_to_move_off_the_wall_a_bit = move_off_const


class Player(Tank):
    def __init__(self, col, row, game_level):
        pos_x, pos_y = position_count(col, row)
        super().__init__(TANKS_IMAGES['player'], 1, NUM_OF_FRAMES, pos_x, pos_y, game_level, player_group)


class GameLevel:
    def __init__(self, level_file):
        self.pause = False

        self.player_won = None
        self.running = True
        self.level_file = level_file
        self.houses = []
        self.player = None
        self.player_is_alive = True

        pygame.mouse.set_visible(False)

        for i in range(LEVEL_HEIGHT):
            pos_y = i * TILE_HEIGHT
            Border(0, pos_y, 0, pos_y + TILE_HEIGHT, right_borders_group)
            Border(LEVEL_WIDTH * TILE_WIDTH, pos_y,
                   LEVEL_WIDTH * TILE_WIDTH, pos_y + TILE_HEIGHT,
                   left_borders_group)
        for i in range(LEVEL_WIDTH):
            pos_x = i * TILE_WIDTH
            Border(pos_x, 0, pos_x + TILE_WIDTH, 0, bottom_borders_group)
            Border(pos_x, LEVEL_HEIGHT * TILE_HEIGHT,
                   pos_x + TILE_WIDTH, LEVEL_HEIGHT * TILE_HEIGHT,
                   top_borders_group)
        self.map = self.load_level_map()
        self.load_level()
        self.loop()

    def load_level_map(self):
        filename = os.path.join("data", 'level_maps', self.level_file)
        with open(filename) as map_file:
            level_map = [line.strip() for line in map_file]
        max_width = max(map(len, level_map))
        return list(map(lambda x: x.ljust(max_width, OBJECTS['empty']), level_map))

    def get_borders_dict(self, row, column):
        borders = {
            'bottom_border': True,
            'top_border': True,
            'right_border': True,
            'left_border': True
        }
        if row != len(self.map) - 1 and self.map[row + 1][column] == OBJECTS['wall']:
            borders['bottom_border'] = False
        if row != 0 and self.map[row - 1][column] == OBJECTS['wall']:
            borders['top_border'] = False
        if column != len(self.map[row]) - 1 and self.map[row][column + 1] == OBJECTS['wall']:
            borders['right_border'] = False
        if column != 0 and self.map[row][column - 1] == OBJECTS['wall']:
            borders['left_border'] = False
        return borders

    def load_level(self):
        for row in range(len(self.map)):
            for column in range(len(self.map[row])):
                if self.map[row][column] == OBJECTS['empty']:
                    Tile('empty', column, row)
                elif self.map[row][column] == OBJECTS['wall']:
                    borders = self.get_borders_dict(row, column)
                    self.houses.append(House('wall', column, row, borders))
                elif self.map[row][column] == OBJECTS['enemy']:
                    Tile('empty', column, row)
                    Enemy(column, row, self)
                elif self.map[row][column] == OBJECTS['player']:
                    Tile('empty', column, row)
                    self.player = Player(column, row, self)

    def move_player(self, ds, da):
        move_up = True
        move_down = True
        move_left = True
        move_right = True
        for i in top_borders_group:
            if pygame.sprite.collide_mask(self.player, i):
                move_down = False
        for i in bottom_borders_group:
            if pygame.sprite.collide_mask(self.player, i):
                move_up = False
        for i in right_borders_group:
            if pygame.sprite.collide_mask(self.player, i):
                move_left = False
        for i in left_borders_group:
            if pygame.sprite.collide_mask(self.player, i):
                move_right = False
        if move_up and move_left and move_down and move_right:
            self.player.move(ds, da, '00')

        elif move_up and move_left and move_down and not move_right:
            self.player.move(ds, da, '+0')
        elif move_up and move_left and not move_down and move_right:
            self.player.move(ds, da, '0+')
        elif move_up and move_left and not move_down and not move_right:
            self.player.move(ds, da, '++')
        elif move_up and not move_left and move_down and move_right:
            self.player.move(ds, da, '-0')
        elif move_up and not move_left and move_down and not move_right:
            self.player.move(ds, da, 'n0')
        elif move_up and not move_left and not move_down and move_right:
            self.player.move(ds, da, '-+')
        elif move_up and not move_left and not move_down and not move_right:
            self.player.move(ds, da, 'n+')
        elif not move_up and move_left and move_down and move_right:
            self.player.move(ds, da, '0-')
        elif not move_up and move_left and move_down and not move_right:
            self.player.move(ds, da, '+-')
        elif not move_up and move_left and not move_down and move_right:
            self.player.move(ds, da, '0n')
        elif not move_up and move_left and not move_down and not move_right:
            self.player.move(ds, da, '+n')
        elif not move_up and not move_left and move_down and move_right:
            self.player.move(ds, da, '--')
        elif not move_up and not move_left and move_down and not move_right:
            self.player.move(ds, da, 'n-')
        elif not move_up and not move_left and not move_down and move_right:
            self.player.move(ds, da, '-n')
        elif not move_up and not move_left and not move_down and not move_right:
            self.player.move(ds, da, 'nn')

    def move_enemies(self):
        if len(enemies_group):
            for i in enemies_group:
                self.move_enemy(i)
        else:
            self.player_won = True

    def do_aiming(self, enemy):
        delta_x = self.player.x - enemy.x
        delta_y = self.player.y - enemy.y
        a = delta_y
        b = -delta_x
        c = -enemy.x * delta_y + enemy.y * delta_x
        can_collide_with_house = False
        pygame.draw.line(screen, (0, 0, 0),
                         (self.player.x, self.player.y), (enemy.x, enemy.y))
        for house in self.houses:
            x, y = house.rect.x, house.rect.y
            if ((a * x + b * y + c) > 0 and (a * (x + TILE_WIDTH) + b * (y + TILE_HEIGHT) + c) < 0 or
                (a * x + b * y + c) < 0 and (a * (x + TILE_WIDTH) + b * (y + TILE_HEIGHT) + c) > 0 or
                (a * (x + TILE_WIDTH) + b * y + c) > 0 and (a * x + b * (y + TILE_HEIGHT) + c) < 0 or
                (a * (x + TILE_WIDTH) + b * y + c) < 0 and (a * x + b * (y + TILE_HEIGHT) + c) > 0) and \
                    (self.player.x <= x <= enemy.x or enemy.x <= x <= self.player.x) and \
                    (self.player.y <= y <= enemy.y or enemy.y <= y <= self.player.y):
                can_collide_with_house = True
                break
        try:
            angle = int(math.atan(a / b) * 180 / pi + 0.5)
        except ZeroDivisionError:
            angle = 90
        if angle % 2 == 1:
            angle -= 1

        return not can_collide_with_house, angle  # возвращает можно ли целится и угол прямой
        # по которой нужно стрелять

    def check_tank_pos(self, enemy):
        pl_x, pl_y = self.player.rect.centerx, self.player.rect.centery
        en_x, en_y = enemy.rect.centerx, enemy.rect.centery
        can_aim, angle = self.do_aiming(enemy)

        if 100 > en_x - pl_x > 0 and 100 > en_y - pl_y > 0:
            angle = 226
        elif -100 < en_x - pl_x < 0 and -100 < en_y - pl_y < 0:
            angle = 406
        elif 100 > en_x - pl_x > 0 and -100 < en_y - pl_y < 0:
            angle = 136
        elif -100 < en_x - pl_x < 0 and 100 > en_y - pl_y > 0:
            angle = 316
        else:
            angle = enemy.angle

        return angle, can_aim

    def able_to_shoot(self, enemy):
        player_distance = math.sqrt((self.player.rect.centerx - enemy.rect.centerx) ** 2 +
                                    (self.player.rect.centery - enemy.rect.centery) ** 2)
        enemy_x, enemy_y, enemy_angle = enemy.rect.centerx, enemy.rect.centery, enemy.angle
        player_x_suppose, player_y_suppose = enemy_x + player_distance * math.cos(math.radians(enemy_angle)), \
                                             enemy_y - player_distance * math.sin(math.radians(enemy_angle))
        if player_x_suppose - D_X_FOR_SHOOTING <= self.player.rect.centerx <= player_x_suppose + D_X_FOR_SHOOTING and \
                player_y_suppose - D_X_FOR_SHOOTING <= self.player.rect.centery <= player_y_suppose + D_X_FOR_SHOOTING:
            self.shoot(enemy)

    def move_enemy(self, enemy, ds=DELTA_DISTANCE_FOR_TANK, da=0):
        move_up = True
        move_down = True
        move_left = True
        move_right = True
        for i in top_borders_group:
            if pygame.sprite.collide_mask(enemy, i):
                move_down = False
        for i in bottom_borders_group:
            if pygame.sprite.collide_mask(enemy, i):
                move_up = False
        for i in right_borders_group:
            if pygame.sprite.collide_mask(enemy, i):
                move_left = False
        for i in left_borders_group:
            if pygame.sprite.collide_mask(enemy, i):
                move_right = False

        for i in enemies_group:
            if i != enemy:
                if pygame.sprite.collide_mask(enemy, i):
                    coordinates = enemy.rect.centerx, enemy.rect.centery
                    enemy.kill()
                    i.kill()
                    Boom(*coordinates)

        if pygame.sprite.collide_mask(enemy, self.player):
            coordinates = self.player.rect.centerx, self.player.rect.centery
            enemy.kill()
            self.player.kill()
            Boom(*coordinates)
            self.player_is_alive = False

        information = self.check_tank_pos(enemy)
        if information[1]:
            self.able_to_shoot(enemy)
        angle = information[0]

        if move_up and move_left and move_down and move_right:
            if enemy.rotated_to_needed_angle():
                enemy.angle_to_have = angle
            enemy.move(ds, da, '00')
        elif move_up and move_left and move_down and not move_right:
            enemy.move(ds, da, '+0')
        elif move_up and move_left and not move_down and move_right:
            enemy.move(ds, da, '0+')
        elif move_up and move_left and not move_down and not move_right:
            enemy.move(ds, da, '++')
        elif move_up and not move_left and move_down and move_right:
            enemy.move(ds, da, '-0')
        elif move_up and not move_left and move_down and not move_right:
            enemy.move(ds, da, 'n0')
        elif move_up and not move_left and not move_down and move_right:
            enemy.move(ds, da, '-+')
        elif move_up and not move_left and not move_down and not move_right:
            enemy.move(ds, da, 'n+')
        elif not move_up and move_left and move_down and move_right:
            enemy.move(ds, da, '0-')
        elif not move_up and move_left and move_down and not move_right:
            enemy.move(ds, da, '+-')
        elif not move_up and move_left and not move_down and move_right:
            enemy.move(ds, da, '0n')
        elif not move_up and move_left and not move_down and not move_right:
            enemy.move(ds, da, '+n')
        elif not move_up and not move_left and move_down and move_right:
            enemy.move(ds, da, '--')
        elif not move_up and not move_left and move_down and not move_right:
            enemy.move(ds, da, 'n-')
        elif not move_up and not move_left and not move_down and move_right:
            enemy.move(ds, da, '-n')
        elif not move_up and not move_left and not move_down and not move_right:
            enemy.move(ds, da, 'nn')

    def shoot(self, tank):
        # make bullet if tank is reloaded
        if tank.already_reloaded():
            angle, x, y = tank.get_position_and_angle_for_bullet()
            Bullet(angle, x, y)
            if tank == self.player:
                shot_sound.stop()
                shot_sound.play(loops=0)
            tank.reloading()

    def check_pressed(self):
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
            self.move_player(ds, da)

    def do_pause(self):
        pygame.draw.polygon(screen, PAUSE_COLOR,
                            ((int(WIDTH / 2 - WIDTH / 16), int(HEIGHT / 2 - HEIGHT / 12)),
                             (int(WIDTH / 2 + WIDTH / 16), int(HEIGHT / 2)),
                             (int(WIDTH / 2 - WIDTH / 16), int(HEIGHT / 2 + HEIGHT / 12)))
                            )
        pygame.draw.polygon(screen, pygame.Color(0, 0, 0),
                            ((int(WIDTH / 2 - WIDTH / 16), int(HEIGHT / 2 - HEIGHT / 12)),
                             (int(WIDTH / 2 + WIDTH / 16), int(HEIGHT / 2)),
                             (int(WIDTH / 2 - WIDTH / 16), int(HEIGHT / 2 + HEIGHT / 12))),
                            width=2)
        pygame.display.flip()

    def loop(self):
        while self.running:
            if not self.player_is_alive:
                self.running = False
            if self.player_won:
                self.running = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                if event.type == pygame.MOUSEBUTTONDOWN and not self.pause:
                    if event.button == 1:
                        self.shoot(self.player)
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        if not self.pause:
                            self.pause = True
                            self.do_pause()
                        else:
                            self.pause = False
            if not self.pause:
                screen.fill(BACKGROUND)
                self.check_pressed()
                self.move_enemies()
                all_sprites.draw(screen)
                enemies_group.draw(screen)
                player_group.draw(screen)
                boom_group.draw(screen)

                all_sprites.update()
                pygame.display.flip()
                clock.tick(FPS)

        if not self.player_is_alive:
            for j in all_sprites:
                j.kill()
            self.player_won = False

        if self.player_won:
            for j in all_sprites:
                j.kill()

    def is_player_won(self):
        if not self.running:
            return self.player_won


# for i in range(1, 6):
#     generate(f'{i}_level.txt')

Game()
