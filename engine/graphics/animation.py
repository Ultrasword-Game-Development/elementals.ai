import pygame
from engine import io
from engine import singleton

from engine.graphics import spritesheet

# ---------------------------- #
# globals

ANI_CACHE = {}


def load_animation(path: str, config: dict = spritesheet.DEFAULT_CONFIG):
    """ Load an animation from a spritesheet given the image path"""
    sheet = spritesheet.SpriteSheet(path, config)
    return load_animation_from_spritesheet(sheet)

def load_animation_from_spritesheet(sheet: spritesheet.SpriteSheet):
    """ Load an animation from a spritesheet """
    if hash(sheet) in ANI_CACHE:
        return ANI_CACHE[hash(sheet)]
    ani = Animation(sheet)
    ANI_CACHE[hash(sheet)] = ani
    return ani


# ---------------------------- #
# animation handler

class Animation:

    def __init__(self, sheet: spritesheet.SpriteSheet):
        """ Create a new animation """
        self._spritesheet = sheet

        # x = list, y = x, --> lists are linked
        self._frames = self._spritesheet.sprites

        # TODO - signal

    def get_registry(self):
        """ Return the animation registry """
        return AnimationRegistry(self)

    # ---------------------------- #

    def __getitem__(self, key: int):
        """ Get the frame at the given index """
        return self._frames[key]
    
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
        del state['_frames']
        return state
    
    def __setstate__(self, state):
        """ Unpickle state """
        self.__dict__.update(state)
        # restore unpicklable entries
        self._frames = self._spritesheet.sprites
        # register the animation
        load_animation_from_spritesheet(self._spritesheet)


# ---------------------------- #
# animation registry

class AnimationRegistry:
    """
    Should not be pickle-able
    """
    def __init__(self, parent: Animation):
        """ Create a new animation registry """
        self._parent = parent
        self._parent_hash = hash(parent)
        self._frame = 0
        self._time = 0
    
    def update(self):
        """ Update the animation """
        self._time += singleton.DELTA_TIME
        if self._time > singleton.ANIMATION_DELTA:
            self._time = 0
            self._frame += 1
            if self._frame >= len(self._parent):
                self._frame = 0
    
    def reset(self):
        """ Reset the animation """
        self._frame = 0
        self._time = 0

    @property
    def sprite(self):
        """ Return the current frame """
        return self._parent[self._frame]
    
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






