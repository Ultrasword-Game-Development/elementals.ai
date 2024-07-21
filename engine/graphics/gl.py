import moderngl
import pygame
from array import array

from engine import singleton
from engine.graphics import shader

# ---------------------------- #
# utils

DEFAULT_QUAD_BUFFER = [
    # position (x, y), uv coords (x, y)
    -1.0, 1.0, 0.0, 0.0,  # topleft
    1.0, 1.0, 1.0, 0.0,   # topright
    -1.0, -1.0, 0.0, 1.0, # bottomleft
    1.0, -1.0, 1.0, 1.0,  # bottomright
]

DEFAULT_CONVERSION_CONFIG = {
    'bit_depth': 4,
    'filter': (moderngl.NEAREST, moderngl.NEAREST),
    'swizzle': 'BGRA', # pygame formatting is weird
}


def surface_to_texture(surface, config: dict = DEFAULT_CONVERSION_CONFIG):
    """ Convert a pygame surface to a moderngl texture """
    tex = singleton.CONTEXT.texture(surface.get_size(), config['bit_depth'])
    tex.filter = config['filter']
    tex.swizzle = config['swizzle']
    tex.write(surface.get_view('1'))
    return tex


# ---------------------------- #
# context

class GLContext:
    # ---------------------------- #
    # items

    FRAMEBUFFER_SHADER = None
    FRAMEBUFFER_RENDER_OBJECT = None

    # ---------------------------- #
    # init

    @classmethod
    def add_attribute(cls, name, value):
        """ Add an attribute to the GL context """
        singleton.ATTRIBUTES.append((name, value))
    
    # ---------------------------- #
    # functions

    @classmethod
    def create_context(cls):
        """ Create a new GL context """
        # set attributes for pygame window
        for attr, val in singleton.ATTRIBUTES:
            pygame.display.gl_set_attribute(attr, val)

        # create pygame window
        singleton.WINDOW = pygame.display.set_mode(singleton.WIN_SIZE, singleton.WIN_FLAGS, singleton.WIN_DEPTH, 0, 0)
        singleton.FRAMEBUFFER = pygame.Surface(singleton.FB_SIZE, 0, 16).convert_alpha()

        # create the screen quad buffer
        singleton.CONTEXT = moderngl.create_context()
        singleton.FULL_QUAD_BUFFER = singleton.CONTEXT.buffer(data=array('f', DEFAULT_QUAD_BUFFER))

        # create the framebuffer render object
        cls.FRAMEBUFFER_SHADER = shader.ShaderProgram('assets/shaders/default.glsl')
        cls.FRAMEBUFFER_SHADER.add_layer(shader.TYPE_VERTEX)
        cls.FRAMEBUFFER_SHADER.add_layer(shader.TYPE_FRAGMENT)
        cls.FRAMEBUFFER_SHADER.create()

        cls.FRAMEBUFFER_RENDER_OBJECT = singleton.CONTEXT.vertex_array(cls.FRAMEBUFFER_SHADER._program, [
                (singleton.FULL_QUAD_BUFFER, '2f 2f', 'vert', 'texcoord')
        ])

        return moderngl.create_context()



