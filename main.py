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

from engine import io
from engine import utils
from engine import singleton

from engine.handler import signal
from engine.handler import world

from engine.graphics import gl
from engine.graphics import animation
from engine.graphics import spritesheet

from engine.addon import tiles


# ---------------------------- #
# create a window

pygame.init()

clock = pygame.time.Clock()

singleton.WIN_BACKGROUND = utils.hex_to_rgb('71C828')

gl.GLContext.add_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
gl.GLContext.add_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
gl.GLContext.add_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
gl.GLContext.add_attribute(pygame.GL_CONTEXT_FORWARD_COMPATIBLE_FLAG, True)
gl.GLContext.create_context()

# ---------------------------- #
# testing


world_save = "assets/level/world.elal"

w = world.World.load_world(world_save)

# w = world.World()
# w.t_signal = signal.Signal("Test Signal")
# w.t_emitter = w.t_signal.get_unique_emitter()
# w.t_signal.add_emitter_handling_function("_test_signal", lambda data: print(data))

# w.get_layer_at(0).set_chunk_at(world.Chunk(
#     (w.get_camera_chunk())
# ))

# _c = w.get_layer_at(0).get_chunk_at(w.get_camera_chunk())
# _spritesheet = spritesheet.load_spritesheet("assets/sprites/player.json")

# # temp load a chunk up with a tile
# for i in range(singleton.DEFAULT_CHUNK_WIDTH):
#     for j in range(2):
#         _c.set_tile_at((i, j), world.DefaultTile((i, j), "assets/test/screenshot.png"))

# for i in range(singleton.DEFAULT_CHUNK_WIDTH):
#     _c.set_tile_at((i, 3), world.DefaultTile((i, j), _spritesheet.get_sprite_str_id(i)))
# # add an animated sprite at location - (0, 0)
# _c.set_tile_at((0, 0), tiles.SemiAnimatedTile((0, 0), "assets/sprites/player.json"))
# _c.set_tile_at((0, 2), tiles.SemiAnimatedTile((0, 0), "assets/sprites/player.json"))
# _c.set_tile_at((0, 3), tiles.AnimatedTile((0, 0), "assets/sprites/player.json", offset=2))

# w.ssheet = spritesheet.load_spritesheet("assets/sprites/mage.json")
# w.t_ani = animation.load_animation_from_json("assets/sprites/mage.json")
# w.t_ani_reg = w.t_ani.get_registry()
# w.p_ani = animation.load_animation_from_json('assets/sprites/player.json')
# w.p_ani_reg = w.p_ani.get_registry()




print("world flag should be on")
singleton.save_world(world_save, w)
print("world flag off")



# ---------------------------- #

t = 0

singleton.RUNNING = True
singleton.START_TIME = time.time()

while singleton.RUNNING:
    singleton.END_TIME = time.time()
    singleton.DELTA_TIME = singleton.END_TIME - singleton.START_TIME
    singleton.START_TIME = singleton.END_TIME

    # ---------------------------- #
    singleton.FRAMEBUFFER.fill(singleton.WIN_BACKGROUND)
    
    # w.t_emitter.emit()
    
    w.update_and_render(singleton.FRAMEBUFFER)

    # w.t_ani_reg.update()
    # singleton.FRAMEBUFFER.blit(w.t_ani_reg.sprite, (10, 50))
    # w.p_ani_reg.update()
    # singleton.FRAMEBUFFER.blit(w.p_ani_reg.sprite, (100, 90))

    # for x in range(len(w.ssheet)):
    #     singleton.FRAMEBUFFER.blit(w.ssheet[x], (x * 10, 30))


    # ---------------------------- #
    # final rendering
    t += 1
    ftex = gl.surface_to_texture(singleton.FRAMEBUFFER)
    ftex.use(0)
    gl.GLContext.FRAMEBUFFER_SHADER._program['tex'] = 0
    gl.GLContext.FRAMEBUFFER_SHADER._program['time'] = singleton.ACTIVE_TIME
    gl.GLContext.FRAMEBUFFER_RENDER_OBJECT.render(mode=moderngl.TRIANGLE_STRIP)

    # singleton.WINDOW.blit(pygame.transform.scale(singleton.FRAMEBUFFER, singleton.WIN_SIZE), (0, 0))

    pygame.display.flip()
    ftex.release()

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