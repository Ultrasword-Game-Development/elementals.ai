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

class FrictionComponent(physicscomponent.PhysicsComponent):
    """
    A component is a single piece of data that is attached to a gameobject.

    Components can be used to perform a SHIT TON of functions:

    - sprites
    - animation
    - ai movement
    - tiles
    - meshes

    """

    def __init__(self, dynamic: float = 0.7, static: float = 0.3):
        """ The Init Function - resistance factor should be between [0, 1] ~ generally around 0.1 for good measure"""
        super().__init__()
        self._rect_aspect = None
        self._dynamic = dynamic
        self._static = static

    def __post_init__(self, handler: "PhysicsHandler"):
        """ Called after being added to an aspect """
        super().__post_init__(handler)
        # grab the rect aspect
        self._rect_aspect = self._handler._world._aspect_handler.get_aspect(rect_comp.WorldRectAspect)
    
    # ---------------------------- #
    # logic

    def update(self):
        """ Updates the handler using the component """
        static_blend = math.pow(self._static, singleton.DELTA_TIME * 4)
        dynamic_blend = math.pow(self._dynamic, singleton.DELTA_TIME * 4)
        # print(static_blend, dynamic_blend)
        for _rect_comp in self._rect_aspect.iter_components():
            if _rect_comp._touching[physics_comp.TOUCHING_BOTTOM]:
                if abs(_rect_comp._velocity.x) > 50:
                    _rect_comp._velocity.x *= dynamic_blend
                    continue
                _rect_comp._velocity.x *= static_blend

# ---------------------------- #
# utils


