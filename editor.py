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

from engine.ui import ui

from engine.graphics import gl
from engine.graphics import animation
from engine.graphics import spritesheet

from editor_engine import uiobjects

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

base_window = ui.UIObject(0, 0, padding=2)
base_window.set_background_color(utils.hex_to_rgb('00233A'))

editor_window = uiobjects.Editor(0, 0, w = 0.8, h=1.0, padding=1, parent=base_window)
editor_window.set_background_color(utils.hex_to_rgb('033454'))

sprite_select_window = uiobjects.SpriteSelect(0.8, 0, w = 0.2, h=1.0, padding=[0, 1, 1, 1], parent=base_window)
sprite_select_window.set_background_color(utils.hex_to_rgb('#1F618D'))

ui.add_ui_object(base_window, editor_window, sprite_select_window)


color_picker = uiobjects.ColorPicker(w=0.4, h=0.3, padding=10, parent=editor_window)
ui.add_ui_object(color_picker)

color_picker.color_selection = utils.normalize_rgb((255, 0, 0, 255))

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
    # framebuffer rendering
    gl.GLContext.render_to_opengl_window(singleton.FRAMEBUFFER, singleton.DEFAULT_SHADER, singleton.FRAMEBUFFER_SHADER_QUAD, {
        "tex": 0,
        "time": singleton.ACTIVE_TIME
    })

    # ---------------------------- #
    # render screen items
    ui.render_screen_ui_items(singleton.SCREENBUFFER)
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