import pygame

from engine import singleton

from engine.physics import physicscomponent

from engine.addon.components import rect_comp

# ---------------------------- #
# constants


# ---------------------------- #
# component

class GravityComponent(physicscomponent.PhysicsComponent):
    """
    A component is a single piece of data that is attached to a gameobject.

    Components can be used to perform a SHIT TON of functions:

    - sprites
    - animation
    - ai movement
    - tiles
    - meshes

    """

    def __init__(self, gravity_vector: pygame.math.Vector2):
        """ The Init Function """
        super().__init__()
        self._gravity = gravity_vector
        self._rect_aspect = None

    def __post_init__(self, handler: "PhysicsHandler"):
        """ Called after being added to an aspect """
        super().__post_init__(handler)
        # grab the rect aspect
        self._rect_aspect = self._handler._world._aspect_handler.get_aspect(rect_comp.WorldRectAspect)
    
    # ---------------------------- #
    # logic
    
    def update(self):
        """ Updates the handler using the component """ 
        # rotate gravity by 1 degree
        self._gravity.rotate_ip(1)
        
        for _rect_comp in self._rect_aspect.iter_components():
            _rect_comp._velocity += self._gravity * singleton.DELTA_TIME

# ---------------------------- #
# utils


