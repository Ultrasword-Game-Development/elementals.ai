import os
import pygame


from engine import io

# ---------------------------- #
# util functions

WIDTH = "w"
HEIGHT = "h"
PADX = "padx"
PADY = "pady"
SPACINGX = "spacingx"
SPACINGY = "spacingy"

HORIZONTAL_TILES = "horizontal_tiles"
VERTICAL_TILES = "vertical_tiles"

DEFAULT_CONFIG = {
    'w': 18,
    'h': 18,
    'padx': 0,
    'pady': 0,
    'spacingx': 0,
    'spacingy': 0,
}

SPRITESHEET_CACHE = {}


    
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
        self._config = config.copy()

        if path.endswith('.json'):
            self._json = path
            self._load_json_config(path)

        self.image = io.load_image(self._path)
        self.sprites = []

        # load sprites
        self._load_sprites()

        if not self._path in SPRITESHEET_CACHE:
            # cache all the images
            for index, image in enumerate(self.sprites):
                io.cache_image(self.get_sprite_str_id(index), image)

    # ---------------------------- #
    # logic

    def _load_json_config(self, path: str):
        """ Load a json config file """
        data = io.json_to_dict(path)
        self._path = os.path.dirname(self._json) + "/" + data["meta"]["image"]

        # the aseprite files should NOT have padding/margins
        size = (data["frames"][0]["frame"]['w'], data["frames"][0]["frame"]['h'])
        self._config[WIDTH] = size[0]
        self._config[HEIGHT] = size[1]
        self._config[HORIZONTAL_TILES] = data["meta"]["size"]["w"] // size[0]
        self._config[VERTICAL_TILES] = data["meta"]["size"]["h"] // size[1]

    def _load_sprites(self):
        """ Loads all sprites from the spritesheet - including empty ones """
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
            left = padx
        self.sprites = images     
        
        print(self._json)
        print(self._config)
        
        # set other variables
        self._config[HORIZONTAL_TILES] = (self.image.get_size()[0] - self._config[SPACINGX]) // (self._config[WIDTH] + self._config[SPACINGX])
        self._config[VERTICAL_TILES] = (self.image.get_size()[1] - self._config[SPACINGY]) // (self._config[HEIGHT] + self._config[SPACINGY])
    
    def get_sprite_str_id(self, index: int):
        """ Get the sprite uuid """
        return self._path + "||" + str(index)

    # ---------------------------- #
    # utils

    def __getitem__(self, key: int):
        """ Get the sprite """
        return self.sprites[key]

    def __iter__(self):
        """ Iterate over the sprites """
        return iter(self.sprites)
    
    def __len__(self):
        """ Get the number of sprites """
        return len(self.sprites)

    def __hash__(self):
        """ Hash the spritesheet """
        hashable = tuple([self._path] + list(flatten_config_values(self._config)))
        return hash(hashable)

    # ---------------------------- #
    # pickle

    def __getstate__(self):
        """ Pickle state """
        state = self.__dict__.copy()
        # remove unpicklable entries
        del state['image']
        del state['sprites']
        return state

    def __setstate__(self, state):
        """ Unpickle state """
        self.__dict__.update(state)
        # restore unpicklable entries
        self.image = io.load_image(self._path)
        self.sprites = []
        self._load_sprites()
        # cache all the images
        for index, image in enumerate(self.sprites):
            if not self.get_sprite_str_id(index) in io.IMAGES_CACHE:
                io.cache_image(self.get_sprite_str_id(index), image)
        # cache self
        cache_spritesheet(self)

# ---------------------------- #
# functions


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

def generate_config_from_json(json_path: str):
    """ Generate a config from a json file """
    data = io.json_to_dict(json_path)
    meta = data["meta"]
    frame = data["frames"][0]["frame"]
    return __create_config(frame["w"], frame["h"], padx=0, pady=0, spacingx=0, spacingy=0)

def load_spritesheet(image_path: str, config: dict = DEFAULT_CONFIG):
    """ Load a spritesheet """
    # check if its a json
    _json_path = None
    if image_path.endswith('.json'):
        # load the json + find the image path
        data = io.json_to_dict(image_path)
        _json_path = image_path
        image_path = os.path.dirname(image_path) + "/" + data["meta"]["image"]
        config = generate_config_from_json(_json_path)

    # check if already loaded
    _hash = hash(tuple([image_path] + list(flatten_config_values(config))))
    if _hash in SPRITESHEET_CACHE:
        return SPRITESHEET_CACHE[_hash]

    # create new spritesheet + cache it
    result = SpriteSheet(_json_path if _json_path else image_path, config)
    SPRITESHEET_CACHE[hash(result)] = result    
    return result

def cache_spritesheet(sheet: SpriteSheet):
    """ Cache a spritesheet """
    SPRITESHEET_CACHE[hash(sheet)] = sheet
