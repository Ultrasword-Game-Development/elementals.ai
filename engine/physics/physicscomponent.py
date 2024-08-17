import pygame

from engine import singleton


# ---------------------------- #
# constants


# ---------------------------- #
# component

class PhysicsComponent:
    """
    A physics component is a single piece of data that is attached to a physicshandler.
    
    This type of object interferes with the physics of the world by applying
    
    - single forces onto objects
    - multiple forces onto objects
    - etc

    """

    def __init__(self):
        """ The Init Function """
        self._component_id = generate_component_id()
        self._handler = None
        self._active = True

    def __post_init__(self, handler: "PhysicsHandler"):
        """ Called after being added to an aspect """
        self._handler = handler
    
    # ---------------------------- #
    # logic
    
    def update(self):
        """ Updates the handler using the component """ 
        pass

    # ---------------------------- #
    # attributes
    
    def deactivate(self):
        """ Deactivate the component """
        self._active = False
    
    def activate(self):
        """ Activate the component """
        self._active = True
    
    def get_component_id(self):
        """ Get the component id """
        return self._component_id

# ---------------------------- #
# util functions

def generate_component_id():
    """ Generate a unique ID for the component """
    singleton.PHYSICS_COMP_ID_COUNT += 1
    return singleton.PHYSICS_COMP_ID_COUNT - 1
