import pygame
import sys
import os
import platform

import dill

from engine import io
from engine.graphics import gl

# ---------------------------- #
# pre-run scripts


# default settings = Windows
CONTROL_KEY_EQUIV = pygame.K_LCTRL

# operating system specific info
if platform.system() == "Windows":
    pass
elif platform.system() == "Linux":
    pass
elif platform.system() == "Darwin":
    CONTROL_KEY_EQUIV = pygame.K_LMETA
elif platform.system() == "Java":
    print("why are you playing on java wth. Get outta here lol.")
    sys.exit()


# ---------------------------- #

RUNNING = False
DEBUG = False
EDITOR_DEBUG = False

FPS = 60
FRAME_COUNTER = 0
ACTIVE_TIME = 0

# ---------------------------- #

WIN_SIZE = [1280, 720]
WIN_FLAGS = pygame.DOUBLEBUF | pygame.RESIZABLE | pygame.OPENGL
WIN_DEPTH = 16
WIN_BACKGROUND = (255, 255, 255, 255)

FB_FACTOR = 4
FB_SIZE = [WIN_SIZE[0] // FB_FACTOR, WIN_SIZE[1] // FB_FACTOR]

WINDOW = None
FRAMEBUFFER = None
SCREENBUFFER = None
DEFAULT_SURFACE_FLAGS = pygame.SRCALPHA

# ---------------------------- #

DEFAULT_ATTRIBUTES = [
    (pygame.GL_CONTEXT_MAJOR_VERSION, 3),
    (pygame.GL_CONTEXT_MINOR_VERSION, 3),
    (pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE),
    (pygame.GL_CONTEXT_FORWARD_COMPATIBLE_FLAG, True),
]

ATTRIBUTES = []
CONTEXT = None
FULL_QUAD_BUFFER = None

FRAMEBUFFER_SHADER_QUAD = "fb_shader_quad"
SCREEN_SHADER_QUAD = "screen_shader_quad"

DEFAULT_SHADER = "assets/shaders/default.glsl"
DEFAULT_SCREEN_SHADER = "assets/shaders/defaultscreen.glsl"

# ---------------------------- #
# time

DELTA_TIME = 0
START_TIME = 0
END_TIME = 0

GLOBAL_FRAME_SIGNAL_EMITTER = None
GLOBAL_FRAME_SIGNAL_KEY = "global_frame_signal"

# ---------------------------- #
# animation

ANIMATION_FRAMERATE = 8
ANIMATION_DELTA = 1 / ANIMATION_FRAMERATE

# ---------------------------- #
# world

DEFAULT_CHUNK_WIDTH = 8
DEFAULT_CHUNK_HEIGHT = 8
DEFAULT_CHUNK_AREA_VEC2 = pygame.math.Vector2(DEFAULT_CHUNK_WIDTH, DEFAULT_CHUNK_HEIGHT)

DEFAULT_TILE_WIDTH = 16
DEFAULT_TILE_HEIGHT = 16

DEFAULT_CHUNK_PIXEL_WIDTH = DEFAULT_CHUNK_WIDTH * DEFAULT_TILE_WIDTH
DEFAULT_CHUNK_PIXEL_HEIGHT = DEFAULT_CHUNK_HEIGHT * DEFAULT_TILE_HEIGHT

DEFAULT_LAYER_COUNT = 3
DEFAULT_CHUNK_RENDER_DISTANCE = 2

UPDATE_INVISIBLE_CHUNKS = True

SAVING_WORLD_FLAG = False

# ---------------------------- #
# misc functions

def GAME_EXIT_FUNCTION():
    """ Function to call when the game exits """
    print("Note: Exiting Game")

# ---------------------------- #
# util functions

def update_default_chunk_tile_config(width: int, height: int, tile_width: int, tile_height: int):
    """ Update the default chunk config """
    global DEFAULT_CHUNK_WIDTH, DEFAULT_CHUNK_HEIGHT, DEFAULT_CHUNK_AREA_VEC2, DEFAULT_CHUNK_PIXEL_WIDTH, DEFAULT_CHUNK_PIXEL_HEIGHT, DEFAULT_TILE_WIDTH, DEFAULT_TILE_HEIGHT
    DEFAULT_TILE_WIDTH = tile_width
    DEFAULT_TILE_HEIGHT = tile_height
    DEFAULT_CHUNK_WIDTH = width
    DEFAULT_CHUNK_HEIGHT = height
    DEFAULT_CHUNK_AREA_VEC2 = pygame.math.Vector2(DEFAULT_CHUNK_WIDTH, DEFAULT_CHUNK_HEIGHT)
    DEFAULT_CHUNK_PIXEL_WIDTH = DEFAULT_CHUNK_WIDTH * DEFAULT_TILE_WIDTH
    DEFAULT_CHUNK_PIXEL_HEIGHT = DEFAULT_CHUNK_HEIGHT * DEFAULT_TILE_HEIGHT

def system_update_function():
    """ Update the system """
    global RUNNING, DEBUG, EDITOR_DEBUG
    io.KEY_CLICKED.clear()
    io.KEY_MOD_CLICKED = pygame.key.get_mods()
    io.update_mouse_rel()
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            RUNNING = False
            GAME_EXIT_FUNCTION()
            CONTEXT.release()
            pygame.quit()
            sys.exit()
        elif e.type == pygame.KEYDOWN:
            io.KEY_CLICKED.add(e.key)
            io.KEY_HELD.add(e.key)
        elif e.type == pygame.KEYUP:
            io.KEY_HELD.remove(e.key)
        # TODO - handle mouse scrolling
        elif e.type == pygame.MOUSEBUTTONDOWN:
            if e.button > 3:
                continue
            # io.MOUSE_PRESSED[e.button] = True
        elif e.type == pygame.MOUSEBUTTONUP:
            if e.button > 3:
                continue
            # io.MOUSE_PRESSED[e.button] = False
        elif e.type == pygame.WINDOWSIZECHANGED:
            gl.GLContext.handle_resizing((e.x, e.y))
    
    # TODO - decide if i want to keep this (update per frame) signal emitter
    GLOBAL_FRAME_SIGNAL_EMITTER.emit()
    
    # TODO - REMOVE THIS -- check if debug toggle
    if io.get_key_clicked(pygame.K_d) and io.get_key_pressed(pygame.K_LSHIFT):
        DEBUG = not DEBUG
    if io.get_key_clicked(pygame.K_e) and io.get_key_pressed(pygame.K_LSHIFT):
        EDITOR_DEBUG = not EDITOR_DEBUG

def save_world(path: str, world):
    """ Save the world to a file """
    global SAVING_WORLD_FLAG
    SAVING_WORLD_FLAG = True
    with open(path, "wb") as f:
        dill.dump(world, f)
    SAVING_WORLD_FLAG = False

def load_world(path: str):
    """ Load a world from a file """
    with open(path, "rb") as f:
        return dill.load(f)
