import pygame
import pygame_widgets
from pygame_widgets.button import Button

from game_code.different_funcs import load_image, terminate
from game_code.universal_constants import WIDTH, HEIGHT, FPS

# text parameters
MAIN_TEXT_FONT_SIZE = 32
TITLE_TEXT_FONT_SIZE = 100
TITLE_TEXT_COORD = TITLE_TEXT_X, TITLE_TEXT_TOP = WIDTH // 2, 20
TEXT_COORD = MAIN_TEXT_X, MAIN_TEXT_TOP = WIDTH // 2, 300
TEXT_BG = (242, 232, 201)
TEXT_COLOR = 'black'

# title parameters
TITLE_SIZE = (458, 106)
TITLE_COORDINATES = (50, 20)

# button parameters
BUTTON_SIZE = 391, 62
BUTTON_RADIUS = 10


class Screen:
    def __init__(self, screen, clock, background_image):
        background = pygame.transform.scale(load_image(background_image), (WIDTH, HEIGHT))
        self.running = True
        self.btn = None
        self.screen = screen
        self.clock = clock
        self.screen.blit(background, (0, 0))

    def screen_loop(self):
        while self.running:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    terminate()
            events = pygame.event.get()
            pygame_widgets.update(events)
            pygame.display.flip()
            self.clock.tick(FPS)
        self.btn.hide()

    def is_running(self):
        return self.running

    def stop_screen(self):
        self.running = False


