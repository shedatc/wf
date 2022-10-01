import pygame

from pytmx.util_pygame import load_pygame as tmx_load

from .resources import Resources
from .utils     import log_ex

class Tilemap:

    def log(msg):
        log_ex(msg, category="Tilemap")

    def __init__(self, name):
        path           = Resources.locate("tilemap", f"{name}.tmx")
        self.tmx       = tmx_load(path)
        (w,  h)        = self.get_map_size()
        self.tile_size = (self.tmx.tilewidth, self.tmx.tileheight)
        (tw, th)       = self.tile_size
        Tilemap.log(f"name={name} path={path} map_size={w}x{h} tile_size={tw}x{th}")

        if __debug__:
            (screen_width, screen_height) = pygame.display.get_window_size()
            Tilemap.log(f"screen={screen_width}x{screen_height}")
            if w < screen_width  / tw:
                raise AssertionError("Invalid tilemap width")
            if h < screen_height / th:
                raise AssertionError("Invalid tilemap height")

    def is_obstacle(self, u, v, layer_index):
        props = self.tmx.get_tile_properties(u, v, layer_index)
        return type(props) is dict and props["is_obstacle"]

    def get_layer(self, layer_index):
        return self.tmx.layers[layer_index]

    def get_layer_size(self, layer_index):
        layer = self.get_layer(layer_index)
        return (layer.width, layer.height)

    def get_map_size(self):
        return self.get_layer_size(0)

    def blit_layer(self, rect, layer_index, surface):
        (tw, th) = self.tile_size
        for v in range(rect.y, rect.y + rect.h):
            for u in range(rect.x, rect.x + rect.w):
                tile = self.tmx.get_tile_image(u, v, layer_index)
                if tile is None:
                    continue
                tile_xy = ((u - rect.x) * tw, (v - rect.y) * th)
                surface.blit(tile, tile_xy)
