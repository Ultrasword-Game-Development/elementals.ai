
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

class HitBoxComponent(physics_comp.PhysicsComponent):
    def __init__(self, offset: tuple = (0, 0), area: tuple = (0, 0)):
        """ Create a new Hit Box Component """
        super().__init__()

        self._rect = pygame.FRect(*offset, *area)
    
    def __post_gameobject__(self, gameobject: "GameObject"):
        """ Post init function """
        super().__post_gameobject__(gameobject)
    
    # ---------------------------- #
    # logic

    def get_rect(self):
        """ Get the rect """
        return self._rect
    
    def get_area(self):
        """ Get the area """
        return self._rect.size
    
    def get_offset(self):
        """ Get the offset """
        return self._rect.topleft
    
    def set_offset(self, offset: tuple):
        """ Set the offset """
        self._rect.topleft = offset
    
    def set_area(self, area: tuple):
        """ Set the area """
        self._rect.size = area


# ---------------------------- #
# aspect

class HitBoxDebugAspect(aspect.Aspect):
    def __init__(self):
        """ Create a new Hit Box Debug Aspect """
        super().__init__(target_component_classes=[HitBoxComponent])
    
    # ---------------------------- #
    # logic

    def handle(self, camera: "Camera"):
        """ Handle the Hit Box Debug Aspect """
        if not singleton.DEBUG:
            return

        for _c in self.iter_components():
            _gameobject = _c.get_gameobject()
            
            _layer_surface = _gameobject._parent_phandler._world._layers[_gameobject.zlayer]._layer_buffer
            
            # render hitbox into world
            _position = _gameobject.position - camera.position + _c.get_offset()

            pygame.draw.rect(
                _layer_surface,
                (255, 0, 255), 
                pygame.Rect(_position, _c.get_area()), 
                1
            )


# ---------------------------- #
# utils



# caching the component
component.ComponentHandler.cache_component_class(HitBoxComponent)
