import pygame

from ..constants import Constants


class Game:
    def __init__(self, config):
        pygame.init()
        pygame.mixer.init()

        self.fps = config.SETTINGS["fps"]
        self.display = pygame.display
        self.window = self.display.set_mode(config.SETTINGS["resolution"])
        self.__setup_window(config)

        self.__clock = pygame.time.Clock()
        self.running = False

        self.view = config.STARTING_VIEW()

    @property
    def view(self):
        return self.__view

    @view.setter
    def view(self, value):
        self.__view = value

        self.window.fill(Constants.COLOURS["black"])

        self.window.blit(*self.__view.render())
        self.display.flip()

    def start(self):
        self.running = True
        while self.running:
            elapsed = self.__clock.tick(self.fps)

            events = tuple(pygame.event.get())
            updated_rectangles = self.view.update(elapsed, events)
            if updated_rectangles:
                self.window.blit(*self.view.render())
                self.display.update(updated_rectangles)

    def __setup_window(self, config):
        if "title" in config.SETTINGS:
            self.display.set_caption(config.SETTINGS["title"])

