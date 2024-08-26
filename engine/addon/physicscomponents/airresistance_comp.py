import math
import pygame

from engine import utils
from engine import singleton

from engine.physics import physicscomponent

from engine.addon.components import rect_comp
from engine.addon.components import physics_comp

# ---------------------------- #
# constants


# ---------------------------- #
# component

class AirResistanceComponent(physicscomponent.PhysicsComponent):
    """
    A component is a single piece of data that is attached to a gameobject.

    Components can be used to perform a SHIT TON of functions:

    - sprites
    - animation
    - ai movement
    - tiles
    - meshes

    """

    def __init__(self, resistance_factor: float):
        """ The Init Function - resistance factor should be between [0, 1] ~ generally around 0.1 for good measure"""
        super().__init__()
        self._resistance_factor = resistance_factor
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
        for _rect_comp in self._rect_aspect.iter_components():

            # make sure not touching ground
            if _rect_comp._touching[physics_comp.TOUCHING_BOTTOM]:
                continue
            
            blend = 0.3
            _rect_comp._acceleration += _rect_comp._velocity.rotate(180) * blend

# ---------------------------- #
# utils


