
import pygame

from engine.handler import aspect
from engine.handler import component

# ---------------------------- #
# constants

COMPONENT_NAME = "RenderableComponent"

# ---------------------------- #
# component

class RenderableComponent(component.Component):
    
    def __init__(self, zlayer: int = None):
        """ Initialize the renderable component """
        super().__init__()
        self.zlayer = zlayer

    # ---------------------------- #
    # logic

    def __post_gameobject__(self, _parent_gameobject: "GameObject"):
        """ Called after being added to a gameobject """
        super().__post_gameobject__(_parent_gameobject)

        # set zlayer
        if self.zlayer == None:
            self.zlayer = _parent_gameobject.zlayer



# ---------------------------- #
# aspect



# ---------------------------- #
# utils



# caching the component class
component.ComponentHandler.cache_component_class(RenderableComponent)
