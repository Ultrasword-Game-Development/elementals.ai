import pygame

from engine.handler import signal


# ---------------------------- #
# constants

DEATH_SIGNAL_NAME = "_physics_death_signal"
DEATH_SIGNAL_ID = "_physics_death_signal_id"


# ---------------------------- #
# physics / gameobject handler

class PhysicsHandler:
    def __init__(self, _world: "World") -> None:
        """ Initialize the physics handler """
        self._world = _world
        self._gameobjects = {}
        self._components = []

        # death signal
        self._death_signal = signal.Signal(DEATH_SIGNAL_NAME)
        self._death_signal.add_emitter_handling_function(DEATH_SIGNAL_ID, self.handle_death_signal)
    
    # ---------------------------- #
    # logic

    def update(self):
        """ Update the physics handler """
        # update physics world components
        for component in self._components:
            component.update() if component._active else None
        for gameobject in self._gameobjects.values():
            gameobject.update()
    
    def add_component(self, component: "PhysicsComponent"):
        """ Add an component to the physics handler """
        self._components.append(component)
        component.__post_init__(self)    
            
    def add_gameobject(self, gameobject: "GameObject"):
        """ Add an gameobject to the physics handler """
        self._gameobjects[hash(gameobject)] = gameobject
        gameobject._parent_phandler = self
        # add death signal
        gameobject._death_emitter = self._death_signal.get_unique_emitter()
        # post init
        gameobject.__post_init__()
    
    def get_gameobject(self, gameobject_hash: int):
        """ Get an gameobject by id """
        return self._gameobjects[gameobject_hash]
    
    def handle_death_signal(self, data: dict):
        """ 
        Handle the death signal 
        
        Data found in `data`:
        - id: int
        - data: dict (containing whatever lol)
        """
        
        self._gameobjects[data['id']]._alive = False
        # run the custom gameobject death function
        self._gameobjects[data['id']].handle_death_signal(data)
        # remove the gameobject
        del self._gameobjects[data['id']]
    
    def load_components(self):
        """ Load the components """
        for _gameobject in self._gameobjects.values():
            _gameobject.__post_init__()
        for _comp in self._components:
            _comp.__post_init__(self)
    
    # ---------------------------- #
    # serialize
    
    def __getstate__(self):
        """ Pickle state """
        state = self.__dict__.copy()
        return state
    
    def __setstate__(self, state):
        """ Unpickle state """
        self.__dict__.update(state)
    
        
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

def is_collision_masks_overlap(mask1: int, mask2: int):
    """ Check if two collision masks overlap """
    return mask1 & mask2 != 0
            
