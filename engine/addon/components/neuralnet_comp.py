
import pygame
import neat

from engine import io

from engine.handler import component
from engine.handler import aspect

# ---------------------------- #
# constants

COMPONENT_NAME = "NeuralNetComponent"


# ---------------------------- #
# component

class NeuralNetComponent(component.Component):
    def __init__(self):
        super().__init__()

        self._network = neat.nn

    def __post_gameobject__(self, gameobject: "GameObject"):
        """ Post init function """
        super().__post_aspect__(gameobject)        

    # ---------------------------- #
    # logic




# ---------------------------- #
# aspect


# ---------------------------- #
# utils




# caching the component class
component.ComponentHandler.cache_component_class(SpriteComponent)
