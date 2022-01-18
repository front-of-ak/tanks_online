import os
import pygame

screens_sound = pygame.mixer.Sound(file=os.path.join("data", 'sounds', 'hoi4mainthemeallies.wav'))

fir_level_music = pygame.mixer.Sound(file=os.path.join("data", 'sounds', 'axistheme.wav'))
sec_level_music = pygame.mixer.Sound(file=os.path.join("data", 'sounds', 'operationbarbarossa.wav'))
thi_level_music = pygame.mixer.Sound(file=os.path.join("data", 'sounds', 'thegreatpatrioticwar.wav'))
for_level_music = pygame.mixer.Sound(file=os.path.join("data", 'sounds', 'themightofsovietunion.wav'))
fif_level_music = pygame.mixer.Sound(file=os.path.join("data", 'sounds', 'sovietvictory.wav'))

shot_sound = pygame.mixer.Sound(file=os.path.join("data", 'sounds', 'shot.wav'))
player_tank_dead_sound = pygame.mixer.Sound(file=os.path.join("data", 'sounds', 'player_tank_dead.wav'))
penetration_sound = pygame.mixer.Sound(file=os.path.join("data", 'sounds', 'penetration.wav'))

shot_sound.set_volume(0.3)
penetration_sound.set_volume(1)
screens_sound.set_volume(0.8)
screens_sound.play(loops=-1, fade_ms=100)
