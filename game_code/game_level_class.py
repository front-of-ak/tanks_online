import math
import os
import pygame

from math import pi, atan
from bullet_and_boom_classes import Bullet, Boom
from different_funcs import terminate
from our_errors import PlayerIsDeadError
from sound_init import shot_sound, player_tank_dead_sound
from tanks_classes import Enemy, Player
from tile_classes import Border, Tile, House
from universal_constants import LEVEL_HEIGHT, TILE_HEIGHT, TILE_WIDTH, LEVEL_WIDTH, DELTA_DISTANCE_FOR_TANK, \
    DELTA_ANGLE, WIDTH, HEIGHT, FPS
from sprite_groups import right_borders_group, bottom_borders_group, left_borders_group, top_borders_group, \
    enemies_group, all_sprites, player_group, boom_group

OBJECTS = {'empty': '.', 'wall': '/', 'enemy': '-', 'player': '@', 'stone': '*', 'earth': '&'}

BACKGROUND = pygame.color.Color('white')
PAUSE_COLOR = pygame.Color(81, 144, 174)

D_X_FOR_SHOOTING = 15


class GameLevel:
    def __init__(self, screen, clock, level_file, prev_music, music_for_this_level):
        self.pause = False

        self.screen = screen
        self.clock = clock

        self.player_won = None
        self.running = True
        self.level_file = level_file
        self.houses = []
        self.player = None
        self.player_is_alive = True

        if prev_music != music_for_this_level:
            prev_music.stop()
            music_for_this_level.set_volume(0.8)
            music_for_this_level.play(loops=-1, fade_ms=100)

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
        filename = os.path.join("../data", 'level_maps', self.level_file)
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
                elif self.map[row][column] == OBJECTS['stone']:
                    Tile('stone', column, row)
                elif self.map[row][column] == OBJECTS['earth']:
                    Tile('earth', column, row)

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
        pygame.draw.line(self.screen, (0, 0, 0),
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
            angle = int(atan(a / b) * 180 / pi + 0.5)
        except ZeroDivisionError:
            angle = 90
        if angle % 2 == 1:
            angle -= 1

        return not can_collide_with_house, angle

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
        player_x_suppose = enemy_x + player_distance * math.cos(math.radians(enemy_angle))
        player_y_suppose = enemy_y - player_distance * math.sin(math.radians(enemy_angle))
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
            Bullet(self.screen, angle, x, y)
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
        pygame.draw.polygon(self.screen, PAUSE_COLOR,
                            ((int(WIDTH / 2 - WIDTH / 16), int(HEIGHT / 2 - HEIGHT / 12)),
                             (int(WIDTH / 2 + WIDTH / 16), int(HEIGHT / 2)),
                             (int(WIDTH / 2 - WIDTH / 16), int(HEIGHT / 2 + HEIGHT / 12)))
                            )
        pygame.draw.polygon(self.screen, pygame.Color(0, 0, 0),
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
                    if event.key == pygame.K_k:
                        for j in enemies_group:
                            j.kill()
            if not self.pause:
                self.screen.fill(BACKGROUND)
                self.check_pressed()
                self.move_enemies()
                all_sprites.draw(self.screen)
                enemies_group.draw(self.screen)
                player_group.draw(self.screen)
                boom_group.draw(self.screen)

                try:
                    all_sprites.update()
                except PlayerIsDeadError:
                    self.player_is_alive = False
                pygame.display.flip()
                self.clock.tick(FPS)

        if not self.player_is_alive:
            player_tank_dead_sound.play(loops=0)
            for j in all_sprites:
                j.kill()
            self.player_won = False

        if self.player_won:
            for j in all_sprites:
                j.kill()

    def is_player_won(self):
        if not self.running:
            return self.player_won
