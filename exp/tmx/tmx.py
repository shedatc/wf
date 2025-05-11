from math              import floor
from pytmx.util_pygame import load_pygame as tmx_load

import pygame
import sys

PROPERTIES = ["layer", "is_obstacle"]

tile_props = {}
def set_tile_property(u, v, prop_key, prop_value):
    global tile_props
    tile_key = f"{u}:{v}"
    if tile_key not in tile_props:
        tile_props[tile_key] = {}
    if prop_key in tile_props[tile_key]:
        old_prop_value = tile_props[tile_key][prop_key]
    else:
        old_prop_value = None
    tile_props[tile_key][prop_key] = prop_value
    if old_prop_value is None:
        print(f"                [{tile_key}][{prop_key}]: {prop_value}")
    else:
        print(f"                [{tile_key}][{prop_key}]: {old_prop_value} -> {prop_value}")

def apply_tile_properties(u, v, properties):
    if type(properties) is not dict:
        return
    for pk, pv in properties.items():
        if pk not in PROPERTIES:
            continue
        set_tile_property(u, v, pk, pv)

def main(argv=[]):
    path = argv[1]

    screen_size = (800, 600)
    print(f"Screen Size:      {screen_size[0]}x{screen_size[1]} pixels")
    pygame.init()
    pygame.display.set_mode(screen_size, 0)

    tmx = tmx_load(path)
    print(f"Filename:         {tmx.filename}")
    print(f"Version:          {tmx.version}")
    print(f"Tiled Version:    {tmx.tiledversion}")
    print(f"Orientation:      {tmx.orientation}")
    print(f"Render Order:     {tmx.renderorder}")
    print(f"Map:              {tmx.width}x{tmx.height} tiles")
    print(f"Tile:             {tmx.tilewidth}x{tmx.tileheight} pixels")
    print(f"Background Color: {tmx.background_color}")
    if len(tmx.properties) > 0:
        print(f"Map Properties:")
        for name, value in tmx.properties.items():
            print(f"    {name}: {value}")
    if False:
        print(f"tmx: {tmx.__dict__.keys()}")
    layer_count = len(tmx.layers)
    print(f"Layer Count:      {layer_count}")
    print(f"Layers:")
    layer_index = 0
    for layer in tmx.layers:
        if False:
            print(f"layer: {layer.__dict__.keys()}")
        print(f"    {layer.name}:")
        print(f"        Index:   {layer_index}")
        print(f"        Visible: {layer.visible}")
        layer_alpha = floor(layer.opacity * 255) # Just map value from 0.0..1.0 to 0..255.
        print(f"        Opacity: {layer.opacity} Alpha: {layer_alpha}")
        if len(layer.properties) > 0:
            print(f"        Layer Properties:")
            for lpk, lpv in layer.properties.items():
                print(f"            {lpk}: {lpv}")
        print(f"        Tiles:")
        tile_count = 0
        for u, v, _ in layer.tiles():
            tile_gid        = tmx.get_tile_gid(u, v, layer_index)
            tile_properties = tmx.get_tile_properties(u, v, layer_index)
            if tile_properties is not None:
                print(f"            [{u}, {v}]")
                print(f"                GID: {tile_gid}")
                print(f"                Tile Properties:")
                for tpk, tpv in tile_properties.items():
                    print(f"                    {tpk}: {tpv}")
            tile_count += 1
            apply_tile_properties(u, v, layer.properties)
            apply_tile_properties(u, v, tmx.get_tile_properties(u, v, layer_index))
        print(f"        Tile Count: {tile_count}")
        layer_index += 1


    while layer_index >= 1:
        layer_index -= 1
        tile_gid = tmx.get_tile_gid(0, 0, layer_index)
        if tile_gid is not None:
            print(f"[0, 0]@{layer_index} GID: {tile_gid}")

if __name__ == "__main__":
    sys.exit( main( sys.argv ))
