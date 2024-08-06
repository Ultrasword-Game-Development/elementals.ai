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

from engine.ui import ui

from engine.graphics import gl
from engine.graphics import animation
from engine.graphics import spritesheet

from editor_engine import uiobjects
from editor_engine import editor_singleton
# ---------------------------- #
# create a window

pygame.init()

clock = pygame.time.Clock()

singleton.WIN_BACKGROUND = utils.hex_to_rgb('001E3D')
singleton.DEBUG = False
singleton.EDITOR_DEBUG = True
singleton.FB_SIZE = (1920, 1080)
singleton.FPS = 30

gl.GLContext.add_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
gl.GLContext.add_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
gl.GLContext.add_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
gl.GLContext.add_attribute(pygame.GL_CONTEXT_FORWARD_COMPATIBLE_FLAG, True)
gl.GLContext.create_context()


# ---------------------------- #
# editor UI loadup


# Note: must load world + start ui
ui.start_ui()
editor_singleton.CURRENT_EDITING_WORLD = (w:=singleton.load_world("assets/level/test_world.elal"))

base_window = ui.UIObject(0, 0, padding=2)
base_window.set_background_color(utils.hex_to_rgb('00233A'))

# === editor window
editor_window = uiobjects.Editor(0, 0, w = 0.8, h=1.0, padding=1, parent=base_window)
editor_window.set_background_color(utils.hex_to_rgb('033454'))

# === right side hub
right_side_hub = ui.UIObject(0.8, 0, w = 0.2, h=1.0, padding=[0, 1, 1, 1], parent=base_window)
right_side_hub.set_background_color(utils.hex_to_rgb('1F618D'))

# = title
editing_world_name = ui.Text(0.0, 0.0, w=1.0, h=0.05, padding=1, parent=right_side_hub)
editing_world_name.set_background_color(utils.hex_to_rgb('#00082f'))
editing_world_name.set_font("assets/fonts/Roboto-Medium.ttf")
editing_world_name.set_text(editor_singleton.CURRENT_EDITING_WORLD._world_storage_key)

# = buttons + etc
save_button = uiobjects.SaveButton(0.0, 0.05, w=0.5, h=0.06, padding=1, parent=right_side_hub)
save_button.set_background_color(utils.hex_to_rgb('#001c3e'))
save_button.set_font("assets/fonts/Roboto-Medium.ttf")
save_button.set_text("Save", center=True)

new_world_button = uiobjects.NewWorldButton(0.5, 0.05, w=0.5, h=0.06, padding=1, parent=right_side_hub)
new_world_button.set_background_color(utils.hex_to_rgb('#001c3e'))
new_world_button.set_font("assets/fonts/Roboto-Medium.ttf")
new_world_button.set_text("New World", center=True)

# = tab selector
# TODO - change
tab_selector = uiobjects.TabsManager(0.0, 0.11, w=1.0, h=0.04, padding=1, parent=right_side_hub)
tab_selector.set_background_color(utils.hex_to_rgb('#001B6A'))

for i in range(1, 11):
    tab_selector.add_tab(uiobjects.Tab(f"Tab {i}", parent=tab_selector))


# = sprite selection window
sprite_select_window = uiobjects.SpriteSelect(0.0, 0.15, padding=1, parent=right_side_hub)
sprite_select_window.set_background_color(utils.hex_to_rgb('#010e29'))
sprite_select_window.set_border(utils.hex_to_rgb('#ffffff'), 2)

ui.add_ui_object(base_window, editor_window, sprite_select_window, right_side_hub, save_button, new_world_button)
ui.add_ui_object(tab_selector, editing_world_name)



# editor_window.resize_screen(w.camera.area * 2)

# color_picker = uiobjects.ColorPicker(w=0.4, h=0.3, padding=10, parent=editor_window)
# ui.add_ui_object(color_picker)

# color_picker.color_selection = utils.normalize_rgb((255, 0, 0, 255))


# ---------------------------- #

editor_window.load_config_file("assets/editor/config/tab-example.json")

# ---------------------------- #

def exit_func():
    """ Exit function """
    # save the world or something
    print("saving world - (not really)")
    # don't actaully do it yet

singleton.GAME_EXIT_FUNCTION = exit_func

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