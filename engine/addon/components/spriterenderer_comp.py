
import pygame

from engine import io
from engine import singleton

from engine.handler import component
from engine.handler import aspect

from engine.addon.components import sprite_comp
from engine.addon.components import mask_comp
from engine.addon.components import renderable_comp

# ---------------------------- #
# constants

COMPONENT_NAME = "SpriteRendererComponent"

# ---------------------------- #
# component

class SpriteRendererComponent(renderable_comp.RenderableComponent):
    
    def __init__(self):
        super().__init__()

        self._sprite_component = None
    
    # ---------------------------- #
    # logic

    def __post_gameobject__(self, _parent_gameobject: "GameObject"):
        """ Called after being added to a gameobject """
        super().__post_gameobject__(_parent_gameobject)

        self._sprite_component = self._parent_gameobject.get_component([sprite_comp.COMPONENT_NAME, mask_comp.COMPONENT_NAME])


# ---------------------------- #
# aspect

class SpriteRendererAspect(aspect.Aspect):

    def __init__(self):
        """ Initialize the Sprite Renderer Aspect """
        super().__init__(target_component_classes=[SpriteRendererComponent])

    # ---------------------------- #
    # logic
    
    def handle(self, camera: "Camera"):
        """ Handle the Sprite Renderer aspect """
        for _c in self.iter_components():
            _gameobject = _c.get_gameobject()
            _sprite_comp = _c._sprite_component

            # check if has sprite
            if not _sprite_comp.get_sprite_str():
                return
            
            _layer_surface = self._handler._world._layers[_gameobject.zlayer]._layer_buffer
            
            _sprite = _sprite_comp.get_sprite()
            # render sprite into world
            _position = _gameobject.position - camera.position - _sprite_comp._sprite_rect.center
            _layer_surface.blit(_sprite, _position)


class SpriteRendererDebugAspect(aspect.Aspect):

    def __init__(self):
        """ Create a new Sprite Renderer Debug Aspect """
        super().__init__(target_component_classes=[SpriteRendererComponent])
    
    # ---------------------------- #
    # logic

    def handle(self, camera: "Camera"):
        """ Handle the Sprite Renderer Debug Aspect """
        if not singleton.DEBUG:
            return

        for _c in self.iter_components():
            _gameobject = _c.get_gameobject()
            _sprite_comp = _c._sprite_component

            _layer_surface = _gameobject._parent_phandler._world._layers[_gameobject.zlayer]._layer_buffer
            
            # render rect into world
            _pos = _gameobject.position - camera.position - _sprite_comp._sprite_rect.center
            pygame.draw.rect(
                _layer_surface,
                (255, 0, 0), 
                (_pos, _sprite_comp._sprite_rect.size),
                1
            )

# ---------------------------- #
# utils




# caching the component class
component.ComponentHandler.cache_component_class(SpriteRendererComponent)
