
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
        """
        {
            "type": [
                "image_path1", 
                "image_path2", 
                "image_path3"
            ]
        }
        """
        self._animation_types = {}
        self._default_animation_type = None
        
        # TODO - signal
        
        self.load_sprite_data_from_json()

    # ---------------------------- #
    # logic
    
    def load_sprite_data_from_json(self):
        """ Load the sprite data from the json file """
        # load the animation
        data = io.json_to_dict(self._json_path)
        # extract data
        meta = data["meta"]
        # don't use os.path.join (different between MAC and Windows)
        _framedata = data["frames"]
        _tags = meta["frameTags"]
        _image_size = meta["size"]
                
        sheet = spritesheet.load_spritesheet(self._json_path)
        
        # create all the tags first
        for taginfo in _tags:
            self._animation_types[taginfo["name"]] = []
        
        # add all the images from framedata
        for frameinfo in _framedata:
            name = frameinfo["filename"]
            _, _ani_type, _index_and = name.split("-")
            self._animation_types[_ani_type].append(name)
        
        # set the default animation type - the first animation
        self._default_animation_type = _tags[0]["name"]

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
        self._spritesheet = spritesheet.load_spritesheet(self._json_path)
        self._animation_types = {}
        # register the animation
        self.load_sprite_data_from_json()
        cache_animation(self)
    


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
        return io.load_image(self._parent[self._animation_type][self._frame])
    
    @property
    def sprite_path(self):
        """ Return the current frame path """
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
        self._parent = load_animation_from_json(self._parent_hash)


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
    
    # cache animation
    ANI_CACHE[json_path] = animation
        
    return animation


