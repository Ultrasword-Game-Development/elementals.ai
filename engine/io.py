import os
import json
import pygame

from engine import utils
from engine import singleton

# ---------------------------- #
# caches

IMAGES_CACHE = {}
AUDIO_CACHE = {}
FONT_CACHE = {}

KEY_HELD = set()
KEY_CLICKED = set()
KEY_MOD_CLICKED = None


IMAGE_INDEX = 0
MASK_INDEX = 1


# ---------------------------- #
# images

def load_image(path: str, convert: bool = True):
    """ Load an image from a file """
    if path in IMAGES_CACHE:
        return IMAGES_CACHE[path][IMAGE_INDEX]

    image = pygame.image.load(path)
    image = image if not convert else image.convert_alpha()
    mask = pygame.mask.from_surface(image)
    IMAGES_CACHE[path] = (image, mask)
    return image

def load_mask(path: str):
    """ Load a mask from a file """
    load_image(path)
    return IMAGES_CACHE[path][MASK_INDEX]

def cache_image(path: str, image: pygame.Surface):
    """ Cache an image """
    if path in IMAGES_CACHE:
        raise ValueError(f"Image at path: {path} already cached.")
    # cache image + create mask
    IMAGES_CACHE[path] = (image, pygame.mask.from_surface(image))


# ---------------------------- #
# audio

def load_audio(path: str):
    """ Load an audio file """
    if path in AUDIO_CACHE:
        return AUDIO_CACHE[path]

    audio = pygame.mixer.Sound(path)
    AUDIO_CACHE[path] = audio
    return audio

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

def get_key_clicked(key: int):
    """ Check if a key is clicked """
    return key in KEY_CLICKED

def get_key_pressed(key: int):
    """ Check if a key is pressed """
    return pygame.key.get_pressed()[key]

def get_key_released(key: int):
    """ Check if a key is released """
    return not pygame.key.get_pressed()[key]

def get_key_held(key: int):
    """ Check if a key is held """
    return key in KEY_HELD

def check_mod_pressed(key: int):
    """ Check if a modifier key is pressed """
    return KEY_MOD_CLICKED & key

# ---------------------------- #
# mouse

get_mouse_pos = pygame.mouse.get_pos
get_mouse_pressed = pygame.mouse.get_pressed
get_mouse_clicked = pygame.mouse.get_just_pressed

MOUSE_REL = (0, 0)
MOUSE_REL_SCROLL = (0, 0)

def update_mouse_rel():
    """ Update the mouse relative position """
    global MOUSE_REL
    MOUSE_REL = pygame.mouse.get_rel()

def get_scroll_rel():
    """ Get the relative scroll """
    return MOUSE_REL_SCROLL

def get_mouse_rel():
    """ Get the mouse relative position """
    return MOUSE_REL    

def is_left_clicked():
    """ Check if the left mouse button is clicked """
    return get_mouse_clicked()[0]

def is_right_clicked():
    """ Check if the right mouse button is clicked """
    return get_mouse_clicked()[2]

def is_middle_clicked():
    """ Check if the middle mouse button is clicked """
    return get_mouse_clicked()[1]

def is_left_pressed():
    """ Check if the left mouse button is pressed """
    return get_mouse_pressed()[0]

def is_right_pressed():
    """ Check if the right mouse button is pressed """
    return get_mouse_pressed()[2]

def is_middle_pressed():
    """ Check if the middle mouse button is pressed """
    return get_mouse_pressed()[1]

def is_scroll_clicked():
    """ Check if the scroll wheel is clicked """
    return get_mouse_pressed()[1]

def get_abs_mouse_pos():
    """ Get the mouse position """
    return pygame.mouse.get_pos()

def get_framebuffer_mouse_pos():
    """ Get the mouse position """
    return utils.mouse_surface_to_framebuffer_pos_int(pygame.mouse.get_pos(), singleton.FB_SIZE, singleton.WIN_SIZE)

