import sys
import dill
import time
import pickle
import moderngl
import pygame

from engine import io
from engine import utils
from engine import singleton

from engine.handler import signal

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

# ---------------------------- #
# editor UI loadup

ui.start_ui()

# editor window

base_window = ui.UIObject(0, 0, padding=2)
base_window.set_background_color(utils.hex_to_rgb('002266'))

side_window = ui.UIObject(0, 0, h=0.8, padding=5, parent=base_window)
side_window.set_background_color(utils.hex_to_rgb('004488'))

ui.add_ui_object(base_window, side_window)

# ---------------------------- #

singleton.RUNNING = True
singleton.START_TIME = time.time()

while singleton.RUNNING:
    singleton.END_TIME = time.time()
    singleton.DELTA_TIME = singleton.END_TIME - singleton.START_TIME
    singleton.START_TIME = singleton.END_TIME

    # ---------------------------- #
    singleton.FRAMEBUFFER.fill(singleton.WIN_BACKGROUND)

    # print(io.get_mouse_rel())
    
    ui.update_ui_items()
    ui.render_ui_items(singleton.FRAMEBUFFER)
    

    # ---------------------------- #
    # final rendering
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