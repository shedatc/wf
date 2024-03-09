import pygame

from math              import floor
from pygame            import Rect
from pytmx.util_pygame import load_pygame as tmx_load

from .const  import COLOR_BLACK
from .assets import Assets
from .utils  import log_ex, sz

DEBUG_PROPERTIES = False # Log setting/getting properties

class Tilemap:
    SUPPORTED_TILE_PROPERTIES = [
        "level",
        "is_obstacle",
    ]

    @classmethod
    def log(cls, msg):
        log_ex(msg, category=cls.__name__)

    def __init__(self, name):
        # FIXME Find a way to use Assets.locate also for tilesets to allow
        #       sharing them between tilemaps.
        self._tmx = tmx_load( Assets.locate("tilemap", f"{name}.tmx") )
        Tilemap.log(f"Filename:         {self._tmx.filename}")
        Tilemap.log(f"Version:          {self._tmx.version}")
        Tilemap.log(f"Tiled Version:    {self._tmx.tiledversion}")
        Tilemap.log(f"Orientation:      {self._tmx.orientation}")

        self.map_size     = (self._tmx.width, self._tmx.height)
        self.tile_size    = (self._tmx.tilewidth, self._tmx.tileheight)
        (mw, mh)          = self.map_size
        (tw, th)          = self.tile_size
        self.surface_size = (mw*tw, mh*th)
        Tilemap.log(f"Map:              {sz(self.map_size)} tiles")
        Tilemap.log(f"Tile:             {sz(self.tile_size)} pixels")
        Tilemap.log(f"Surface:          {sz(self.surface_size)} pixels")

        # FIXME Check Tile Render Order. Only Right Down supported for now.
        #       Does it garantee the order of layers in the TMX file?
        Tilemap.log(f"Render Order:     {self._tmx.renderorder}")

        background_color = self._tmx.background_color
        if background_color is not None:
            self.background_surface = pygame.Surface(self.surface_size)
            self.background_surface.fill( pygame.Color(background_color) )
        else:
            self.background_surface = None
        Tilemap.log(f"Background Color: {background_color}")

        layer_index           = 0
        layers                = self._tmx.layers.copy()
        (tw, th)              = self.tile_size
        previous_layer_level  = 0
        self._tile_properties = {}
        self.surface          = pygame.Surface(self.surface_size)
        self.surface.set_colorkey(COLOR_BLACK)
        while len(layers) > 0:
            layer = layers.pop(0)
            Tilemap.log(f"Layer '{layer.name}':")
            Tilemap.log(f"    Properties: {layer.properties}")

            # Ensure levels are somewhat consistent even if the layer is not
            # rendered.
            if "level" in layer.properties:
                layer_level = layer.properties["level"]
                if layer_level == previous_layer_level:
                    pass
                elif layer_level == previous_layer_level + 1:
                    previous_layer_level = layer_level
                else:
                    Tilemap.log(  f"    WARNING: Unexpected layer level, "
                                + f"{previous_layer_level} → {layer_level}")

            # Will use layer opacity to set tile surfaces' alpha.
            layer_alpha = floor(layer.opacity * 255)
            Tilemap.log(f"    Visible: {layer.visible}")
            Tilemap.log(f"    Opacity: {layer.opacity} Alpha: {layer_alpha}")

            # If the layer is visible, blit the tiles onto the surface honoring
            # layer's opacity.
            #
            # Also combine properties as follow:
            # - tile properties override layer properties for a given layer
            # - properties (either tile or layer ones) from upper layers
            #   override the lower ones
            # - properties of a given layer are used even if the tile is
            #   missing from that layer
            tile_count = 0
            for u, v, tile_surface in layer.tiles():
                if layer.visible:
                    tile_surface.set_alpha(layer_alpha)
                    self.surface.blit(tile_surface, (u*tw, v*th))
                self.apply_tile_properties(u, v,
                        layer.properties)
                self.apply_tile_properties(u, v,
                        self._tmx.get_tile_properties(u, v, layer_index))
                tile_count += 1
            Tilemap.log(f"    {tile_count} tiles")
            layer_index += 1
        self.layer_count = layer_index

    def blit(self, surface, squares):
        (tw, th) = self.tile_size
        pixels   = Rect((squares.x     * tw, squares.y      * th),
                        (squares.width * tw, squares.height * th))
        if self.background_surface is not None:
            surface.blit(self.background_surface, (0, 0), pixels)
        surface.blit(self.surface, (0, 0), pixels)

    def set_tile_property(self, u, v, prop_key, prop_value):
        tile_key = f"{u}:{v}"
        if tile_key not in self._tile_properties:
            self._tile_properties[tile_key] = {}
        if DEBUG_PROPERTIES:
            if prop_key in self._tile_properties[tile_key]:
                old_prop_value = self._tile_properties[tile_key][prop_key]
            else:
                old_prop_value = None
        self._tile_properties[tile_key][prop_key] = prop_value
        if DEBUG_PROPERTIES:
            if old_prop_value is None:
                Tilemap.log(f"Property {prop_key} set to {prop_value} for tile [{u}, {v}]")
            else:
                Tilemap.log(f"Property {prop_key} changed from {old_prop_value} to {prop_value} for tile [{u}, {v}]")

    def apply_tile_properties(self, u, v, properties):
        if type(properties) is not dict:
            return
        for prop_key, prop_value in properties.items():
            if prop_key not in Tilemap.SUPPORTED_TILE_PROPERTIES:
                continue
            self.set_tile_property(u, v, prop_key, prop_value)

    def get_tile_properties(self, u, v):
        tile_key = f"{u}:{v}"
        if tile_key not in self._tile_properties:
            if DEBUG_PROPERTIES:
                Tilemap.log(f"Tile [{u}, {v}] have no property")
            return None
        return self._tile_properties[tile_key]

    def get_tile_property(self, u, v, prop_key):
        properties = self.get_tile_properties(u, v)
        if properties is None:
            return None
        elif prop_key not in properties:
            if DEBUG_PROPERTIES:
                Tilemap.log(f"Missing property {prop_key} for tile [{u}, {v}]")
            return None
        return properties[prop_key]

    def have_tile(self, u, v, layer_index=None):
        if layer_index is None:
            for layer_index in range(self.layer_count):
                gid = self._tmx.get_tile_gid(u, v, layer_index)
                if gid > 0:
                    return True
            return False
        else:
            return self._tmx.get_tile_gid(u, v, layer_index) > 0

    def is_obstacle(self, u, v):
        return not self.have_tile(u, v) \
            or self.get_tile_property(u, v, "is_obstacle") is True
