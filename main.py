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

from engine.graphics import gl
from engine.graphics import animation
from engine.graphics import spritesheet


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

class World:
    def __init__(self):
        pass
world_save = "assets/level/level.save"

with open(world_save, 'rb') as f:
    w = dill.load(f)

print(w.__dict__)
print(w.t_signal.__dict__)
print(w.t_emitter.__dict__)


# signal testing

# w = World()
# w.t_signal = signal.Signal("Test Signal")
# w.t_emitter = w.t_signal.get_unique_emitter()
# w.t_signal.add_emitter_handling_function(lambda data: print(data))
# with open(world_save, 'wb') as f:
#     dill.dump(w, f)

# load an image
image = io.load_image('assets/sprites/icons/player-big.png')
ssheet = spritesheet.SpriteSheet('assets/sprites/mage.json')

t_ani = animation.load_animation_from_spritesheet(ssheet)
t_ani_reg = t_ani.get_registry()

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

    t_ani_reg.update()
    singleton.FRAMEBUFFER.blit(t_ani_reg.sprite, (10, 50))

    singleton.FRAMEBUFFER.blit(image, (200, 100))
    for x in range(len(ssheet)):
        singleton.FRAMEBUFFER.blit(ssheet[x], (x * 10, 30))


    # ---------------------------- #
    # final rendering
    t += 1
    ftex = gl.surface_to_texture(singleton.FRAMEBUFFER)
    ftex.use(0)
    gl.GLContext.FRAMEBUFFER_SHADER._program['tex'] = 0
    gl.GLContext.FRAMEBUFFER_SHADER._program['time'] = t
    gl.GLContext.FRAMEBUFFER_RENDER_OBJECT.render(mode=moderngl.TRIANGLE_STRIP)

    # singleton.WINDOW.blit(pygame.transform.scale(singleton.FRAMEBUFFER, singleton.WIN_SIZE), (0, 0))

    pygame.display.flip()
    ftex.release()

    # ---------------------------- #
    # update events
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            singleton.RUNNING = False
            pygame.quit()
            sys.exit()
    
    # update signals
    signal.update_signals()
    clock.tick(singleton.FPS)

    singleton.FRAME_COUNTER += 1

# ---------------------------- #