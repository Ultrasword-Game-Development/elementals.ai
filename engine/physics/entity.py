import pygame


# ---------------------------- #
#



# ---------------------------- #

class Entity:
    def __init__(self):
        """ Create a new entity """
        self.position = pygame.math.Vector2()
        self.velocity = pygame.math.Vector2()
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.sprite = None
        self.bitmask = None

    def update(self):
        """ Update the entity """
        pass

    def render(self, surface: pygame.Surface):
        """ Render the entity """
        if self.sprite:
            surface.blit(self.sprite, self.position)

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


