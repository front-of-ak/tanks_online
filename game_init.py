import os
import sys
import pygame
import pygame_widgets

from pygame_widgets.button import Button
from math import sin, cos, pi
# from screen_attributes import screens

pygame.init()

# constants
FPS = 60
WIDTH = 1080
HEIGHT = 800
BACKGROUND = pygame.color.Color('black')

FONT_SIZE = 32
TEXT_COORD = TEXT_X, TEXT_Y = 40, 300
TEXT_BG = (242, 232, 201)

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

# screen and clock init
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption(GAME_TITLE)
# sprite groups
all_sprites = pygame.sprite.Group()
bullets_group = pygame.sprite.Group()


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
    start_screen_run = True

    Button(screen,
           WIDTH // 2 - BUTTON_SIZE[0] // 2, HEIGHT // 2, *BUTTON_SIZE,
           radius=BUTTON_RADIUS,
           image=load_image('play_btn.jpg'),
           onClick=break_start_screen
           )

    while start_screen_run:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                terminate()
            if not start_screen_run:
                screen.fill(BACKGROUND)
                return
        events = pygame.event.get()
        pygame_widgets.update(events)
        pygame.display.flip()
        clock.tick(FPS)


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
        x_for_bullet = self.x + self.rect.width / 2 * cos(self.angle * pi / 180)
        y_for_bullet = self.y + -self.rect.height / 2 * sin(self.angle * pi / 180)
        return self.angle, x_for_bullet, y_for_bullet


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
            Boom(self.x, self.y)
            self.kill()

    def set_image_using_angle(self, angle):  # getting bullet image from bullet_sheet
        num_of_sprite = (angle // DELTA_ANGLE) % NUM_OF_FRAMES
        self.rect = pygame.Rect(0, 0, self.sheet.get_width() // NUM_OF_FRAMES, self.sheet.get_height() // 1)
        frame_location = (self.rect.w * num_of_sprite, 0)
        self.image = self.sheet.subsurface(pygame.Rect(frame_location, self.rect.size))


class Boom(pygame.sprite.Sprite):
    sheet = load_image('boom_sheet.png', color_key=-1)
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
        self.rect = pygame.Rect(0, 0, self.sheet.get_width() // self.columns,
                                self.sheet.get_height() // self.rows)
        for i in range(self.rows):
            for j in range(self.columns):
                frame_location = (self.rect.w * j, self.rect.h * i)
                new_image = self.sheet.subsurface(pygame.Rect(frame_location, self.rect.size))
                self.frames.append(new_image)


class MiddleScreen:
    def __init__(self, title, text, background_image):
        self.render_screen(title, text, background_image)

        self.button_next = Button(screen,
                                  WIDTH - BUTTON_SIZE[0] - 10, HEIGHT - BUTTON_SIZE[1] - 10, *BUTTON_SIZE,
                                  radius=BUTTON_RADIUS,
                                  image=load_image('accept.jpg'),
                                  onClick=lambda: print(1)
                                  )

        while True:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    terminate()
            events = pygame.event.get()
            pygame_widgets.update(events)
            pygame.display.flip()
            clock.tick(FPS)

    def render_screen(self, title, text, background_image):
        background = pygame.transform.scale(load_image(background_image), (WIDTH, HEIGHT))
        screen.blit(background, (0, 0))
        font = pygame.font.Font(None, FONT_SIZE)
        text_coord = TEXT_Y
        for line in text:
            string_rendered = font.render(line, True, 'black')
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = TEXT_X
            text_coord += intro_rect.height
            screen.fill(TEXT_BG, intro_rect)
            screen.blit(string_rendered, intro_rect)


start_screen()

# first_screen = MiddleScreen(screens[0]['title'], screens[0]['text'], screens[0]['background'])

# main game cycle
player_tank = Tank(load_image('tank_sheet.png'), 1, NUM_OF_FRAMES, 500, 500)
pygame.mouse.set_visible(False)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # make bullet if you press left mouse button
                angle, x, y = player_tank.get_position_and_angle_for_bullet()
                Bullet(angle, x, y)

    screen.fill(BACKGROUND)

    check_pressed()

    all_sprites.draw(screen)
    all_sprites.update()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
terminate()
