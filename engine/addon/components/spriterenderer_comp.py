
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
    def handle(self):
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
            _position = _gameobject.position - self._handler._world._camera.position
            _layer_surface.blit(_sprite, _position)

            if singleton.DEBUG:
                pygame.draw.rect(
                    _layer_surface, 
                    (255, 0, 0), 
                    pygame.Rect(_position, _sprite.get_size()), 
                    1
                )



# ---------------------------- #
# utils




# caching the component class
component.ComponentHandler.cache_component_class(SpriteRendererComponent)
