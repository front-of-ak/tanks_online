import os

import pygame

back_sound = pygame.mixer.Sound(file=os.path.join("../data", 'sounds', 'hoi4mainthemeallies.wav'))
shot_sound = pygame.mixer.Sound(file='../data/sounds/shot.wav')
player_tank_dead_sound = pygame.mixer.Sound(file='../data/sounds/player_tank_dead.wav')
# penetration_sound = pygame.mixer.Sound(file='data/sounds/penetration.wav')
# no_penetration_sound = pygame.mixer.Sound(file='data/sounds/no_penetration.wav')

shot_sound.set_volume(0.3)
back_sound.set_volume(0.8)
back_sound.play(loops=-1, fade_ms=100)
