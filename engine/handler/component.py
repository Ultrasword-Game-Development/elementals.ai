import pygame

from engine import singleton


# ---------------------------- #
# constants

# ---------------------------- #
# component handler

class ComponentHandler:

    COMPONENTS_CLASS_CACHE = {}

    @classmethod
    def cache_component_class(cls, _class: "Component Child Class"):
        """ Cache the component class supplied """
        cls.COMPONENTS_CLASS_CACHE[_class.__name__] = _class

    # ---------------------------- #
    
    def __init__(self, _world: "World"):
        """ Initialize the component handler """
        self._components = {}
        self._world = _world
    
    # ---------------------------- #
    # logic

    def add_component(self, _component: "Component"):
        """ Add a component to the handler """
        self._components[_component.get_component_id()] = _component
        _component._handler = self

    def get_component(self, _component_id: int):
        """ Get a component by id """
        return self._components[_component_id]

    def _remove_component(self, _component_id: int):
        """ Remove a component from the handler """
        del self._components[_component_id]
    
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
# component

class Component:
    """
    A component is a single piece of data that is attached to a gameobject.

    Components can be used to perform a SHIT TON of functions:

    - sprites
    - animation
    - ai movement
    - tiles
    - meshes

    """

    def __init__(self):
        """ The Init Function """
        self._component_id = generate_component_id()

        self._parent_gameobject = None
        self._parent_aspect = None
        self._handler = None
    
    # ---------------------------- #
    # logic

    def __post_gameobject__(self, _parent_gameobject: "GameObject"):
        """ Called after being added to a gameobject """
        self._parent_gameobject = _parent_gameobject

    def __post_aspect__(self, _parent_aspect: "Aspect"):
        """ Called after being added to an aspect """
        self._parent_aspect = _parent_aspect

    # ---------------------------- #
    # attributes

    def get_gameobject(self):
        """ Get the parent gameobject """
        return self._parent_gameobject
    
    def get_aspect(self):
        """ Get the parent aspect """
        return self._parent_aspect
    
    def get_component_id(self):
        """ Get the component id """
        return self._component_id

# ---------------------------- #
# util functions

def generate_component_id():
    """ Generate a unique ID for the component """
    singleton.COMPONENT_ID_COUNT += 1
    return singleton.COMPONENT_ID_COUNT - 1
