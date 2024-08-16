import pygame

from engine import io
from engine import singleton


# ---------------------------- #
# constants


# ---------------------------- #

class GameObject:
    def __init__(
            self, 
            position: tuple = (0, 0), 
            area: tuple = (0, 0), 
            zlayer: int = 0, 
            parent: "Physics Handler" = None, 
        ):
        """ Create a new GameObject """
        self._id = create_gameobject_id()
        
        self.position = pygame.math.Vector2(position)
        self.zlayer = 0

        # gameobject component system
        self._components = []
        
        # for the physics/gameobject handler
        self._alive = True
        self._death_emitter = None
        self._parent_phandler = parent

    # ---------------------------- #
    # logic

    def update(self):
        """ Update the gameobject """
        pass
    
    def handle_death_signal(self, data: dict):
        """ Death function -- to be overriden """
        # self._alive should already be set to false
        for _comp in self._components:
            self.remove_component(self._parent_phandler._world._component_handler.get_component(_comp))
            # remove from handler
            self._parent_phandler._world._component_handler.remove_component(_comp)
            # remove from aspect handler
            self._parent_phandler._world._aspect_handler._remove_component_by_id(_comp)

    def add_component(self, component: "Component"):
        """ Add a component to the gameobject """
        # add component to component handler + aspect handler
        self._parent_phandler._world._component_handler.add_component(component)
        self._parent_phandler._world._aspect_handler.register_component(component)
        # add to self
        self._components.append(component)
        # run post_init script
        component.__post_gameobject__(self)
        # return the component
        return component
    
    def get_component(self, component_name: list):
        """ Get a component by name """
        for _comp in self._components:
            if _comp.__class__.__name__ in component_name:
                return _comp
        return None

    def remove_component(self, component: "Component"):
        """ Remove a component from the gameobject """
        # remove component from component handler + aspect handler
        self._parent_phandler._world._component_handler._remove_component(component)
        self._parent_phandler._world._aspect_handler._remove_component(component)
        # remove from self
        self._components.remove(component)

    # ---------------------------- #
    # utils

    def set_position(self, x, y):
        """ Set the position """
        self.position.xy = x, y
        self.rect.topleft = x, y
    
    def kill(self):
        """ Kill the gameobject """
        self._alive = False
        self._death_emitter.emit({'id': self._id})

    def __hash__(self):
        """ Hash the gameobject """
        return self._id

    # ---------------------------- #
    # dill pickle

    def __getstate__(self):
        """ Pickle state """
        state = self.__dict__.copy()
        # remove unpicklable entries
        del state['sprite']
        del state['mask']
        return state

    def __setstate__(self, state):
        """ Unpickle state """
        self.__dict__.update(state)
        # restore unpicklable entries
        self.sprite = pygame.Surface((0,0)).convert_alpha()


# ---------------------------- #
# functions

def create_gameobject_id():
    """ Create a new gameobject id """
    singleton.GAMEOBJECT_ID_COUNT += 1
    return singleton.GAMEOBJECT_ID_COUNT - 1
