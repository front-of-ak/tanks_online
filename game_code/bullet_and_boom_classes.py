from math import cos, pi, sin

import pygame

from game_code.different_funcs import load_image
from game_code.universal_constants import WIDTH, HEIGHT, FPS, DELTA_ANGLE, NUM_OF_FRAMES, BOOM_FPS
from game_code.sprite_groups import all_sprites, bullets_group, houses_group, enemies_group, player_group, boom_group

DELTA_DISTANCE_FOR_BULLET = 12

BOOM_SHEET = load_image('boom_sheet.png', color_key=-1)
BULLET_SHEET = load_image('bullet_sheet.png', color_key=-1)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, screen, angle, pos_x, pos_y):
        super().__init__(all_sprites, bullets_group)

        self.screen = screen

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
        if not self.rect.colliderect(self.screen.get_rect()) or self.x > WIDTH or self.y > HEIGHT:
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
                i.game_level.player_is_alive = False  # serious prbl (макс гений инкапсуляция)

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
