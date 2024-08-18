
import pygame

from engine.handler import aspect
from engine.handler import component

# ---------------------------- #
# constants

COMPONENT_NAME = "StateMachineComponent"

# ---------------------------- #
# component

class StateMachineComponent(component.Component):
    
    def __init__(self):
        """ Initialize the renderable component """
        super().__init__()
        self._states = []



# ---------------------------- #
# aspect



# ---------------------------- #
# utils



# caching the component class
component.ComponentHandler.cache_component_class(RenderableComponent)
