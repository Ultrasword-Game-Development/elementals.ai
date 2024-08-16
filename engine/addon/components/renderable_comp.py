
import pygame

from engine.handler import aspect
from engine.handler import component

# ---------------------------- #
# constants

COMPONENT_NAME = "RenderableComponent"

# ---------------------------- #
# component

class RenderableComponent(component.Component):
    
    def __init__(self):
        """ Initialize the renderable component """
        super().__init__()



# ---------------------------- #
# aspect



# ---------------------------- #
# utils



# caching the component class
component.ComponentHandler.cache_component_class(RenderableComponent)