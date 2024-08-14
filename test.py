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
from engine.physics import gameobject

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


_left = gameobject.GameObject(
    position = (-100, 0),
    area = _spritesheet[0].get_size(),
    sprite_str = _spritesheet.get_sprite_str_id(0),
    create_mask = True
)
_left.set_area((_left.get_area()[0] - 1, _left.get_area()[1] - 1))
_left_mask_surface = _left.mask.to_surface()

_w.add_gameobject(_left)


_right = gameobject.GameObject(
    position = (-100, 0),
    area = _spritesheet[1].get_size(),
    sprite_str = _spritesheet.get_sprite_str_id(1),
    create_mask = True
)
_right.set_area((_right.get_area()[0] - 1, _right.get_area()[1] - 1))
_right_mask_surface = _right.mask.to_surface()

_w.add_gameobject(_right)

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
    if phandler.collide_bitmask_to_bitmask(_left.mask, _left.rect, _right.mask, _right.rect):
        singleton.FRAMEBUFFER.fill((255, 0, 0))

    _right.velocity.xy = 0, 0
    # if io.get_key_clicked(pygame.K_a):
    #     _right.velocity.x = -1
    # if io.get_key_clicked(pygame.K_d):
    #     _right.velocity.x = 1
    # if io.get_key_clicked(pygame.K_w):
    #     _right.velocity.y = -1
    # if io.get_key_clicked(pygame.K_s):
    #     _right.velocity.y = 1
    if io.get_key_pressed(pygame.K_a):
        _right.velocity.x += -1 * 100 * singleton.DELTA_TIME
    if io.get_key_pressed(pygame.K_d):
        _right.velocity.x += 1 * 100 * singleton.DELTA_TIME
    if io.get_key_pressed(pygame.K_w):
        _right.velocity.y += -1 * 100 * singleton.DELTA_TIME
    if io.get_key_pressed(pygame.K_s):
        _right.velocity.y += 1 * 100 * singleton.DELTA_TIME

    _w.move_entity_in_world(_right)

    _w.update_and_render(singleton.FRAMEBUFFER)


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