# start screen class
class StartScreen(Screen):
    def __init__(self, screen, clock):
        super().__init__(screen, clock, background_image='intro_screen.jpg')
        logo = pygame.transform.scale(load_image('logo.png', -1), TITLE_SIZE)
        self.screen.blit(logo, (WIDTH // 2 - logo.get_width() // 2, HEIGHT // 4 - logo.get_height()))

        self.btn = Button(self.screen,
                          WIDTH // 2 - BUTTON_SIZE[0] // 2, HEIGHT // 2, *BUTTON_SIZE,
                          radius=BUTTON_RADIUS,
                          image=load_image('play_btn.jpg'),
                          onClick=self.stop_screen
                          )

        self.screen_loop()


class EndScreen(Screen):
    def __init__(self, screen, clock):
        super().__init__(screen, clock, background_image='end_screen_photo.jpg')

        self.btn = Button(self.screen,
                          WIDTH // 2 - BUTTON_SIZE[0] // 2, HEIGHT // 2, *BUTTON_SIZE,
                          radius=BUTTON_RADIUS,
                          image=load_image('back_to_main_menu.jpg'),
                          onClick=self.stop_screen
                          )

        title = 'Победа!'
        text = ['Враг повержен! Победа за нами!']
        font_title = pygame.font.Font(None, TITLE_TEXT_FONT_SIZE)
        title_rendered = font_title.render(title, True, TEXT_COLOR)
        intro_rect = title_rendered.get_rect()
        intro_rect.centerx = TITLE_TEXT_X
        intro_rect.top = TITLE_TEXT_TOP
        self.screen.fill(TEXT_BG, intro_rect)
        self.screen.blit(title_rendered, intro_rect)

        # main text rendering
        font_text = pygame.font.Font(None, MAIN_TEXT_FONT_SIZE)
        text_coord = MAIN_TEXT_TOP
        for line in text:
            string_rendered = font_text.render(line, True, TEXT_COLOR)
            intro_rect = string_rendered.get_rect()
            intro_rect.centerx = MAIN_TEXT_X
            text_coord += 10
            intro_rect.top = text_coord
            text_coord += intro_rect.height
            self.screen.fill(TEXT_BG, intro_rect)
            self.screen.blit(string_rendered, intro_rect)

        self.screen_loop()


class MiddleScreen(Screen):
    def __init__(self, screen, clock, title, text, background_image):
        super().__init__(screen, clock, background_image=background_image)
        self.title = title
        self.text = text
        self.render_screen()

        self.btn = Button(self.screen,
                          WIDTH // 2 - BUTTON_SIZE[0] // 2, HEIGHT // 3 * 2, *BUTTON_SIZE,
                          radius=BUTTON_RADIUS,
                          image=load_image('accept.jpg'),
                          onClick=self.stop_screen
                          )
        self.screen_loop()

    def render_screen(self):
        # title rendering
        font_title = pygame.font.Font(None, TITLE_TEXT_FONT_SIZE)
        title_rendered = font_title.render(self.title, True, TEXT_COLOR)
        intro_rect = title_rendered.get_rect()
        intro_rect.centerx = TITLE_TEXT_X
        intro_rect.top = TITLE_TEXT_TOP
        self.screen.fill(TEXT_BG, intro_rect)
        self.screen.blit(title_rendered, intro_rect)

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
            self.screen.fill(TEXT_BG, intro_rect)
            self.screen.blit(string_rendered, intro_rect)


class WonScreen(Screen):
    def __init__(self, screen, clock):
        super().__init__(screen, clock, background_image='won_screen.jpg')

        self.btn = Button(self.screen,
                          WIDTH // 2 - BUTTON_SIZE[0] // 2, 3 * HEIGHT // 4, *BUTTON_SIZE,
                          radius=BUTTON_RADIUS,
                          image=load_image('go_forward.jpg'),
                          onClick=self.stop_screen
                          )

        self.render_screen()
        self.screen_loop()

    def render_screen(self):
        # title rendering
        font_title = pygame.font.Font(None, TITLE_TEXT_FONT_SIZE)
        title_rendered = font_title.render('ПОБЕДА!', True, TEXT_COLOR)
        intro_rect = title_rendered.get_rect()
        intro_rect.centerx = TITLE_TEXT_X
        intro_rect.top = TITLE_TEXT_TOP
        self.screen.fill(TEXT_BG, intro_rect)
        self.screen.blit(title_rendered, intro_rect)

        # main text rendering
        font_text = pygame.font.Font(None, MAIN_TEXT_FONT_SIZE)
        text_coord = MAIN_TEXT_TOP
        text = ['В этом сражении удалось одержать победу.', 'Вперёд, к следующим битвам!']
        for line in text:
            string_rendered = font_text.render(line, True, TEXT_COLOR)
            intro_rect = string_rendered.get_rect()
            intro_rect.centerx = MAIN_TEXT_X
            text_coord += 10
            intro_rect.top = text_coord
            text_coord += intro_rect.height
            self.screen.fill(TEXT_BG, intro_rect)
            self.screen.blit(string_rendered, intro_rect)


class LoseScreen(Screen):
    def __init__(self, screen, clock):
        super().__init__(screen, clock, background_image='lost_screen.jpg')

        self.btn = Button(self.screen,
                          WIDTH // 2 - BUTTON_SIZE[0] // 2, 3 * HEIGHT // 4, *BUTTON_SIZE,
                          radius=BUTTON_RADIUS,
                          image=load_image('back_to_main_menu.jpg'),
                          onClick=self.stop_screen
                          )

        self.render_screen()
        self.screen_loop()

    def render_screen(self):
        # title rendering
        font_title = pygame.font.Font(None, TITLE_TEXT_FONT_SIZE)
        title_rendered = font_title.render('Вы проиграли!', True, TEXT_COLOR)
        intro_rect = title_rendered.get_rect()
        intro_rect.centerx = TITLE_TEXT_X
        intro_rect.top = TITLE_TEXT_TOP
        self.screen.fill(TEXT_BG, intro_rect)
        self.screen.blit(title_rendered, intro_rect)

        # main text rendering
        font_text = pygame.font.Font(None, MAIN_TEXT_FONT_SIZE)
        text_coord = MAIN_TEXT_TOP
        text = ['Это сражение выиграть не удалось.', 'Вам придется начать Ваш боевой путь с самого начала...']
        for line in text:
            string_rendered = font_text.render(line, True, TEXT_COLOR)
            intro_rect = string_rendered.get_rect()
            intro_rect.centerx = MAIN_TEXT_X
            text_coord += 10
            intro_rect.top = text_coord
            text_coord += intro_rect.height
            self.screen.fill(TEXT_BG, intro_rect)
            self.screen.blit(string_rendered, intro_rect)
