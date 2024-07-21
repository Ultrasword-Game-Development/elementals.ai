import pygame


RUNNING = False

FPS = 60
FRAME_COUNTER = 0

# ---------------------------- #

WIN_SIZE = [1280, 720]
WIN_FLAGS = pygame.DOUBLEBUF | pygame.RESIZABLE | pygame.OPENGL
WIN_DEPTH = 16
WIN_BACKGROUND = (255, 255, 255, 255)

FB_FACTOR = 4
FB_SIZE = [WIN_SIZE[0] // FB_FACTOR, WIN_SIZE[1] // FB_FACTOR]

WINDOW = None
FRAMEBUFFER = None

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

# ---------------------------- #

DELTA_TIME = 0
START_TIME = 0
END_TIME = 0

# ---------------------------- #

ANIMATION_FRAMERATE = 8
ANIMATION_DELTA = 1 / ANIMATION_FRAMERATE



