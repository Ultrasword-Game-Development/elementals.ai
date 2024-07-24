
import pygame

from engine import io
from engine import utils
from engine import singleton

from engine.ui import ui

from engine.graphics import shader


# ---------------------------- #
# 


# ---------------------------- #
# editor window

class Editor(ui.Frame):
    
    def render(self, surface: pygame.Surface):
        """ Render the object """

        super().render(surface)

# ---------------------------- #
# sprite selection window

class SpriteSelect(ui.UIObject):
    pass


# -------------------------------------------------- #
# editor objects

# ---------------------------- #
# color picker / selector

class ColorPicker(ui.ExternalUIObject):
    DEFAULT_COLORPICKTER_SHADER = "assets/shaders/color-picker.glsl"
    
    """
    the actual colorpicker object is a small 8x8 icon
    - drawn onto the framebuffer

    the actual picker window is a 256x256 window 
    - drawn onto the main surface
    - graphics used include: 
        - opengl to render colors
        - color gradient
        - mouse resizing capabilities

    """

    def __post_init__(self):
        """ Post init function """
        super().__post_init__()
        self._color = (0, 0, 0)
        self._padding = 1

        self._color_picker = pygame.Surface((self._screen_area[0] - self._padding, self._screen_area[1] - self._padding), 0, 16).convert_alpha()
        self._color_picker.fill(self._color)
        
        # create an opengl framebuffer
        self._rgb_surface = pygame.Surface((256, 256), 0, 16).convert_alpha()
        self._renderbuffer = singleton.CONTEXT.renderbuffer(self._rgb_surface.get_size(), components=4, samples=0)        
        self._gl_framebuffer = singleton.CONTEXT.framebuffer([self._renderbuffer], None)
        
        # load up shader + quad
        self._color_shader = shader.load_shader(self.DEFAULT_COLORPICKTER_SHADER)
        self._color_render_quad = singleton.FULL_QUAD_BUFFER
    
    def render(self, surface: pygame.Surface):
        """ Render the object """
        pygame.draw.rect(surface, (255, 255, 255), self.get_screen_ui_rect())

    def update(self):
        """ Update the object """
        # handle stuff if mouse clicked

        # have to use self.color_selector = (r, g, b, a) to update the color        
        pass
    
    @property
    def color_selection(self):
        """ Get the color selection """
        return self._color

    @color_selection.setter
    def color_selection(self, new: tuple):
        """ Set the new color sleection """
        if len(new) != 4: raise ValueError("Color must be a 4-tuple (255, 255, 255, 255)")
        self._color = new
        
        # render new color selector
        
        self._color_shader["color"] = self.color_selection[0:3]
        
        



