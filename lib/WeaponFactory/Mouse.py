import pygame.display
import pygame.mouse

class Mouse:

    @classmethod
    def screen_xy(cls):
        return pygame.mouse.get_pos()

    @classmethod
    def move(cls, x, y):
        pygame.mouse.set_pos([x, y])

    @classmethod
    def center(cls):
        (screen_width, screen_height) = pygame.display.get_surface().get_size()
        pygame.mouse.set_pos([screen_width  // 2,
                              screen_height // 2])
