
import math
import pygame
import random


from engine import io
from engine import singleton

from engine.physics import gameobject

from engine.addon import components


# ---------------------------- #
# constants


# ---------------------------- #
# player

class Entity(gameobject.GameObject):
    
    def __init__(self, x: int, y: int):
        super().__init__(position=(x, y))
        
        self._health = 100
        self._mana = 100
        self._agility = 20
        self._resistance = 10
        self._magic_resistance = 10
        
        self._climbing_factor = 0.8
        
        # flags
        self._can_climb = False

        # add components
        self._sprite_comp = self.add_component(components.sprite_comp.SpriteComponent())
        self._hitbox_comp = self.add_component(components.hitbox_comp.HitBoxComponent())
        self._rect_comp = self.add_component(components.rect_comp.WorldRectComponent())
    
        self.add_component(components.spriterenderer_comp.SpriteRendererComponent())

    # ---------------------------- #
    # logic

    def move(self, x: float, y: float):
        """ Move the entity """
        self.position += (x, y)
        self._rect_comp._rect.center = self.position
