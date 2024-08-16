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

PARTICLE_CREATION_STAGE = "particle_creation_stage"
PARTICLE_UPDATE_STAGE = "particle_update_stage"
PARTICLE_DELETE_STAGE = "particle_delete_stage"

PARTICLE_FUNCTION_COMBINATION = {}

# ---------------------------- #
# component

class ParticleHandlerComponent(renderable_comp.RenderableComponent):
    
    def __init__(self):
        """ Initialize the Particle Handler Component """
        super().__init__()

        self._particles = {}
        self._particle_count = 0
        self._particle_delete_queue = set()

    def __post_gameobject__(self, gameobject: "GameObject"):
        """ Post init function """
        super().__post_gameobject__(gameobject)

    # ---------------------------- #
    # logic

    def generate_id(self):
        """ Generate a unique ID for the particle """
        self._particle_count += 1
        return self._particle_count

    def create_new_particle(self, **kwargs):
        """ Create a particle """
        _particle_id = self.generate_id()
        _velocity = pygame.math.Vector2(random.random() * 40, 0).rotate(random.randint(0, 360))
        _time = random.random() * 4

        self._particles[_particle_id] = [_particle_id, self._parent_gameobject.position.copy(), _velocity, _time]

    def update_particles(self, surface: pygame.Surface):
        """ Update all particles """
        for _particle in self._particles.values():
            _particle[1] += _particle[2] * singleton.DELTA_TIME
            _particle[3] -= singleton.DELTA_TIME

            # render particle
            pygame.draw.circle(surface, (255, 255, 255), _particle[1] - self._handler._world._camera.position, 2)

            if _particle[3] <= 0:
                self._particle_delete_queue.add(_particle[0])
    
    def delete_particles(self):
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

    def handle(self):
        """ Handle the Particle Handler Aspect """
        for _c in self.iter_components():
            _c.create_new_particle()
            _c.update_particles(self._handler._world.get_layer_at(_c._parent_gameobject.zlayer)._layer_buffer)
            _c.delete_particles()

# ---------------------------- #
# utils



# caching the component class
component.ComponentHandler.cache_component_class(ParticleHandlerComponent)
