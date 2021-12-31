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
LEVEL_WIDTH, LEVEL_HEIGHT = 27, 20
TILE_WIDTH = WIDTH / LEVEL_WIDTH
TILE_HEIGHT = HEIGHT / LEVEL_HEIGHT
BACKGROUND = pygame.color.Color('white')

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
BOOM_FPS = 48
RELOAD_TIME = 2

OBJECTS = {'empty': '.', 'wall': '/', 'enemy': '-', 'player': '@'}

# screen and clock init
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption(GAME_TITLE)

# music init
back_sound = pygame.mixer.Sound(file='data/sounds/malinovka.wav')
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
TILE_IMAGES = {
    'wall': load_image('house.png'),
    'empty': load_image('grass.png')
}
TANKS_IMAGES = {
    'player': load_image('tank_sheet.png', -1),
    'enemy': load_image('enemy_tank_sheet.png', -1)
}
SHEET = load_image('boom_sheet.png', color_key=-1)


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


class Tank(pygame.sprite.Sprite):
    def __init__(self, sheet, row, col, pos_x, pos_y, *groups):
        super().__init__(all_sprites, *groups)
        self.frames = {}
        self.cut_sheet(sheet, col, row)

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
        x_for_bullet = self.x + self.rect.width / 2 * cos(self.angle * pi / 180)
        y_for_bullet = self.y + -self.rect.height / 2 * sin(self.angle * pi / 180)
        return self.angle, x_for_bullet, y_for_bullet

    def already_reloaded(self):
        return self.is_reloaded

    def reloading(self):
        self.is_reloaded = False


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

        if not self.rect.colliderect(screen.get_rect()) or self.x > WIDTH or self.y > HEIGHT:
            Boom(self.x, self.y)
            self.kill()

    def set_image_using_angle(self, angle):  # getting bullet image from bullet_sheet
        num_of_sprite = (angle // DELTA_ANGLE) % NUM_OF_FRAMES
        self.rect = pygame.Rect(0, 0, self.sheet.get_width() // NUM_OF_FRAMES, self.sheet.get_height() // 1)
        frame_location = (self.rect.w * num_of_sprite, 0)
        self.image = self.sheet.subsurface(pygame.Rect(frame_location, self.rect.size))


class Boom(pygame.sprite.Sprite):
    rows, columns, = 6, 8

    def __init__(self, pos_x, pos_y):
        super().__init__(all_sprites)
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
        self.rect = pygame.Rect(0, 0, SHEET.get_width() // self.columns,
                                SHEET.get_height() // self.rows)
        for i in range(self.rows):
            for j in range(self.columns):
                frame_location = (self.rect.w * j, self.rect.h * i)
                new_image = SHEET.subsurface(pygame.Rect(frame_location, self.rect.size))
                self.frames.append(new_image)


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
    pos_x = column * TILE_WIDTH - TILE_WIDTH // 2
    pos_y = row * TILE_HEIGHT - TILE_HEIGHT // 2
    return pos_x, pos_y


class Enemy(Tank):
    def __init__(self, col, row):
        pos_x, pos_y = position_count(col, row)
        super().__init__(TANKS_IMAGES['enemy'], 1, NUM_OF_FRAMES, pos_x, pos_y, enemies_group)


class Player(Tank):
    def __init__(self, col, row):
        pos_x, pos_y = position_count(col, row)
        super().__init__(TANKS_IMAGES['player'], 1, NUM_OF_FRAMES, pos_x, pos_y, player_group)


class GameLevel:
    def __init__(self, level_file):
        self.running = True
        self.level_file = level_file
        self.enemies = []
        self.houses = []
        self.player = None

        pygame.mouse.set_visible(False)

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
                    self.enemies.append(Enemy(column, row))
                elif self.map[row][column] == OBJECTS['player']:
                    Tile('empty', column, row)
                    self.player = Player(column, row)

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

    def move_enemy(self):
        pass

    def shoot(self, tank):
        # make bullet if tank is reloaded
        if tank.already_reloaded():
            angle, x, y = tank.get_position_and_angle_for_bullet()
            Bullet(angle, x, y)
            if tank == self.player:
                shot_sound.stop()
                shot_sound.play(loops=-1, fade_ms=100)
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
        self.move_enemy()

    def loop(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.shoot(self.player)
            for i in self.enemies:
                self.shoot(i)
            screen.fill(BACKGROUND)
            self.check_pressed()
            enemies_group.draw(screen)
            all_sprites.draw(screen)
            all_sprites.update()
            player_group.draw(screen)

            pygame.display.flip()
            clock.tick(FPS)


start_screen()
first_screen = MiddleScreen(screens[0]['title'],
                            screens[0]['text'],
                            screens[0]['background'])

first_level = GameLevel('first_level.txt')
terminate()
