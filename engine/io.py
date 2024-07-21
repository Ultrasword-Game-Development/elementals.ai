import pygame
import json
import os


# ---------------------------- #
# caches

IMAGES_CACHE = {}
AUDIO_CACHE = {}
FONT_CACHE = {}


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

