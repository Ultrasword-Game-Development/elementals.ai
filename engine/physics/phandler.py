import pygame

from engine.handler import signal


# ---------------------------- #
# constants

DEATH_SIGNAL_NAME = "_physics_death_signal"
DEATH_SIGNAL_ID = "_physics_death_signal_id"

# ---------------------------- #
# physics / entity handler

class PhysicsHandler:
    def __init__(self) -> None:
        """ Initialize the physics handler """
        self._entities = {}
        
        # death signal
        self._death_signal = signal.Signal(DEATH_SIGNAL_NAME)
        self._death_signal.add_emitter_handling_function(DEATH_SIGNAL_ID, self.handle_death_signal)
    
    def update_and_render(self, surface: pygame.Surface, offset: tuple):
        """ Update the physics handler """
        for entity in self._entities.values():
            entity.update()
            # render
            entity.render(surface, offset)
            
    def add_entity(self, entity):
        """ Add an entity to the physics handler """
        self._entities[entity] = entity
        # add death signal
        entity._death_emitter = self._death_signal.get_unique_emitter()
    
    # TODO - killing/removing entities
    def handle_death_signal(self, data: dict):
        """ 
        Handle the death signal 
        
        Data found in `data`:
        - id: int
        - data: dict (containing whatever lol)
        """
        
        self._entities[data['id']]._alive = False
        # run the custom entity death function
        self._entities[data['id']].handle_death_signal(data)
        # remove the entity
        del self._entities[data['id']]
        
        
        
    
        
            
            
            