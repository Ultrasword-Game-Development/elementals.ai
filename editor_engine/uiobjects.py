
import pygame

from engine import io
from engine import utils

from engine.ui import ui

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
    
    def render(self, surface: pygame.Surface):
        """ Render the object """
        pygame.draw.rect(surface, (255, 255, 255), self.get_screen_ui_rect())

    def update(self):
        """ Update the object """
        # check if mouse clicked
        pass






