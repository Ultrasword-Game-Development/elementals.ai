import pygame


RUNNING = False

# ---------------------------- #

WIN_SIZE = [1280, 720]
WIN_FLAGS = pygame.DOUBLEBUF | pygame.RESIZABLE
WIN_DEPTH = 16
WIN_BACKGROUND = (255, 255, 255, 255)

FB_FACTOR = 4
FB_SIZE = [WIN_SIZE[0] // FB_FACTOR, WIN_SIZE[1] // FB_FACTOR]

WINDOW = None
FRAMEBUFFER = None


# ---------------------------- #

DELTA_TIME = 0
START_TIME = 0
END_TIME = 0

# ---------------------------- #

ANIMATION_FRAMERATE = 8
ANIMATION_DELTA = 1 / ANIMATION_FRAMERATE

