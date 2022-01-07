import os
import random

OBJECTS = ['.', '/', '-', '@']


def generate(level_name):
    level_map = []
    enemies = 0
    for i in range(20):
        level_map.append([])
        areHouses = random.choice((True, False, True, True))
        areEnemies = random.choice((False, False, True))
        houses_positions = []
        enemies_positions = []
        if areHouses:
            houses_amount = random.randint(0, 15)
            for _ in range(houses_amount):
                temp_pos = random.randint(0, 27)
                while temp_pos in houses_positions:
                    temp_pos = random.randint(0, 27)
                houses_positions.append(temp_pos)
        if areEnemies and enemies <= 5:
            enemies_amount = random.randint(1, 2)
            enemies += 1
            for _ in range(enemies_amount):
                temp_pos = random.randint(0, 27)
                while temp_pos in enemies_positions and temp_pos in houses_positions:
                    temp_pos = random.randint(0, 27)
                enemies_positions.append(temp_pos)
        for j in range(27):
            if i == 0 and j == 0:
                level_map[i].append('@')
            elif j in houses_positions:
                level_map[i].append('/')
            elif j in enemies_positions:
                level_map[i].append('-')
            else:
                level_map[i].append('.')
    with open(os.path.join('data', 'level_maps', level_name), mode='wt', encoding='utf-8') as f:
        for i in level_map:
            f.write(''.join(i) + '\n')
