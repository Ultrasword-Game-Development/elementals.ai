
import math
import pygame
import random


from engine import io
from engine import singleton

from engine.physics import gameobject

from engine.addon import components

from game.entities import entity
from game.components import player_comp

from game import singleton as game_singleton


# ---------------------------- #
# constants

IDLE_ANIM = "Idle"
WALK_ANIM = "Walk"
ATTACK1_ANIM = "Attack01"
ATTACK2_ANIM = "Attack02"
HURT_ANIM = "Hurt"
DEATH_ANIM = "Death"

# ---------------------------- #
# player

class Archer(entity.Entity):
    
    def __init__(self, x: int, y: int):
        super().__init__(x=x, y=y)
        
        # add components
        self._animation_comp = self.add_component(components.animation_comp.AnimationComponent("assets/sprites/entities/archer.json"))
        self._player_comp = self.add_component(player_comp.PlayerComponent(_main_player=False))
                
        # set up hitbox
        self._hitbox_comp.set_offset((-4, -7))
        self._hitbox_comp.set_area((10, 18))
                
        # set up animation
        self._animation_comp.set_animation_type("Idle")
        
    def __post_init__(self):
        """ Post init function """
        super().__post_init__()

        self._agility = 500
    
    # ---------------------------- #
    # logic

    def activate_attack(self, attack: str):
        """ Activate attack """
        pass
            
