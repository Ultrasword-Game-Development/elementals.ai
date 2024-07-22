import pygame
import json
import os

# ---------------------------- #
# caches

IMAGES_CACHE = {}
AUDIO_CACHE = {}
FONT_CACHE = {}

KEY_HELD = set()

MOUSE_PRESSED = [0, 0, 0, 0]

# ---------------------------- #
# images

def load_image(path: str, convert: bool = True):
    """ Load an image from a file """
    if path in IMAGES_CACHE:
        return IMAGES_CACHE[path]

    image = pygame.image.load(path)
    image = image if not convert else image.convert_alpha()
    IMAGES_CACHE[path] = image
    return image


# ---------------------------- #
# audio


# ---------------------------- #
# fonts

def load_font(path: str, size: int):
    """ Load a font from a file """
    if not size in FONT_CACHE:
        FONT_CACHE[size] = {}
    if path in FONT_CACHE[size]:
        return FONT_CACHE[size][path]

    font = pygame.font.Font(path, size)
    FONT_CACHE[size][path] = font
    return font


# ---------------------------- #
# utils

def json_to_dict(path: str):
    """ Load a json file and return it as a dict """
    with open(path, 'r') as f:
        return json.load(f)


# ---------------------------- #
# keyboard

def get_key_pressed(key: int):
    """ Check if a key is pressed """
    return pygame.key.get_pressed()[key]

def get_key_released(key: int):
    """ Check if a key is released """
    return not pygame.key.get_pressed()[key]

def get_key_held(key: int):
    """ Check if a key is held """
    return key in KEY_HELD

# ---------------------------- #
# mouse

get_mouse_pos = pygame.mouse.get_pos
get_mouse_pressed = pygame.mouse.get_pressed
get_mouse_rel = pygame.mouse.get_rel

def is_left_clicked():
    """ Check if the left mouse button is clicked """
    return get_mouse_pressed()[0]

def is_right_clicked():
    """ Check if the right mouse button is clicked """
    return get_mouse_pressed()[2]

def is_scroll_clicked():
    """ Check if the scroll wheel is clicked """
    return get_mouse_pressed()[1]
