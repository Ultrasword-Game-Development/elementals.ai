
import os
import json
import pygame

from engine import io
from engine import singleton

from engine.graphics import spritesheet

# ---------------------------- #
# constants

ANI_CACHE = {}


# ---------------------------- #
# animation handler

class Animation:

    def __init__(self, json_path: str, spritesheet: spritesheet.SpriteSheet):
        """ Create a new animation """
        self._json_path = json_path
        self._spritesheet = spritesheet
                
        # handle all the types of animations within an animation
        # including frame limits + etc
        self._animation_types = {}
        self._default_animation_type = None
        
        # TODO - signal

    def get_registry(self):
        """ Return the animation registry """
        result = AnimationRegistry(self)
        result._animation_type = self._default_animation_type
        return result

    # ---------------------------- #

    def __getitem__(self, key: str):
        """ Get the frame at the given index """
        return self._animation_types[key]
    
    def __hash__(self):
        """ Return the hash of the animation """
        return hash(self._spritesheet)
    
    def __len__(self):
        """ Return the length of the animation """
        return len(self._frames)
    
    def __iter__(self):
        """ Return the animation iterator """
        return iter(self._frames)
    
    # ---------------------------- #
    # pickle

    def __getstate__(self):
        """ Pickle state """
        state = self.__dict__.copy()
        # remove unpicklable entries
        del state['_animation_types']
        del state['_spritesheet']
        return state
    
    def __setstate__(self, state):
        """ Unpickle state """
        self.__dict__.update(state)
        # restore unpicklable entries
        self._spritesheet = spritesheet.SpriteSheet(self._json_path)
        self._animation_types = {}
        # register the animation
        Animation.load_sprite_data_from_json(self._json_path, self)
        cache_animation(self)
    
    # ---------------------------- #
    # classmethod
    
    @classmethod
    def load_sprite_data_from_json(cls, json_path: str, animation: "Animation"):
        # load the animation
        data = io.json_to_dict(json_path)
        # extract data
        meta = data["meta"]
        # don't use os.path.join (different between MAC and Windows)
        _layers = meta["layers"]
        _framedata = data["frames"]
        _sprite_size = (_framedata[0]["frame"]["w"], _framedata[0]["frame"]["h"])
        _size = meta["size"]
        
        sprites_per_row = _size['w'] // _sprite_size[0]
        
        sheet = spritesheet.load_spritesheet(json_path)
        
        # create all animation_types (layers of the aseprite file)
        for l_id, layer in enumerate(_layers):
            _name = layer["name"]
            print(layer, sprites_per_row * l_id)
            animation._animation_types[_name] = [
                # get all sprites from spritesheet on this layer 
                sheet[sprites_per_row * l_id + __sid] for __sid in range(sprites_per_row)
            ]
        
        # set the default animation type
        animation._default_animation_type = _layers[0]["name"]


# ---------------------------- #
# animation registry

class AnimationRegistry:
    """
    Should not be pickle-able
    """
    def __init__(self, parent: Animation):
        """ Create a new animation registry """
        self._parent = parent
        self._parent_hash = parent._json_path
        self._frame = 0
        self._time = 0
        self._animation_type = None
    
    # ---------------------------- #
    # logic
    
    def update(self):
        """ Update the animation """
        self._time += singleton.DELTA_TIME
        if self._time > singleton.ANIMATION_DELTA:
            self._time = 0
            self._frame += 1
            if self._frame >= len(self._parent[self._animation_type]):
                self._frame = 0
    
    def reset(self):
        """ Reset the animation """
        self._frame = 0
        self._time = 0

    @property
    def sprite(self):
        """ Return the current frame """
        return self._parent[self._animation_type][self._frame]
    
    # ---------------------------- #
    # utils
    
    def get_all_animation_types(self) -> list:
        """ Return all the animation types """
        return list(self._parent._animation_types.keys())
    
    # ---------------------------- #
    # pickle

    def __getstate__(self):
        """ Pickle state """
        state = self.__dict__.copy()
        # remove unpicklable entries
        del state['_parent']
        return state

    def __setstate__(self, state):
        """ Unpickle state """
        self.__dict__.update(state)
        # restore unpicklable entries
        self._parent = ANI_CACHE[state['_parent_hash']]



# ---------------------------- #
# functions


def cache_animation(animation: Animation):
    """ Cache the animation """
    ANI_CACHE[animation._json_path] = animation


def load_animation_from_json(json_path: str):
    """ Load an animation from a spritesheet given the image path"""
    # check if the animation is already loaded
    if json_path in ANI_CACHE:
        return ANI_CACHE[json_path]
        
    # create the spritesheet
    sheet = spritesheet.load_spritesheet(json_path)
    
    # create the animation
    animation = Animation(json_path, sheet)
    Animation.load_sprite_data_from_json(json_path, animation)
    
    # cache animation
    ANI_CACHE[json_path] = animation
        
    return animation


