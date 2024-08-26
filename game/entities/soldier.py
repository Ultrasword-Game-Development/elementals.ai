
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
ATTACK3_ANIM = "Attack03"
HURT_ANIM = "Hurt"
DEATH_ANIM = "Death"

# ---------------------------- #
# player

class Soldier(entity.Entity):
    
    def __init__(self, x: int, y: int):
        super().__init__(x=x, y=y)
        
        # add components
        self._animation_comp = self.add_component(components.animation_comp.AnimationComponent("assets/sprites/entities/soldier.json"))
        self._player_comp = self.add_component(player_comp.PlayerComponent())
        self._camera_comp = self.add_component(components.cameracontrol_comp.CameraControlComponent())
        
        components.particlehandler_comp.register_particle_function_combination("playertest", create_func=_DEFAULT_CREATE_PARTICLE, update_func=_DEFAULT_UPDATE_PARTICLE)
        self.add_component(components.particlehandler_comp.ParticleHandlerComponent(create_func_str="playertest" ,update_func_str="playertest", zlayer=-2))
        
        # set up hitbox
        self._hitbox_comp.set_offset((-4, -7))
        self._hitbox_comp.set_area((10, 18))
                
        # set up animation
        self._animation_comp.set_animation_type("Idle")
        
    def __post_init__(self):
        """ Post init function """
        super().__post_init__()

        self._agility = 350
            
        
# testing
def _DEFAULT_CREATE_PARTICLE(self, **kwargs):
    """ Create a particle """
    for i in range(3):
        _particle_id = self.generate_id()
        _velocity = pygame.math.Vector2(random.random() * 40, 0).rotate(random.randint(0, 360))
        _time = random.random() * 4
        _length = random.randint(1, 10)
        _angle = random.randint(0, 360)
        _angular_velocity = random.random() * 30 + 30

        self._particles[_particle_id] = [
            _particle_id, # 0
            self._parent_gameobject.position.copy(), # 1
            _velocity, # 2
            _time, # 3
            _length, # 4
            _angle,# 5
            _angular_velocity # 6
        ]


def _DEFAULT_UPDATE_PARTICLE(self, surface: pygame.Surface, camera: "Camera"):
    """ Update all particles """
    for _particle in self._particles.values():
        _particle[1] += _particle[2] * singleton.DELTA_TIME
        _particle[3] -= singleton.DELTA_TIME
        _particle[5] += _particle[6] * singleton.DELTA_TIME

        _vec = pygame.math.Vector2(0, 1).rotate(_particle[5]) 
        startpoint = _particle[1] - _vec * _particle[4] - camera.position
        endpoint = _particle[1] + _vec * _particle[4] - camera.position

        _pos = _particle[1] - camera.position
        # render particle
        _color = (
            math.sin(_pos.x / 100) * 127 + 127, 
            math.cos(_pos.y / 80) * 127 + 127, 
            math.sin(singleton.ACTIVE_TIME) * 127 + 127,
            100
        )
        # pygame.draw.circle(surface, (
            # _color,
            # _pos, 
            # 2
        # )
        pygame.draw.line(surface, _color, startpoint, endpoint, 2)
        

        if _particle[3] <= 0:
            self._particle_delete_queue.add(_particle[0])



