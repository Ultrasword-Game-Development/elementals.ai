
import pygame

from engine.handler import aspect
from engine.handler import component

# ---------------------------- #
# constants

COMPONENT_NAME = "StateMachineComponent"

# ---------------------------- #
# component

class StateMachineComponent(component.Component):
    
    def __init__(self):
        """ Initialize the renderable component """
        super().__init__()

        self._states = {}
        self._next_state: str = None
        self._current_state: str = None

    # ---------------------------- #
    # logic

    def set_next_state(self, name: str):
        """ Set the next state """
        self._next_state = self.get_state(name)

    def set_current_state(self, name: str):
        """ Set the current state """
        self._current_state = self.get_state(name)
    
    def get_current_state(self) -> "State":
        """ Get the current state """
        return self._current_state

    def add_state(self, state: "State"):
        """ Add a state to the state machine """
        self._states[state.get_name()] = state
    
    def get_state(self, name: str) -> "State":
        """ Get a state by name """
        return self._states.get(name, None)
    
    def remove_state(self, name: str):
        """ Remove a state by name """
        return self._states.pop(name, None)
    


class State:
    def __init__(self, name: str):
        self._name = name
        self._statemachine = None
    
    def __post_init__(self, statemachine: "StateMachineComponent"):
        self._statemachine = statemachine
    
    # ---------------------------- #
    # logic

    def update(self, surface: pygame.Surface, camera: "Camera"):
        """ Update the state """
        pass

    # ---------------------------- #
    # utils

    def get_name(self) -> str:
        return self._name
    
    def get_statemachine(self) -> "StateMachineComponent":
        return self._statemachine


# ---------------------------- #
# aspect

class StateMachineAspect(aspect.Aspect):
    def __init__(self):
        super().__init__(target_component_classes=[StateMachineComponent])  

    # ---------------------------- #
    # logic

    def handle(self, camera: "Camera"):
        """ Handle the aspect """
        for _statemachinecomp in self.iter_components():
            if not _statemachinecomp.get_current_state():
                continue

            if _statemachinecomp._next_state != None:
                _statemachinecomp.set_current_state(_statemachinecomp._next_state)
                _statemachinecomp._next_state = None

            # update state machine
            _statemachinecomp.get_current_state().update(self._handler._world.get_layer_at(_rect_comp.get_gameobject().zlayer)._layer_buffer, camera)


# ---------------------------- #
# utils



# caching the component class
component.ComponentHandler.cache_component_class(RenderableComponent)
