import pygame
import sys
import os

from engine import io

# ---------------------------- #
# pre-run scripts



# ---------------------------- #

RUNNING = False
DEBUG = False

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

# ---------------------------- #
# animation

ANIMATION_FRAMERATE = 8
ANIMATION_DELTA = 1 / ANIMATION_FRAMERATE

# ---------------------------- #
# world

DEFAULT_CHUNK_WIDTH = 8
DEFAULT_CHUNK_HEIGHT = 8

DEFAULT_TILE_WIDTH = 16
DEFAULT_TILE_HEIGHT = 16

DEFAULT_LAYER_COUNT = 8

# ---------------------------- #
# util functions

def system_update_function():
    """ Update the system """
    global RUNNING, DEBUG
    io.KEY_CLICKED.clear()
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            RUNNING = False
            CONTEXT.release()
            pygame.quit()
            sys.exit()
        elif e.type == pygame.KEYDOWN:
            io.KEY_CLICKED.add(e.key)
            io.KEY_HELD.add(e.key)
        elif e.type == pygame.KEYUP:
            io.KEY_HELD.remove(e.key)
        elif e.type == pygame.MOUSEBUTTONDOWN:
            if e.button > 3:
                continue
            io.MOUSE_PRESSED[e.button] = True
        elif e.type == pygame.MOUSEBUTTONUP:
            if e.button > 3:
                continue
            io.MOUSE_PRESSED[e.button] = False
    
    # TODO - REMOVE THIS -- check if debug toggle
    if io.get_key_clicked(pygame.K_d) and io.get_key_pressed(pygame.K_LSHIFT):
        DEBUG = not DEBUG
