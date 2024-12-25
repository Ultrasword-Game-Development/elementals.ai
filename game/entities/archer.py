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


RESULT_LEFT = 0
RESULT_UP = 1
RESULT_RIGHT = 2
RESULT_DOWN = 3
RESULT_JUMP = 4
RESULT_ATTACK = 5
RESULT_SHIFT = 6

LIMIT = 0.7


# ---------------------------- #
# player


class Archer(entity.Entity):

    def __init__(self, x: int, y: int):
        super().__init__(x=x, y=y)

        # add components
        self._animation_comp = self.add_component(
            components.animation_comp.AnimationComponent(
                "assets/sprites/entities/archer.json"
            )
        )
        self._player_comp = self.add_component(player_comp.PlayerComponent(inputs_config={
            "a": pygame.K_LEFT,
            "d": pygame.K_RIGHT,
            "w": pygame.K_UP,
            "s": pygame.K_DOWN,
            "space": pygame.K_SPACE,
            "lshift": pygame.K_LSHIFT
        }))
        self._rect_comp = self.get_component(components.rect_comp.COMPONENT_NAME)
        # add the states
        self._state_machine = self.add_component(
            components.statemachine_comp.StateMachineComponent()
        )

        self._rays = [self.add_component(components.ray2d_comp.Ray2DComponent((0, 0), 100, i, zlayer=0, tilecast=True, entitycast=True)) for i in range(-90, -90 + 361, 45)]

        # set up hitbox
        self._hitbox_comp.set_offset((-4, -7))
        self._hitbox_comp.set_area((10, 18))

        # set up animation
        self._animation_comp.set_animation_type("Idle")

    def __post_init__(self):
        """Post init function"""
        super().__post_init__()

        self._agility = 500

    # ---------------------------- #
    # logic

    def activate_attack(self, attack: str):
        """Activate attack"""
        pass


# ---------------------------- #
# utils
