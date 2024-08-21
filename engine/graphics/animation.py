
import os
import json
import pygame

from engine import io
from engine import singleton

from engine.graphics import spritesheet

# ---------------------------- #
# constants

ANI_CACHE = {}

NAME_CONSTANT = '[n]'
LAYER_CONSTANT = '[l]'
TAG_CONSTANT = '[t]'
FRAME_CONSTANT = '[f]'

DEFAULT_LAYER = "default"


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
        self._layers = []
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
        _layers = meta["layers"]
        _image_size = meta["size"]
                
        sheet = spritesheet.load_spritesheet(self._json_path)
        
        # create all the tags first
        for taginfo in _tags:
            if len(_layers) > 0:
                self._animation_types[taginfo["name"]] = {
                    _lname["name"] : [] for _lname in _layers
                }
            else:
                self._animation_types[taginfo["name"]] = {
                    DEFAULT_LAYER : []
                }
        
        # add all the images from framedata
        for frameinfo in _framedata:
            _name = frameinfo["filename"]
            _namedata = sorted(frameinfo["filename"].split('.')[0].split('-'))
            
            _frame = _namedata[0][3:]
            _layer = _namedata[1][3:] if len(_namedata[1][3:]) != 0 else DEFAULT_LAYER
            _ani_name = _namedata[2][3:]
            _ani_type = _namedata[3][3:]

            self._animation_types[_ani_type][_layer].append(_name)
        
        # set the default animation type - the first animation
        self._layers = [l['name'] for l in _layers]
        self._default_animation_type = _tags[0]["name"]

    def get_default_animation_type(self):
        """ Return the default animation type """
        return self._default_animation_type

    def get_default_animation_layer(self):
        """ Return the default animation layer """
        return self._layers[0]

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
        self._animation_type = self._parent.get_default_animation_type()
        self._layer = self._parent.get_default_animation_layer()
        self._compile_layers = True
    
    # ---------------------------- #
    # logic
    
    def update(self):
        """ Update the animation """
        self._time += singleton.DELTA_TIME
        if self._time > singleton.ANIMATION_DELTA:
            self._time = 0
            self._frame += 1
            if self._frame >= len(self._parent[self._animation_type][self._layer]):
                self._frame = 0
            
    def reset(self):
        """ Reset the animation """
        self._frame = 0
        self._time = 0

    @property
    def sprite(self):
        """ Return the current frame """
        if not self._compile_layers and self._layer != None:        
            return io.load_image(self._parent[self._animation_type][self._layer][self._frame])
        # stack layers
        result = None
        for layer in self._parent._layers:
            if result == None:
                result = io.load_image(self._parent[self._animation_type][layer][self._frame])
                continue
            result.blit(io.load_image(self._parent[self._animation_type][layer][self._frame]), (0, 0))
    
    @property
    def sprite_path(self):
        """ Return the current frame path """
        return self._parent[self._animation_type][self._parent._layers[0]][self._frame]
    
    @property
    def animation_type(self):
        """ Return the current animation type """
        return self._animation_type
    
    @animation_type.setter
    def animation_type(self, value: str):
        """ Set the animation type """
        if self._animation_type == value:
            return
        self._animation_type = value
        self.reset()

    @property
    def animation_layer(self):
        """ Return the current animation layer """
        return self._layer    

    @animation_layer.setter
    def animation_layer(self, value: str):
        """ Set the animation layer """
        if self._layer == value: 
            return
        self._layer = value
        self.reset()

    @property
    def compile_layers(self):
        """ Return the compile layers flag """
        return self._compile_layers

    @compile_layers.setter
    def compile_layers(self, value: bool):
        """ Set the compile layers flag """
        self._compile_layers = value
        self._layer = self._parent._layers[0]

    # ---------------------------- #
    # utils
    
    def get_all_animation_types(self) -> list:
        """ Return all the animation types """
        return list(self._parent._animation_types.keys())

    def get_all_animation_layers(self) -> list:
        """ Return all the animation layers """
        return list(self._parent[self._animation_type].keys())
    
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


