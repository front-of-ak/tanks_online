import random
import pygame

from math import pi, cos, sin
from different_funcs import position_count, load_image
from sprite_groups import enemies_group, player_group, all_sprites
from universal_constants import FPS, DELTA_ANGLE, NUM_OF_FRAMES, DELTA_DISTANCE_FOR_TANK

RELOAD_TIME = 2

TANKS_IMAGES = {
    'player': load_image('player_tank_sheet.png', -1),
    'enemy': load_image('enemy_tank_sheet.png', -1)
}


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
