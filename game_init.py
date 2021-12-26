import os
import sys
import pygame_widgets
from pygame_widgets.button import Button
from math import sin, cos, pi
import pygame

pygame.init()

# constants
FPS = 60
WIDTH = 1080
HEIGHT = 800
BACKGROUND = pygame.color.Color('black')

GAME_TITLE = 'WWII: Величайшие танковые битвы'
TITLE_SIZE = (458, 106)
TITLE_COORDINATES = (50, 20)

BUTTON_SIZE = 391, 62
BUTTON_RADIUS = 10

DELTA_A = 2
DELTA_S = 3
NUM_OF_FRAMES = 360 // DELTA_A


# screen and clock init
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption(GAME_TITLE)
# sprite groups
all_sprites = pygame.sprite.Group()


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

    button_play = Button(screen,
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
                return
        events = pygame.event.get()
        pygame_widgets.update(events)
        pygame.display.flip()
        clock.tick(FPS)


class Player(pygame.sprite.Sprite):
    def __init__(self, sheet, row, col, pos_x, pos_y):
        super().__init__(all_sprites)
        self.frames = {}
        self.cut_sheet(sheet, col, row)

        self.a = 0
        self.image = self.frames[self.a]
        self.rect = self.image.get_rect()
        self.rect.centerx = pos_x
        self.rect.centery = pos_y
        self.x = pos_x
        self.y = pos_y

    def move(self, s, a):
        self.a += a
        self.x += s * cos(self.a * pi / 180)
        self.y += -s * sin(self.a * pi / 180)

        self.image = self.frames[(self.a + 360) % 360]
        self.rect = self.image.get_rect()
        self.rect.centerx = self.x
        self.rect.centery = self.y

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for i in range(rows):
            for j in range(columns):
                frame_location = (self.rect.w * j, self.rect.h * i)
                self.frames[(columns * i + j) * DELTA_A] = sheet.subsurface(pygame.Rect(frame_location, self.rect.size))


def check_pressed():
    ds = 0
    da = 0
    if pygame.key.get_pressed()[pygame.K_LEFT]:
        da += DELTA_A
    elif pygame.key.get_pressed()[pygame.K_RIGHT]:
        da -= DELTA_A
    elif pygame.key.get_pressed()[pygame.K_UP]:
        ds += DELTA_S
    elif pygame.key.get_pressed()[pygame.K_DOWN]:
        ds -= DELTA_S
    if ds or da:
        player.move(ds, da)


start_screen()
# main game cycle
player = Player(load_image('tank_sheet.png'), 1, NUM_OF_FRAMES, 500, 500)
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BACKGROUND)

    check_pressed()

    all_sprites.draw(screen)
    all_sprites.update()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
terminate()
