
import pygame

from engine import io

from engine.handler import component
from engine.handler import aspect

from engine.addon.components import renderable_comp
from engine.addon.components import animation_comp

# ---------------------------- #
# constants

COMPONENT_NAME = "Ray2DComponent"


# ---------------------------- #
# component

class Ray2DComponent(component.Component):
    
    def __init__(self, start: "Vector2", direction: "Vector2", magnitude: float):
        super().__init__()

        self._start = start
        self._direction = direction
        self._magnitude = magnitude

        self._entitycast = None
        self._tilecast = None

    def __post_gameobject__(self, gameobject: "GameObject"):
        """ Post init function """
        super().__post_aspect__(gameobject)


# ---------------------------- #
# aspect

class Ray2DAspect(aspect.Aspect):

    def __init__(self):
        super().__init__(target_component_classes=[Ray2DComponent])
    
    # ---------------------------- #
    # logic

    def handle(self, camera: "Camera"):
        """ Handle the aspect """
        for _comp in self.iter_components():
            # grab first entity / tile that collides with the object
            pass


# ---------------------------- #
# utils




# caching the component class
component.ComponentHandler.cache_component_class(Ray2DComponent)
