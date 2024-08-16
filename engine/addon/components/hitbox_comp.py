
import pygame

from engine import singleton

from engine.handler import world
from engine.handler import aspect
from engine.handler import component

from engine.physics import phandler

from engine.addon.components import sprite_comp
from engine.addon.components import mask_comp
from engine.addon.components import physics_comp

# ---------------------------- #
# constants

COMPONENT_NAME = "HitBoxComponent"

# ---------------------------- #
# component

class HitBoxComponent(component.Component):
    def __init__(self, offset: tuple = (0, 0), area: tuple = (0, 0)):
        """ Create a new Hit Box Component """
        super().__init__()

        self._offset = pygame.math.Vector2(offset)
        self._area = pygame.math.Vector2(area)

        self._rect = pygame.FRect(*offset, *area)
    
    # ---------------------------- #
    # logic

    def get_rect(self):
        """ Get the rect """
        return self._rect
    
    def get_area(self):
        """ Get the area """
        return self._area
    
    def get_offset(self):
        """ Get the offset """
        return self._offset
    
    def set_offset(self, offset: tuple):
        """ Set the offset """
        self._offset.xy = offset
        self._rect.topleft = self._offset
    
    def set_area(self, area: tuple):
        """ Set the area """
        self._area.xy = area
        self._rect.size = area


# ---------------------------- #
# aspect


# ---------------------------- #
# utils



# caching the component
component.ComponentHandler.cache_component_class(HitBoxComponent)
