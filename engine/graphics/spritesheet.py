import pygame
import os

from engine import io

# ---------------------------- #
# util functions

WIDTH = "w"
HEIGHT = "h"
PADX = "padx"
PADY = "pady"
SPACINGX = "spacingx"
SPACINGY = "spacingy"


DEFAULT_CONFIG = {
    'w': 18,
    'h': 18,
    'padx': 0,
    'pady': 0,
    'spacingx': 0,
    'spacingy': 0,
}


def __create_config(width: int, height: int, padx: int = 0, pady: int = 0, spacingx: int = 0, spacingy: int = 0):
    return {
        'w': width,
        'h': height,
        'padx': padx,
        'pady': pady,
        'spacingx': spacingx,
        'spacingy': spacingy,
    }

def flatten_config_values(config: dict = DEFAULT_CONFIG):
    """ Flatten the config values """
    return (config[WIDTH], config[HEIGHT], config[PADX], config[PADY], config[SPACINGX], config[SPACINGY])


# ---------------------------- #
# sprite sheet object

class SpriteSheet:
    """
    Should not be pickle-able
    """

    # ---------------------------- #

    def __init__(self, path: str, config: dict = DEFAULT_CONFIG):
        """ Create a new spritesheet """
        self._path = path
        self._json = None
        self._config = config

        if path.endswith('.json'):
            self._json = path
            self._load_json_config(path)

        self.image =  io.load_image(self._path)
        self.sprites = []

        # load sprites
        self._load_sprites()

    def _load_json_config(self, path: str):
        """ Load a json config file """
        data = io.json_to_dict(path)
        self._path = os.path.join(os.path.dirname(self._json), data["meta"]["image"])

        # the aseprite files should NOT have padding/margins
        size = (data["frames"][0]["frame"]['w'], data["frames"][0]["frame"]['h'])
        self._config[WIDTH] = size[0]
        self._config[HEIGHT] = size[1]

    def _load_sprites(self):
        """ Loads all sprites from the spritesheet """
        left = 0
        top = 0

        max_width = self.image.get_width()
        max_height = self.image.get_height()

        padx = self._config[PADX]
        pady = self._config[PADY]
        spacingx = self._config[SPACINGX]
        spacingy = self._config[SPACINGY]
        width = self._config[WIDTH]
        height = self._config[HEIGHT]

        left += self._config[PADX]
        images = []
        while top <= max_height - pady - height:
            while left <= max_width - padx - width:
                snip = self.image.subsurface(left, top, width, height).convert_alpha()
                images.append(snip)
                left += spacingx + width
            top += spacingy + height
        self.sprites = images

    def __getitem__(self, key: int):
        return self.sprites[key]

    def __iter__(self):
        return iter(self.sprites)
    
    def __len__(self):
        return len(self.sprites)

    def __hash__(self):
        """ Hash the spritesheet """
        return hash(tuple([self._path] + list(flatten_config_values())))

    # ---------------------------- #
    # pickle

    def __getstate__(self):
        """ Pickle state """
        state = self.__dict__.copy()
        # remove unpicklable entries
        del state['image']
        return state

    def __setstate__(self, state):
        """ Unpickle state """
        self.__dict__.update(state)
        # restore unpicklable entries
        self.image = io.load_image(self._path)
        self._load_sprites()


