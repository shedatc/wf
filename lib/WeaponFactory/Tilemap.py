import pygame

from math              import floor
from pygame            import Rect
from pytmx             import TiledObjectGroup, TiledTileLayer
from pytmx.util_pygame import load_pygame as tmx_load

from .Assets import Assets
from .Screen import Screen
from .const  import COLOR_BLACK, DEBUG_BLIT
from .utils  import log_ex

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
        tmx       = tmx_load( Assets.locate("tilemap", f"{name}.tmx") )
        self._tmx = tmx
        Tilemap.log(f"Filename:         {tmx.filename}")
        Tilemap.log(f"Version:          {tmx.version}")
        Tilemap.log(f"Tiled Version:    {tmx.tiledversion}")
        Tilemap.log(f"Orientation:      {tmx.orientation}")

        self.rect                 = Rect((0, 0), (tmx.width, tmx.height))             # tiles
        self.tile_rect            = Rect((0, 0), (tmx.tilewidth, tmx.tileheight))     # pixels
        self.surface_rect         = self.rect.scale_by(tmx.tilewidth, tmx.tileheight) # pixels
        self.surface_rect.topleft = (0, 0)

        Tilemap.log(f"Map:              {self.rect} tiles")
        Tilemap.log(f"Tile:             {self.tile_rect} pixels")
        Tilemap.log(f"Surface:          {self.surface_rect} pixels")

        # FIXME Check Tile Render Order. Only Right Down supported for now.
        #       Does it garantee the order of layers in the TMX file?
        Tilemap.log(f"Render Order:     {tmx.renderorder}")

        background_color = tmx.background_color
        if background_color is not None:
            self.background_surface = pygame.Surface(self.surface_rect.size)
            self.background_surface.fill( pygame.Color(background_color) )
        else:
            self.background_surface = None
        Tilemap.log(f"Background Color: {background_color}")

        self.surface          = pygame.Surface(self.surface_rect.size)
        self.surface.set_colorkey(COLOR_BLACK)

        current_level         = 0
        layers                = tmx.layers.copy()
        self._tile_properties = {}
        self.locations        = {}
        tile_layer_index      = 0
        while len(layers) > 0:
            layer = layers.pop(0)
            if type(layer) is TiledTileLayer:
                current_level = self._handle_tile_layer(layer, current_level, tile_layer_index)
                tile_layer_index += 1
            elif type(layer) is TiledObjectGroup:
                self._handle_object_group(layer)
            else:
                Tilemap.log(f"Unknown Layer Type: {layer}")
        self.tile_layer_count = tile_layer_index

    def _handle_object_group(self, object_group):
        assert type(object_group) is TiledObjectGroup

        Tilemap.log(f"Object Group '{object_group.name}':")
        Tilemap.log(f"    Properties: {object_group.properties}")
        Tilemap.log(f"    Objects:")

        object_count   = 0
        location_count = 0
        for object in object_group:
            Tilemap.log(f"        Object '{object.name}':")
            Tilemap.log(f"            Type:       '{object.type}'")
            Tilemap.log(f"            Properties: {object.properties}")
            Tilemap.log(f"            Position:   ({object.x}, {object.y})")
            Tilemap.log(f"            Size:       {object.width}x{object.height} pixels")
            Tilemap.log(f"            Visible:    {object.visible == 1}")
            object_count += 1

            if object.type not in self.locations:
                self.locations[object.type] = {}
            self.locations[object.type][object.name] = (object.x, object.y)
            location_count += 1
        Tilemap.log(f"    {location_count} locations")
        Tilemap.log(f"    {object_count} objects")

    def _handle_tile_layer(self, tile_layer, current_level, tile_layer_index):
        assert type(tile_layer) is TiledTileLayer

        Tilemap.log(f"Tile Layer '{tile_layer.name}':")
        Tilemap.log(f"    Properties: {tile_layer.properties}")

        # Ensure levels are somewhat consistent even if the layer is not
        # rendered.
        if "level" in tile_layer.properties:
            layer_level = tile_layer.properties["level"]
            if layer_level == current_level:
                pass
            elif layer_level == current_level + 1:
                current_level = layer_level
            else:
                Tilemap.log(  f"    WARNING: Unexpected layer level, "
                              + f"{current_level} → {layer_level}")

        # Will use layer opacity to set tile surfaces' alpha.
        layer_alpha = floor(tile_layer.opacity * 255)
        Tilemap.log(f"    Visible: {tile_layer.visible}")
        Tilemap.log(f"    Opacity: {tile_layer.opacity} Alpha: {layer_alpha}")

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
        for x, y, tile_surface in tile_layer.tiles():
            tile_dest = Rect((x * self._tmx.tilewidth, y * self._tmx.tileheight),
                             tile_surface.get_size())
            if tile_layer.visible:
                tile_surface.set_alpha(layer_alpha)
                self.surface.blit(tile_surface, tile_dest)
                if DEBUG_BLIT:
                    Tilemap.log(f"Blit tile ({x}, {y}) to {self.surface}@{tile_dest}")
            self.apply_tile_properties(x, y, tile_layer.properties)
            self.apply_tile_properties(x, y, self._tmx.get_tile_properties(x, y, tile_layer_index))
            tile_count += 1
        Tilemap.log(f"    {tile_count} tiles")
        return current_level

    def blit(self, source_rect):
        screen = Screen.singleton()
        if self.background_surface is not None:
            screen.screen_blit(self.background_surface, (0, 0), source_rect=source_rect)
        screen.screen_blit(self.surface, (0, 0), source_rect=source_rect)

    def set_tile_property(self, x, y, prop_key, prop_value):
        tile_key = f"{x}:{y}"
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
                Tilemap.log(f"Property {prop_key} set to {prop_value} for tile ({x}, {y})")
            else:
                Tilemap.log(f"Property {prop_key} changed from {old_prop_value} to {prop_value} for tile ({x}, {y})")

    def apply_tile_properties(self, x, y, properties):
        if type(properties) is not dict:
            return
        for prop_key, prop_value in properties.items():
            if prop_key not in Tilemap.SUPPORTED_TILE_PROPERTIES:
                continue
            self.set_tile_property(x, y, prop_key, prop_value)

    def get_tile_properties(self, x, y):
        tile_key = f"{x}:{y}"
        if tile_key not in self._tile_properties:
            if DEBUG_PROPERTIES:
                Tilemap.log(f"Tile ({x}, {y}) have no property")
            return None
        return self._tile_properties[tile_key]

    def get_tile_property(self, x, y, prop_key):
        properties = self.get_tile_properties(x, y)
        if properties is None:
            return None
        elif prop_key not in properties:
            if DEBUG_PROPERTIES:
                Tilemap.log(f"Missing property {prop_key} for tile ({x}, {y})")
            return None
        return properties[prop_key]

    def have_tile(self, x, y, layer_index=None):
        if layer_index is None:
            for layer_index in range(self.tile_layer_count):
                gid = self._tmx.get_tile_gid(x, y, layer_index)
                if gid > 0:
                    return True
            return False
        else:
            return self._tmx.get_tile_gid(x, y, layer_index) > 0

    def is_obstacle(self, x, y):
        return not self.have_tile(x, y) \
            or self.get_tile_property(x, y, "is_obstacle") is True
