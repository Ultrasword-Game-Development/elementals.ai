
import pygame

from engine import io

from engine.handler import component
from engine.handler import aspect

from engine.addon.components import renderable_comp

# ---------------------------- #
# constants

COMPONENT_NAME = "SpriteComponent"


# ---------------------------- #
# component

class SpriteComponent(renderable_comp.RenderableComponent):
    
    def __init__(self, sprite_str: str = None, scale_area: float = 1, has_mask: bool = False):
        super().__init__()

        self._sprite_str = sprite_str
        self._sprite_rect = pygame.Rect(0, 0, 0, 0)

        self._scale_area = scale_area
        self._flipx = False
        self._flipy = False

        self._sprite_changed = True
        self._sprite = None

    def __post_gameobject__(self, gameobject: "GameObject"):
        """ Post init function """
        super().__post_aspect__(gameobject)
        
        if self._sprite_str:
            self.set_sprite_str(self._sprite_str)

    # ---------------------------- #
    # logic

    def get_sprite_str(self):
        """ Get the sprite string """
        return self._sprite_str
    
    def set_sprite_str(self, sprite_str: str):
        """ Set the sprite string """
        self._sprite_str = sprite_str
        self._sprite_rect = io.load_image(sprite_str).get_rect()
        self._sprite_rect.size = (
            self._sprite_rect.width * self._scale_area,
            self._sprite_rect.height * self._scale_area
        )
        self._sprite_changed = True
    
    def get_scale_area(self):
        """ Get the scale area """
        return self._scale_area
    
    def set_scale_area(self, scale_area: float):
        """ Set the scale area """
        self._scale_area = scale_area
        self._sprite_changed = True
    
    def get_flipx(self):
        """ Get the flip """
        return self._flipx

    def set_flipx(self, flipx: bool):
        """ Set the flip """
        self._flip = flipx
        self._sprite_changed = True
    
    def get_flipy(self):
        """ Get the flip """
        return self._flipy
    
    def set_flipy(self, flipy: bool):
        """ Set the flip """
        self._flipy = flipy
        self._sprite_changed = True
    
    def get_sprite(self):
        """ Get the sprite """
        if self._sprite_changed:
            self._sprite = io.load_image(self._sprite_str)
            self._sprite = pygame.transform.flip(self._sprite, self._flipx, self._flipy)
            self._sprite = pygame.transform.scale(
                self._sprite, 
                (
                    int(self._sprite_rect.width), 
                    int(self._sprite_rect.height)
                )
            )

        return self._sprite

    # ---------------------------- #
    # serialize
    
    def __getstate__(self):
        """ Pickle state """
        state = self.__dict__.copy()
        del state['_sprite']
        return state
    
    def __setstate__(self, state):
        """ Unpickle state """
        self.__dict__.update(state)
        self._sprite = None
        self._sprite_changed = True

# ---------------------------- #
# aspect


# ---------------------------- #
# utils




# caching the component class
component.ComponentHandler.cache_component_class(SpriteComponent)
