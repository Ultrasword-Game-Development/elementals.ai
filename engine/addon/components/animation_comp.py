
import pygame

from engine import io
from engine import singleton

from engine.handler import aspect
from engine.handler import component

from engine.graphics import animation

from engine.addon.components import sprite_comp
from engine.addon.components import mask_comp
from engine.addon.components import renderable_comp

# ---------------------------- #
# constants

COMPONENT_NAME = "AnimationComponent"

# ---------------------------- #
# component

class AnimationComponent(renderable_comp.RenderableComponent):
    
    def __init__(self, json_path: str):
        super().__init__()

        self._animation_str = json_path
        self._animation_registry = animation.load_animation_from_json(json_path).get_registry()
    
    def __post_gameobject__(self, _parent_gameobject: "GameObject"):
        """ Called after being added to a gameobject """
        super().__post_gameobject__(_parent_gameobject)

        self._sprite_component = self._parent_gameobject.get_component([sprite_comp.COMPONENT_NAME, mask_comp.COMPONENT_NAME])
        # update sprite
        self._sprite_component.set_sprite_str(self._animation_registry.sprite_path)

    # ---------------------------- #
    # logic

    def set_animation(self, animation_json: str, layer: str = None, all_layers: bool = True):
        """ Set the animation """
        self._animation_str = animation_json
        self._animation_registry = animation.load_animation_from_json(animation_json).get_registry()
        self.set_animation_layer(layer, all_layers = all_layers)

    def set_animation_type(self, animation_name: str):
        """ Set the animation """
        self._animation_registry.animation_type = animation_name
    
    def set_animation_layer(self, layer_name: str = None, all_layers: bool = True):
        """ Set the animation """
        if not all_layers and layer_name == None:
            raise ValueError("Layer name cannot be None if all_layers is False")
        self._animation_registry.animation_layer = layer
        self._animation_registry.compile_layers = all_layers
    
    def get_animation(self) -> str:
        """ Get the animation """
        return self._animation_str
    
    def get_animation_type(self) -> str:
        """ Get the animation """
        return self._animation_registry.animation_type
    
    def get_animation_layer(self) -> str:
        """ Get the animation """
        return self._animation_registry.animation_layer



# ---------------------------- #
# aspect

class AnimationAspect(aspect.Aspect):

    def __init__(self):
        """ Initialize the Sprite Renderer Aspect """
        super().__init__(priority=1, target_component_classes=[AnimationComponent])

    # ---------------------------- #
    def handle(self, camera: "Camera"):
        """ Handle the Sprite Renderer aspect """
        for _c in self.iter_components():
            _gameobject = _c.get_gameobject()
            _sprite = _c._sprite_component
            _registry = _c._animation_registry
                        
            # update sprite
            _registry.update()
            _sprite.set_sprite_str(_registry.sprite_path)

# ---------------------------- #
# utils


# caching the component class
component.ComponentHandler.cache_component_class(AnimationComponent)
