
import pygame

from engine import singleton

from engine.handler import world
from engine.handler import aspect
from engine.handler import component

from engine.physics import phandler

from engine.addon.components import sprite_comp
from engine.addon.components import mask_comp
from engine.addon.components import physics_comp
from engine.addon.components import hitbox_comp

# ---------------------------- #
# constants

COMPONENT_NAME = "WorldRectComponent"

# ---------------------------- #
# component

class CameraControlComponent(component.Component):
    def __init__(self, active: bool = True):
        """ Create a new Rect Component that collides with the World """
        super().__init__()
        
        self._active = active
        self._camera = None

    
    def __post_gameobject__(self, gameobject: "GameObject"):
        """ Post init function """
        super().__post_gameobject__(gameobject)
        self._camera = self._handler._world._camera
    
    # ---------------------------- #
    # logic
    
    def get_camera(self):
        """ Get the camera """
        return self._camera

    def set_camera(self, camera: "Camera"):
        """ Set the camera """
        self._camera = camera
        
    def get_active(self):
        """ Get the active state """
        return self._active
    
    def set_active(self, active: bool):
        """ Set the active state """
        self._active = active
    
    # ---------------------------- #
    # serialize
    
    def __getstate__(self):
        """ Pickle state """
        state = self.__dict__.copy()
        return state

    def __setstate__(self, state):
        """ Unpickle state """
        self.__dict__.update(state)


# ---------------------------- #
# aspect

class CameraControlAspect(aspect.Aspect):
    def __init__(self):
        """ Create a new World Rect Aspect """
        super().__init__(target_component_classes=[CameraControlComponent])
    
    # ---------------------------- #
    # logic

    def handle(self, camera: "Camera"):
        """ Handle the aspect """
        for _camera in self.iter_components():
            # update camera position to gameobject position
            _camera._camera._rect.center = _camera._parent_gameobject.position


# ---------------------------- #
# utils



# caching the component
component.ComponentHandler.cache_component_class(CameraControlComponent)


