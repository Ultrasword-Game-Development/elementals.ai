import os
import sys
import platform

# TODO - figure out what to do when I compile this program (because that'll be quite a problem)
if not os.environ.get("PYTHONHASHSEED"):
    os.environ["PYTHONHASHSEED"] = "13"
    
    import subprocess
    subprocess.run([sys.executable] + sys.argv)
    sys.exit()
    # os.execv(sys.executable, ['python'] + sys.argv)

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

from engine.physics import phandler

from engine.ui import ui

from engine.graphics import gl
from engine.graphics import animation
from engine.graphics import spritesheet

from engine.addon import tiles

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
singleton.set_framebuffer_size_factor(4)
singleton.update_default_chunk_tile_config(8, 8, 16, 16)

# TODO - put into editor lol

# ---------------------------- #
# loading the world

_world_path = "test_world"

# _w = world.World.load_world(_world_path)

_w = world.World(_world_path)
_w.get_layer_at(0).set_chunk_at(world.Chunk(
    (_w.get_camera_chunk())
))

_c = _w.get_layer_at(0).get_chunk_at(_w.get_camera_chunk())

_spritesheet = spritesheet.load_spritesheet("assets/sprites/entities/player.json")

# temp load a chunk up with a tile
for i in range(singleton.DEFAULT_CHUNK_WIDTH):
    for j in range(2):
        _c.set_tile_at((i, j), world.DefaultTile((i, j), "assets/test/screenshot.png"))

for i in range(singleton.DEFAULT_CHUNK_WIDTH):
    _c.set_tile_at((i, 3), world.DefaultTile((i, j), _spritesheet.get_sprite_str_id(i)))

# add an animated sprite at location - (0, 0)
_c.set_tile_at((0, 0), tiles.SemiAnimatedTile((0, 0), "assets/sprites/entities/player.json"))
_c.set_tile_at((0, 2), tiles.SemiAnimatedTile((0, 0), "assets/sprites/entities/player.json"))
_c.set_tile_at((0, 3), tiles.AnimatedTile((0, 0), "assets/sprites/entities/player.json", offset=2))

_spritesheet = spritesheet.load_spritesheet("assets/sprites/entities/wizard.json")
for i in range(singleton.DEFAULT_CHUNK_WIDTH):
    _c.set_tile_at((i, 4), tiles.AnimatedTile((i, 4), "assets/sprites/entities/wizard.json", offset=0))

singleton.save_world(_w)



# take player sprite 1 + player sprite 2
_spritesheet = spritesheet.load_spritesheet("assets/sprites/entities/player.json")
_left = _spritesheet[0]
_left_rect = _left.get_rect()
_left_rect.topleft = (100, 100)
_left_mask = pygame.mask.from_surface(_spritesheet[0])
_left_mask_surface = _left_mask.to_surface()

_right = _spritesheet[1]
_right_rect = _right.get_rect()
_right_rect.topleft = (120, 100)
_right_mask = pygame.mask.from_surface(_spritesheet[1])
_right_mask_surface = _right_mask.to_surface()


# ---------------------------- #

singleton.RUNNING = True
singleton.START_TIME = time.time()

while singleton.RUNNING:
    singleton.END_TIME = time.time()
    singleton.DELTA_TIME = singleton.END_TIME - singleton.START_TIME
    singleton.START_TIME = singleton.END_TIME

    # ---------------------------- #
    singleton.FRAMEBUFFER.fill(singleton.WIN_BACKGROUND)
    singleton.SCREENBUFFER.fill((0, 0, 0, 0))

    # if phandler.collide_rect_to_rect(_left_rect, _right_rect):
    # if phandler.collide_rect_to_bitmask(_left_rect, _right_mask, _right_rect):
    if phandler.collide_bitmask_to_bitmask(_left_mask, _left_rect, _right_mask, _right_rect):
        singleton.FRAMEBUFFER.fill((255, 0, 0))

    # testing
    singleton.FRAMEBUFFER.blit(_left_mask_surface, _left_rect, special_flags=pygame.BLEND_RGBA_MAX)
    # pygame.draw.rect(singleton.FRAMEBUFFER, (255, 255, 255), _left_rect, 1)
    singleton.FRAMEBUFFER.blit(_right_mask_surface, _right_rect, special_flags=pygame.BLEND_RGBA_MAX)
    # pygame.draw.rect(singleton.FRAMEBUFFER, (255, 255, 255), _right_rect, 1)

    _w.update_and_render(singleton.FRAMEBUFFER)

    if io.get_key_clicked(pygame.K_a):
        _right_rect.x -= 1
    if io.get_key_clicked(pygame.K_d):
        _right_rect.x += 1
    if io.get_key_clicked(pygame.K_w):
        _right_rect.y -= 1
    if io.get_key_clicked(pygame.K_s):
        _right_rect.y += 1




    # singleton.SCREENBUFFER.blit(_spritesheet.image, (100, 100))
    # singleton.SCREENBUFFER.blit(_mask.to_surface(), (200, 100))
        
    # ---------------------------- #
    # render screen items
    gl.GLContext.render_to_opengl_window(singleton.FRAMEBUFFER, singleton.DEFAULT_SHADER, singleton.FRAMEBUFFER_SHADER_QUAD, {
        "tex": 0,
        "time": singleton.ACTIVE_TIME    
    })
    gl.GLContext.render_to_opengl_window(singleton.SCREENBUFFER, singleton.DEFAULT_SCREEN_SHADER, singleton.SCREEN_SHADER_QUAD, {
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