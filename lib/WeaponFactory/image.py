import pygame.image

def image_load(path):
    surface = pygame.image.load(path)
    surface.convert()
    surface.convert_alpha()
    return surface
