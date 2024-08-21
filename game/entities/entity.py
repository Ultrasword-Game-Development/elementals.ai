
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
        
        self._climbing_factor = 0.7
        
        # flags
        self._can_climb = False
