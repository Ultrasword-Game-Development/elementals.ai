
import pygame

from engine.handler import component
from engine.handler import aspect

# ---------------------------- #
# constants

COMPONENT_NAME = "PhysicsComponent"

PHYSICS_OBJECTS_CLASSES = []

TOUCHING_LEFT = 0
TOUCHING_RIGHT = 1
TOUCHING_TOP = 2
TOUCHING_BOTTOM = 3

# ---------------------------- #
# component

class PhysicsComponent(component.Component):

    def __init__(self):
        """ Create a new Physics Component """
        super().__init__()

        self._collision_mask = 0b0000000000000000

        # stored in kg
        self._mass = 0
        self._velocity = pygame.math.Vector2(0, 0)
        self._acceleration = pygame.math.Vector2(0, 0)
        self._force = pygame.math.Vector2(0, 0)
        self._touching = [False, False, False, False]

        # default mask value
        self.set_mask_value(0, True)
    
    # ---------------------------- #
    # logic
    
    def set_mask_value(self, mask_index: int, value: bool):
        """ Set the mask value """
        if mask_index < 0 or mask_index > 15:
            raise ValueError("mask_index must be between 0 and 15")
        if value:
            self._collision_mask |= 0b1 << (mask_index)
        else:
            self._collision_mask &= ~(0b1 << (mask_index))
    
    def get_mask_value(self, mask_index: int):
        """ Get the mask value """
        if mask_index < 0 or mask_index > 15:
            raise ValueError("mask_index must be between 0 and 15")
        return (self._collision_mask >> (mask_index - 1)) & 0b1
    
    def get_mask(self):
        """ Get the mask """
        return self._collision_mask
    
    # ---------------------------- #
    # component logic

    def add_detection_step(self, detection_step: "DetectionStep"):
        """ Add a detection step """
        self._detection_steps.append(detection_step)
    
    def add_resolution_step(self, resolution_step: "ResolutionStep"):
        """ Add a resolution step """
        self._resolution_steps.append(resolution_step)


class CollisionStep:
    def __init__(self, name: str):
        """ Create a new Collision Step """
        self._name = name
    
    # ---------------------------- #
    # logic

    def handle(self, component: "Component"):
        """ Handle the component """
        pass

# ---------------------------- #
# aspect

class PhysicsAspect(aspect.Aspect):
    """
    The Physics Aspect

    Handles everything physics related. That's literally it.
    """
    
    def __init__(self):
        """ Create a new Physics Aspect """
        super().__init__(target_component_classes=PHYSICS_OBJECTS_CLASSES)
    
    # ---------------------------- #
    # logic

    def handle(self, camera: "Camera"):
        """ Handle the component """
        pass

# ---------------------------- #
# utils

def add_physics_target_component_class(component_class: "Component Class"):
    """ Add a physics target component class """
    if type(component_class).__name__ != "type":
        raise ValueError("component_class must be a class")
    PHYSICS_OBJECTS_CLASSES.append(component_class)


# caching the component class
component.ComponentHandler.cache_component_class(PhysicsComponent)

