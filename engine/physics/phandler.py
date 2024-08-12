import pygame

from engine.handler import signal


# ---------------------------- #
# constants

DEATH_SIGNAL_NAME = "_physics_death_signal"
DEATH_SIGNAL_ID = "_physics_death_signal_id"


# ---------------------------- #
# physics / entity handler

class PhysicsHandler:
    def __init__(self, _world: "World") -> None:
        """ Initialize the physics handler """
        self._world = _world
        self._entities = {}

        # death signal
        self._death_signal = signal.Signal(DEATH_SIGNAL_NAME)
        self._death_signal.add_emitter_handling_function(DEATH_SIGNAL_ID, self.handle_death_signal)
    
    # ---------------------------- #
    # logic

    def update(self):
        """ Update the physics handler """
        for entity in self._entities.values():
            entity.update()
            self._world.get_layer_at(entity.zlayer)._entity_rendering_queue.add(entity)
            
    def add_entity(self, entity):
        """ Add an entity to the physics handler """
        self._entities[entity] = entity
        # add death signal
        entity._death_emitter = self._death_signal.get_unique_emitter()
    
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
    
    # ---------------------------- #
    # movement + collision

    def move_entity(self, entity: "Entity", world: "World"):
        """ Move the entity """
        pass
        
# ---------------------------- #
# utils

def collide_rect_to_rect(rect1: pygame.Rect, rect2: pygame.Rect):
    """ Check if two rects collide """
    return rect1.colliderect(rect2)

def collide_rect_to_bitmask(rect: pygame.Rect, bitmask: pygame.Surface, bitmask_rect: pygame.Rect):
    """ Check if a rect collides with a bitmask """
    if not rect.colliderect(bitmask_rect):
        return False
    # get the overlap
    _rect_mask = pygame.mask.Mask(rect.size, fill=True)
    return _rect_mask.overlap(bitmask, (bitmask_rect.x - rect.x, bitmask_rect.y - rect.y)) != None

def collide_bitmask_to_bitmask(bitmask1: pygame.Surface, bitmask1_rect: pygame.Rect, bitmask2: pygame.Surface, bitmask2_rect: pygame.Rect):
    """ Check if two bitmasks collide """
    if not bitmask1_rect.colliderect(bitmask2_rect):
        return False
    # get the overlap
    # TODO - bitmask + bitmask collision
    return bitmask1.overlap(bitmask2, (bitmask2_rect.x - bitmask1_rect.x, bitmask2_rect.y - bitmask1_rect.y)) != None


            
            