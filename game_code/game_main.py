import pygame
from game_code.universal_constants import WIDTH, HEIGHT

pygame.init()

# window constants
GAME_TITLE = 'WWII: Величайшие танковые битвы'

# screen and clock init
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption(GAME_TITLE)

from game_code.game_level_class import GameLevel
from game_code.screens import StartScreen, WonScreen, MiddleScreen, LoseScreen, EndScreen
from game_code.level_attributes import LEVELS

MAX_LEVEL = 5


class Game:
    def __init__(self, main_screen, main_clock):
        self.screen = main_screen
        self.clock = main_clock

        self.won_screen_run = False
        self.lost_screen_run = False
        self.start_screen_run = True
        self.current_level = 0
        self.screen_process(StartScreen)

    def screen_process(self, cur_screen):
        next_screen = None
        if cur_screen == WonScreen:
            cur_screen = WonScreen(self.screen, self.clock)
            next_screen = MiddleScreen
            self.current_level += 1
        elif cur_screen == LoseScreen:
            cur_screen = LoseScreen(self.screen, self.clock)
            next_screen = StartScreen
            self.current_level = 0
        elif cur_screen == StartScreen:
            next_screen = MiddleScreen
            cur_screen = StartScreen(self.screen, self.clock)
        elif cur_screen == MiddleScreen:
            cur_screen = MiddleScreen(self.screen, self.clock, *LEVELS[self.current_level][0])
            next_screen = GameLevel
        elif cur_screen == EndScreen:
            cur_screen = EndScreen(self.screen, self.clock)
            next_screen = StartScreen

        if self.current_level == MAX_LEVEL:
            next_screen = EndScreen
            self.current_level = 0

        while cur_screen.is_running():
            pass

        if next_screen == GameLevel:
            self.level_process()
        else:
            self.screen_process(next_screen)

    def level_process(self):
        game_level = GameLevel(self.screen, self.clock, LEVELS[self.current_level][1])
        player_won = None
        while player_won is None:
            player_won = game_level.is_player_won()
        pygame.mouse.set_visible(True)

        if player_won:
            self.screen_process(WonScreen)
        else:
            self.screen_process(LoseScreen)


Game(screen, clock)
