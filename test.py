



import sys
import dill
import time
import pickle
import moderngl
import pygame

import math

from engine import io
from engine import utils
from engine import singleton

from engine.handler import signal
from engine.handler import world

from engine.ui import ui

from engine.graphics import gl
from engine.graphics import animation
from engine.graphics import spritesheet

# ---------------------------- #
# create a window

pygame.init()

clock = pygame.time.Clock()

singleton.WIN_BACKGROUND = utils.hex_to_rgb('001E3D')

gl.GLContext.add_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
gl.GLContext.add_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
gl.GLContext.add_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
gl.GLContext.add_attribute(pygame.GL_CONTEXT_FORWARD_COMPATIBLE_FLAG, True)
gl.GLContext.create_context()

singleton.DEBUG = True

# ---------------------------- #
# loading the world


_w = world.World()


_c = world.Chunk((0, 0))

_spritesheet = spritesheet.SpriteSheet("assets/sprites/player.json")

# temp load a chunk up with a tile
for i in range(8):
    for j in range(2):
        _c.set_tile_at((i, j), world.DefaultTile((i, j), "assets/test/screenshot.png"))

for i in range(8):
    _c.set_tile_at((i, 4), world.DefaultTile((i, j), _spritesheet.get_sprite_str_id(i)))


# ---------------------------- #

singleton.RUNNING = True
singleton.START_TIME = time.time()

while singleton.RUNNING:
    singleton.END_TIME = time.time()
    singleton.DELTA_TIME = singleton.END_TIME - singleton.START_TIME
    singleton.START_TIME = singleton.END_TIME

    # ---------------------------- #
    singleton.FRAMEBUFFER.fill(singleton.WIN_BACKGROUND)

    _c.update_and_render(singleton.FRAMEBUFFER, pygame.math.Vector2(0, 0))

    singleton.FRAMEBUFFER.blit(_spritesheet.image, (100, 100))
    
    # # render all sprites from the spritecache
    # for i, sprite in enumerate(_c._sprite_cacher._cached_sprites.values()):
    #     singleton.FRAMEBUFFER.blit(sprite, (20 * i, 50))
    
    # ---------------------------- #
    # render screen items
    gl.GLContext.render_to_opengl_window(singleton.FRAMEBUFFER, singleton.DEFAULT_SHADER, singleton.FRAMEBUFFER_SHADER_QUAD, {
        "tex": 0,
        "time": singleton.ACTIVE_TIME    
    })

    pygame.display.flip()

    # ---------------------------- #
    # update events
    singleton.system_update_function()    
    
    # update signals
    signal.update_signals()
    clock.tick(singleton.FPS)

    # update statistics
    singleton.FRAME_COUNTER += 1
    singleton.ACTIVE_TIME += singleton.DELTA_TIME

# ---------------------------- #