import moderngl
import pygame
from array import array

from engine import io
from engine import singleton

from engine.handler import signal

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
    'color_channels': 4,
    'filter': (moderngl.NEAREST, moderngl.NEAREST),
    'swizzle': 'BGRA', # pygame formatting is weird
}


def surface_to_texture(surface, config: dict = DEFAULT_CONVERSION_CONFIG):
    """ Convert a pygame surface to a moderngl texture """
    tex = singleton.CONTEXT.texture(surface.get_size(), config['color_channels'])
    tex.filter = config['filter']
    tex.swizzle = config['swizzle']
    tex.write(surface.get_view('1'))
    return tex


# ---------------------------- #
# context

class GLContext:
    # ---------------------------- #
    # items

    SCREEN_SHADER = None
    FRAMEBUFFER_SHADER = None

    SCREEN_RENDER_OBJECT = None
    FRAMEBUFFER_RENDER_OBJECT = None

    ACTIVE_SPRITES = {}
    _SPRITE_COUNTER = 0

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
        singleton.FRAMEBUFFER = pygame.Surface(singleton.FB_SIZE, singleton.DEFAULT_SURFACE_FLAGS, 16).convert_alpha()
        singleton.SCREENBUFFER = pygame.Surface(singleton.WIN_SIZE, singleton.DEFAULT_SURFACE_FLAGS, 16).convert_alpha()
        
        # load all pygame items
        io.KEY_MOD_CLICKED = pygame.key.get_mods()
        io.init_audio()

        # create signal
        singleton.GLOBAL_FRAME_SIGNAL_EMITTER = signal.Signal(singleton.GLOBAL_FRAME_SIGNAL_KEY).get_unique_emitter()
        singleton.GLOBAL_FILE_DROP_SIGNAL_EMITTER = signal.Signal(singleton.GLOBAL_FILE_DROP_SIGNAL_KEY).get_unique_emitter()
        singleton.GLOBAL_KEYBOARD_PRESS_SIGNAL_EMITTER = signal.Signal(singleton.GLOBAL_KEYBOARD_PRESS_SIGNAL_KEY).get_unique_emitter()

        # empty the surfaces
        singleton.FRAMEBUFFER.fill((0, 0, 0, 0))
        singleton.SCREENBUFFER.fill((0, 0, 0, 0))

        # create the screen quad buffer
        singleton.CONTEXT = moderngl.create_context()
        singleton.FULL_QUAD_BUFFER = singleton.CONTEXT.buffer(data=array('f', DEFAULT_QUAD_BUFFER))

        # create the framebuffer render object
        cls.FRAMEBUFFER_SHADER = shader.load_shader(singleton.DEFAULT_SHADER)
        cls.SCREEN_SHADER = shader.load_shader(singleton.DEFAULT_SCREEN_SHADER)
        cls.handle_resizing(singleton.WIN_SIZE)

        cls.FRAMEBUFFER_RENDER_OBJECT = cls.FRAMEBUFFER_SHADER.load_quad_vertexarray(singleton.FRAMEBUFFER_SHADER_QUAD, [
                (singleton.FULL_QUAD_BUFFER, '2f 2f', 'vert', 'texcoord')
        ])
        cls.SCREEN_RENDER_OBJECT = cls.SCREEN_SHADER.load_quad_vertexarray(singleton.SCREEN_SHADER_QUAD, [
                (singleton.FULL_QUAD_BUFFER, '2f 2f', 'vert', 'texcoord')
        ])

        # debug output
        print("Using OpenGL version:", singleton.CONTEXT.version_code)

        return moderngl.create_context()
    
    @classmethod
    def render_to_opengl_window(cls, sprite: pygame.Surface, _shader: str, _vao: str, variables: dict = {}):
        """ Render a sprite to the opengl window """
        singleton.CONTEXT.screen.use()
        a_shader = shader.load_shader(_shader)
        tex = surface_to_texture(sprite)
        tex.use(0)
        for key, value in variables.items():
            a_shader[key] = value
        a_shader.load_quad_vertexarray(_vao).render(mode=moderngl.TRIANGLE_STRIP)
        tex.release()
    
    @classmethod
    def render_to_framebuffer(cls, framebuffer, _shader: str, _vao: str, variables: dict = {}, work_group_size: tuple = (8, 8, 8)):
        """ Render to a framebuffer - compute shader only """
        a_shader = shader.load_shader(_shader)
        for key, value in variables.items():
            a_shader[key] = value
        
        # work groups :)
        nx, ny, nz = a_shader.get_size()[0] // work_group_size[0], a_shader.get_size()[1] // work_group_size[1], 1
        framebuffer.bind_to_image(0, read=False, write=True)
        
        a_shader.run(nx, ny, nz)
    
    @classmethod
    def register_sprite(cls, name: str, sprite: pygame.Surface):
        """ Register a sprite to the active sprites """
        cls.ACTIVE_SPRITES[name] = (sprite, cls._SPRITE_COUNTER)
        cls._SPRITE_COUNTER += 1

    # ---------------------------- #
    # utils

    @classmethod
    def handle_resizing(cls, new_size: tuple):
        """ Handles the resizing of the window """
        singleton.WIN_SIZE = new_size
        _desired_ratio = round(16 / 9, ndigits=4) # w / h
        # hceck if content is same ratio
        _aspect_ratio = round(new_size[0] / new_size[1], ndigits=4)
        _offset = (0, 0)
         
        # width is too big - create shift in x axis 
        if _aspect_ratio < _desired_ratio:
            # find offset
            _offset = (
                (new_size[0] - new_size[1] * _desired_ratio) // 2,
                0
            )
            # find new_size
            new_size = (new_size[1] * _desired_ratio, new_size[1])
        # width is too small - create shift in y axis
        elif _aspect_ratio > _desired_ratio:
            # find offset
            _offset = (
                0,
                (new_size[1] - new_size[0] / _desired_ratio) // 2
            )
            # find new_size
            new_size = (new_size[0], new_size[0] / _desired_ratio)
            
        
        singleton.CONTEXT.viewport = (*_offset, *new_size)
