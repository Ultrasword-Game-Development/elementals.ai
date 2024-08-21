
import pygame

from engine import singleton

from engine.handler import world
from engine.handler import signal

from engine.graphics import animation
from engine.graphics import spritesheet


# ---------------------------- #
# constants

SYNCED_TILE_ANIMATION = "_synced_tile_animation"

# ---------------------------- #
# animated - semi-dynamic tiles (across the entire world)

class SemiAnimatedTile(world.DefaultTile):
    
    def __init__(self, position: tuple, sprite: str) -> None:
        self.__parent_class__ = self.__class__

        super().__init__(position, sprite)
        self._animation_json_path = sprite
        self._animation_registry = None
        self._signal_function_registry_key = sprite + "||" + SYNCED_TILE_ANIMATION
        
        # grab the animation and stick a default image into the sprite object
        ani = animation.load_animation_from_json(sprite)
        self._sprite_path = None
        
    # ---------------------------- #
    # logic
    
    def __post_init__(self, chunk: "world.Chunk"):
        """ Post init """
        # check if the animation registry has already been added to the signal function call cache
        if not signal.get_signal(singleton.GLOBAL_FRAME_SIGNAL_KEY).has_registered_function_key(self._signal_function_registry_key):
            # add the animation registry to the signal function call cache
            signal.get_signal(singleton.GLOBAL_FRAME_SIGNAL_KEY).add_emitter_handling_function(
                self._signal_function_registry_key,
                update_synced_sprite_animations, 
                registry = animation.load_animation_from_json(self._animation_json_path).get_registry()
            )
        
        # set animation registry
        self._animation_registry = signal.get_signal(singleton.GLOBAL_FRAME_SIGNAL_KEY).get_registered_function_info(self._signal_function_registry_key)[1]["registry"]
        self._animation_registry.compile_layers = True
        # cache all animation registry sprites - into local spritecacher
        # loop through types
        for _a_type in self._animation_registry._parent._animation_types:
            # loop through image paths
            for _layer in self._animation_registry._parent[_a_type]:
                for _sid in self._animation_registry._parent[_a_type][_layer]:
                    _config = self._animation_registry._parent._spritesheet.get_config()
                    # load the sprite
                    chunk._sprite_cacher.load_sprite(_sid)
        
        # set sprite_path
        self._sprite_path = self._animation_registry.sprite_path
                
    def update(self):
        """ Update the tile """
        self._sprite_path = self._animation_registry.sprite_path
    
    # ---------------------------- #
    # serialization
    
    def __getstate__(self):
        """ Get state """
        state = super().__getstate__()
        return state

    def __setstate__(self, state):
        """ Set state """
        super().__setstate__(state)


def update_synced_sprite_animations(data: dict, **kwargs):
    """ Update the synced sprite animations """
    kwargs['registry'].update()


# ---------------------------- #
# animated - dynamic tiles

class AnimatedTile(world.DefaultTile):
    def __init__(self, position: tuple, sprite: str, offset: int = 0) -> None:
        self.__parent_class__ = self.__class__
        
        super().__init__(position, sprite)
        self._animation_json_path = sprite
        self._animation_registry = None
        
        # load animation registry
        ani = animation.load_animation_from_json(self._animation_json_path)
        self._animation_registry = ani.get_registry()
        self._animation_registry.compile_layers = True
        self._sprite_path = None
        
        # set offset frame
        self._animation_registry._frame += offset
    
    # ---------------------------- #
    # logic

    def __post_init__(self, chunk: "world.Chunk"):
        """ Post init """
        # cache all animation registry sprites
        for _a_type in self._animation_registry._parent._animation_types:
            for _layer in self._animation_registry._parent[_a_type]:
                for _sid in self._animation_registry._parent[_a_type][_layer]:
                    _config = self._animation_registry._parent._spritesheet.get_config()
                    chunk._sprite_cacher.load_sprite(_sid)
        
        # set sprite_path
        self._sprite_path = self._animation_registry.sprite_path
        
    def update(self):
        """ Update the tile """
        self._animation_registry.update()
        self._sprite_path = self._animation_registry.sprite_path
    
    # ---------------------------- #
    # serialization
    
    def __getstate__(self):
        """ Get state """
        state = super().__getstate__()
        return state
    
    def __setstate__(self, state):
        """ Set state """
        super().__setstate__(state)
        # update all sprites
        
    

