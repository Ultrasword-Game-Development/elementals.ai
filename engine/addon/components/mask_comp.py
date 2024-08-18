
import pygame

from engine.handler import aspect
from engine.handler import component

from engine.addon.components import sprite_comp

# ---------------------------- #
# constants

COMPONENT_NAME = "MaskedSpriteComponent"


# ---------------------------- #
# component

class MaskedSpriteComponent(sprite_comp.SpriteComponent):
    def __init__(self):
        """ Create a new Rect Component """
        super().__init__()

        self._offset = (0, 0)
        self._rect = pygame.Rect(0, 0, 0, 0)
        self._has_mask = False
        self._mask = None

        self._change = pygame.Rect(0, 0, 0, 0)
    
    # ---------------------------- #
    # logic

    def update_mask(self):
        """ Update the mask """
        self._has_mask = True
        self._mask = self.get_mask()
        _outline = self.get_mask().outline(every=3)
        _left = min(_outline, key=lambda x: x[0])
        _right = max(_outline, key=lambda x: x[0])
        _top = min(_outline, key=lambda x: x[1])
        _bottom = max(_outline, key=lambda x: x[1])
        self._change = pygame.Rect(
            _left[0] - self._rect.left, 
            _top[1] - self._rect.top, 
            _right[0] - _left[0] - self._rect.width, 
            _bottom[1] - _top[1] - self._rect.height
        )
        self._rect = pygame.Rect(_left[0], _top[1], _right[0] - _left[0], _bottom[1] - _top[1])

    def set_sprite_str(self, sprite_str: str):
        """ Set the sprite string """
        flag = (sprite_str != self._sprite_str)
        super().set_sprite_str(sprite_str)
        
        if flag:
            self.update_mask()
        
    def set_scale_area(self, area: tuple):
        """ Set the scale area """
        super().set_scale_area(area)
        self.update_mask()
    
    def get_mask(self):
        """ Get the mask """
        return pygame.mask.from_surface(self.get_sprite())

    # ---------------------------- #
    # serialize
    
    def __getstate__(self):
        """ Pickle state """
        state = super().__getstate__()
        del state['_mask']
        return state

    def __setstate__(self, state):
        """ Unpickle state """
        self.__dict__.update(state)
        self._mask = None

# ---------------------------- #
# aspect


# ---------------------------- #
# utils



# caching the component
component.ComponentHandler.cache_component_class(MaskedSpriteComponent)


