import pygame
import random

from engine import io
from engine import singleton

from engine.handler import aspect
from engine.handler import component

from engine.addon.components import renderable_comp

# ---------------------------- #
# constants

COMPONENT_NAME = "ParticleHandlerComponent"

PARTICLE_FUNCTION_COMBINATION = {}
DEFAULT_COMBINATION = "default"

# ---------------------------- #
# component

class ParticleHandlerComponent(renderable_comp.RenderableComponent):
    
    def __init__(self, create_func_str: str = DEFAULT_COMBINATION, update_func_str: str = DEFAULT_COMBINATION, delete_func_str: str = DEFAULT_COMBINATION, zlayer: int = None):
        """ Initialize the Particle Handler Component """
        super().__init__(zlayer=zlayer)

        self._particles = {}
        self._particle_count = 0
        self._particle_delete_queue = set()
        
        self.create_new_particle = PARTICLE_FUNCTION_COMBINATION[create_func_str][0]
        self.update_particles = PARTICLE_FUNCTION_COMBINATION[update_func_str][1]
        self.delete_particles = PARTICLE_FUNCTION_COMBINATION[delete_func_str][2]
        

    def __post_gameobject__(self, gameobject: "GameObject"):
        """ Post init function """
        super().__post_gameobject__(gameobject)

    # ---------------------------- #
    # logic

    def generate_id(self):
        """ Generate a unique ID for the particle """
        self._particle_count += 1
        return self._particle_count


# ---------------------------- #
# particle functions

def _DEFAULT_CREATE_PARTICLE(self, **kwargs):
    """ Create a particle """
    _particle_id = self.generate_id()
    _velocity = pygame.math.Vector2(random.random() * 40, 0).rotate(random.randint(0, 360))
    _time = random.random() * 4

    self._particles[_particle_id] = [_particle_id, self._parent_gameobject.position.copy(), _velocity, _time]

def _DEFAULT_UPDATE_PARTICLE(self, surface: pygame.Surface, camera: "Camera"):
    """ Update all particles """
    for _particle in self._particles.values():
        _particle[1] += _particle[2] * singleton.DELTA_TIME
        _particle[3] -= singleton.DELTA_TIME

        # render particle
        pygame.draw.circle(surface, (255, 255, 255), _particle[1] - camera.position, 2)

        if _particle[3] <= 0:
            self._particle_delete_queue.add(_particle[0])

def _DEFAULT_DELETE_PARTICLE(self):
    """ Delete a particle """
    for particle in self._particle_delete_queue:
        del self._particles[particle]
    self._particle_delete_queue.clear()

# ---------------------------- #
# aspect

class ParticleHandlerAspect(aspect.Aspect):

    def __init__(self):
        """ Initialize the Particle Handler Aspect """
        super().__init__(target_component_classes=[ParticleHandlerComponent])

        self._particles = []
    
    # ---------------------------- #
    # logic

    def handle(self, camera: "Camera"):
        """ Handle the Particle Handler Aspect """
        for _c in self.iter_components():
            _layer_surface = self._handler._world.get_layer_at(_c.zlayer)._layer_buffer
            
            _c.create_new_particle(_c)
            _c.update_particles(_c, _layer_surface, camera)
            _c.delete_particles(_c)

# ---------------------------- #
# utils

def register_particle_function_combination(name: str, create_func: "function" = None, update_func: "function" = None, delete_func: "function" = None):
    """ Register a particle function combination """
    if create_func is None:
        create_func = _DEFAULT_CREATE_PARTICLE
    if update_func is None:
        update_func = _DEFAULT_UPDATE_PARTICLE
    if delete_func is None:
        delete_func = _DEFAULT_DELETE_PARTICLE
    PARTICLE_FUNCTION_COMBINATION[name] = (create_func, update_func, delete_func)

# register default
register_particle_function_combination(DEFAULT_COMBINATION)

# caching the component class
component.ComponentHandler.cache_component_class(ParticleHandlerComponent)
