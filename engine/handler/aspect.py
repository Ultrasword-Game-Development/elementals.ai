


# ---------------------------- #
# constants

ASPECT_CACHE = {}

# ---------------------------- #
# aspect handler

class AspectHandler:
    """

    """

    def __init__(self, _world: "World"):
        """ Initialize the Aspect Handler class """
        self._aspect = []
        self._world = _world
    
    # ---------------------------- #
    # logic

    def handle(self):
        """ Handle all the aspects """
        for aspect in self._aspect:
            aspect.handle()

    def add_aspect(self, aspect: "Aspect"):
        """ Add an aspect to the handler """
        # check if a copy already exists
        for _aspect in self._aspect:
            if _aspect.__class__.__name__ == aspect.__class__.__name__:
                # TODO - log it
                return
        # add aspect
        self._aspect.append(aspect)
        # sort the array
        self._aspect.sort(key = lambda x: x._priority)
    
    def remove_aspect(self, aspect: "Aspect"):
        """ Remove an aspect from the handler """
        self._aspect.remove(aspect)
    
    def remove_aspect_by_str(self, _aspect_class: str):
        """ Remove an aspect by string """
        for aspect in self._aspect:
            if aspect.__class__.__name__ == _aspect_class:
                self._aspect.remove(aspect)
                break
    
    # component logic
    
    def register_component(self, component: "Component"):
        """ Register a component """
        for aspect in self._aspect:
            aspect.register_component(component)
    
    def _remove_component(self, component: "Component"):
        """ Remove a component """
        for aspect in self._aspect:
            aspect._remove_component(component)
    
    def _remove_component_by_id(self, component_id: int):
        """ Remove a component by id """
        for aspect in self._aspect:
            if component_id in aspect._components:
                aspect._remove_component_by_id(component_id)
                break
    

# ---------------------------- #
# aspect

class Aspect:
    """
    An aspect acts as a category for the components in the ECS system.

    Aspects perform these functions:

    - Update the components in the aspect
    - Store the components that belong to the aspect
    - Serialize all components when saving the game

    They are 'component handlers'
    """

    def __init__(self, priority: int = 0):
        """ The Init Function """
        self._component_ids = set()
        self._priority = 0
    
    # ---------------------------- #
    # logic

    def handle(self):
        """ Handle the aspect """
        pass
    
    def register_component(self, component: "Component"):
        """ Register a component """
        self._components.add(component.get_component_id())
        component.__post_aspect__(self)
    
    def _remove_component(self, component: "Component"):
        """ Remove a component """
        if component.get_component_id() in self._components:
            self._components.remove(component.get_component_id())
    
    def _remove_component_by_id(self, component_id: int):
        """ Remove a component by id """
        if component_id in self._component_ids:
            self._components.remove(component_id)
    
    # ---------------------------- #
    # utils

    def iter_components(self):
        """ Iterate through the components """
        for component in self._components_id:
            yield component

# ---------------------------- #
# util functions


