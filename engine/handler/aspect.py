


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
        self._aspects = []
        self._world = _world
        self._aspect_targets: {"Component Class": ["Aspect Instance"]} = {}
    
        self._component_backlog = []
    
    def __post_init__(self):
        """ Post init function """
        for aspect in self._aspects:
            aspect.__post_init__()

            print(aspect)

    # ---------------------------- #
    # logic

    def handle(self, camera: "Camera"):
        """ Handle all the aspects """
        for aspect in self._aspects:
            aspect.handle(camera)

    def add_aspect(self, aspect: "Aspect"):
        """ Add an aspect to the handler """
        # check if a copy already exists
        for _aspect in self._aspects:
            if _aspect.__class__.__name__ == aspect.__class__.__name__:
                # TODO - log it
                return
        # add aspect
        self._aspects.append(aspect)
        aspect._handler = self
        # sort the array - BIGGEST PRIORITY FIRST
        self._aspects.sort(key = lambda x: -x._priority)
        # add targetted component classes
        for _class in aspect._target_component_classes:
            if _class.__name__ not in self._aspect_targets:
                self._aspect_targets[_class.__name__] = []
            if aspect not in self._aspect_targets[_class.__name__]:
                self._aspect_targets[_class.__name__].append(aspect)
        
        print("ADDING:", aspect)
        aspect.__post_init__()
    
    def get_aspect(self, _aspect_class: "Aspect Class"):
        """ Get an aspect by string """
        for aspect in self._aspects:
            if aspect.__class__.__name__ == _aspect_class.__name__:
                return aspect
        return None
    
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
        component.__post_aspect__(self)
        # register component into aspect instances
        if component.__class__.__name__ not in self._aspect_targets:
            self._component_backlog.append(component)
            return
        
        for aspect in self._aspect_targets[component.__class__.__name__]:
            aspect.register_component(component)
        
        # update backlog of components
        if not self._component_backlog:
            return
        index = 0
        while index < len(self._component_backlog):
            _comp = self._component_backlog[index]
            if _comp.__class__.__name__ in self._aspect_targets:
                for aspect in self._aspect_targets[_comp.__class__.__name__]:
                    aspect.register_component(_comp)
                self._component_backlog.pop(index)
            else:
                index += 1

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

    def __init__(self, priority: int = 0, target_component_classes: list = []):
        """ The Init Function """
        self._components = {}
        self._priority = priority
        self._handler = None
        self._target_component_classes = target_component_classes
    
    def __post_init__(self):
        """ Post init function """
        pass
    
    # ---------------------------- #
    # logic

    def handle(self, camera: "Camera"):
        """ Handle the aspect """
        pass
    
    def register_component(self, component: "Component"):
        """ Register a component """
        self._components[component.get_component_id()] = component
        component.__post_aspect__(self)
    
    def _remove_component(self, component: "Component"):
        """ Remove a component """
        if component.get_component_id() in self._components:
            self._remove_component_by_id(component.get_component_id())
    
    def _remove_component_by_id(self, component_id: int):
        """ Remove a component by id """
        if component_id in self._components:
            del self._components[component_id]
    
    # ---------------------------- #
    # utils

    def iter_components(self):
        """ Iterate through the components """
        for component in self._components:
            yield self._components[component]
    
    def iter_target_component_classes(self):
        """ Iterate through the target component classes """
        # idk why anyone would use this
        for _class in self._target_component_classes:
            yield _class

# ---------------------------- #
# util functions


