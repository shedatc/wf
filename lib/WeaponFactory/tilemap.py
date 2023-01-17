import pygame

from pygame            import Rect
from pytmx.util_pygame import load_pygame as tmx_load
from xml.etree         import ElementTree

from .const     import COLOR_BLACK, TILE_WIDTH, TILE_HEIGHT
from .resources import Resources
from .utils     import log_ex, sz

class Tilemap:

    @classmethod
    def log(cls, msg):
        log_ex(msg, category=cls.__name__)

    def __init__(self, name):
        path     = Resources.locate("tilemap", f"{name}.tmx")
        self.tmx = tmx_load(path)
        Tilemap.log(f"name={name} path={path}")

        self.map_size     = (self.tmx.width, self.tmx.height)
        self.tile_size    = (self.tmx.tilewidth, self.tmx.tileheight)
        (mw, mh)          = self.map_size
        (tw, th)          = self.tile_size
        self.surface_size = (mw*tw, mh*th)
        assert tw == TILE_WIDTH,  "Invalid tile width; must be {TILE_WIDTH} pixels"
        assert th == TILE_HEIGHT, "Invalid tile height; must be {TILE_HEIGHT} pixels"
        self._build_level_surfaces()
        Tilemap.log(f"sizes: map={sz(self.map_size)} tile={sz(self.tile_size)}"
                    + f" surface={sz(self.surface_size)}")

        if __debug__:
            (screen_width, screen_height) = pygame.display.get_window_size()
            Tilemap.log(f"screen={sz(pygame.display.get_window_size())}")
            assert screen_width  // tw <= mw, "Invalid tilemap width"
            assert screen_height // th <= mh, "Invalid tilemap height"

    def _build_level_surfaces(self):
        self.level_count     = 0
        self._level_surfaces = []
        layers               = self.tmx.layers
        (tw, th)             = self.tile_size
        for level in range(5):
            layer_names = []
            surface     = pygame.Surface(self.surface_size)
            surface.set_colorkey(COLOR_BLACK)
            while len(layers) > 0:
                layer      = layers[0]
                layers     = layers[1:]
                tile_count = 0
                for u, v, tile_surface in layer.tiles():
                    surface.blit(tile_surface, (u*tw, v*th))
                    tile_count += 1
                layer_names.append(layer.name)
                Tilemap.log(f"layer_name='{layer.name}' tile_count={tile_count}")
                if layer.name == f"Level {level}":
                    break
            self._level_surfaces.append(surface)
            Tilemap.log(f"level={level} layers={layer_names}")
            self.level_count += 1
            if len(layers) == 0:
                break
        Tilemap.log(f"level_count={self.level_count}")

    def is_obstacle(self, u, v, layer_index):
        props = self.tmx.get_tile_properties(u, v, layer_index)
        return type(props) is dict and props["is_obstacle"]

    def blit_level(self, squares, level, surface):
        (tw, th) = self.tile_size
        pixels   = Rect((squares.x     * tw, squares.y      * th),
                        (squares.width * tw, squares.height * th))
        surface.blit(self._level_surfaces[level], (0, 0), pixels)

    def lookup_layer(self, square):
        layers = self.tmx.layers.copy()
        while len(layers) > 0:
            layer = layers.pop(-1)
            for u, v, _ in layer.tiles():
                if square.u == u and square.v == v:
                    return layer
        raise RuntimeError(f"No layer for tile at {square}")

    # Look for the given property. First at tile-level and, if missing, at
    # layer-level.
    def lookup_tile_property(self, square, prop_name):
        layer = self.lookup_layer(square)
        ps    = []
        if layer.data is not None:
            gid = layer.data[square.v][square.u]
            ps.append(self.tmx.tile_properties[gid])
        ps.append(layer.properties)
        for p in ps:
            if p is not None and prop_name in p:
                prop_value = p[prop_name]
                Tilemap.log(f"Property {prop_name} for tile {square} is {prop_value}")
                return prop_value
        Tilemap.log(f"Missing property {prop_name} for tile {square}")
        return None
