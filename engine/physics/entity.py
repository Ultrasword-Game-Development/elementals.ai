import pygame


# ---------------------------- #
# constants

ENTITY_COUNTER = 0

# ---------------------------- #

class Entity:
    def __init__(self):
        """ Create a new entity """
        self._id = create_entity_id()
        self.position = pygame.math.Vector2()
        self.zlayer = 0
        self.velocity = pygame.math.Vector2()
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.sprite = None
        self.bitmask = None
        # bit collision mask
        self.layer_mask = 0b00000000
        
        # for the physics/entity handler
        self._alive = True
        self._death_emitter = None

    def update(self):
        """ Update the entity """
        pass

    def render(self, surface: pygame.Surface, offset: tuple):
        """ Render the entity """
        if self.sprite:
            surface.blit(self.sprite, self.position - offset)
    
    def handle_death_signal(self, data: dict):
        """ Death function -- to be overriden """
        # self._alive should be set to false
        pass

    # ---------------------------- #
    # utils

    def __hash__(self):
        """ Hash the entity """
        return self._id

    # ---------------------------- #
    # dill pickle

    def __getstate__(self):
        """ Pickle state """
        state = self.__dict__.copy()
        # remove unpicklable entries
        del state['sprite']
        return state

    def __setstate__(self, state):
        """ Unpickle state """
        self.__dict__.update(state)
        # restore unpicklable entries
        self.sprite = pygame.Surface((0,0)).convert_alpha()



# ---------------------------- #
# functions

def create_entity_id():
    """ Create a new entity id """
    global ENTITY_COUNTER
    ENTITY_COUNTER += 1
    return ENTITY_COUNTER
