
import uuid
import pygame
import dataclasses

from engine import io
from engine import singleton

# ---------------------------- #
# constants

CHUNK_TILE_RECT = "_tile_rect"
CHUNK_TILE_PIXEL_COORD = "_tile_pixel_coords"


# ---------------------------- #
# tile

@dataclasses.dataclass
class DefaultTile:
    """
    The DefaultTile object is only used to HOLD information.
    
    No rendering.
    
    Just data... and updating.
    
    """
    
    _tile_id: str
    _index_position: tuple
    _sprite_path: str
    _data: dict
    
    def __init__(self, position: tuple, sprite: str, width: int = singleton.DEFAULT_TILE_WIDTH, height: int = singleton.DEFAULT_TILE_HEIGHT) -> None:
        """ Initialize the default tile """
        self._tile_id = generate_id()
        
        self._index_position = position
        self._sprite_path = sprite
        
        # extra data storage for custom data objects (child classes)
        self._data = {}
    
    # ---------------------------- #
    # to be overriden
    
    def update(self):
        """ Update the tile """
        pass
    
    # ---------------------------- #
    # utils

    def __setitem__(self, key, value):
        """ Set the data item """
        self._data[key] = value
    
    def __getitem__(self, key):
        """ Get the data item """
        return self._data[key]
    
    def __hash__(self):
        """ Hash the tile """
        return hash(self._tile_id)

# ---------------------------- #
# chunk

class Chunk:
    
    def __init__(self, chunk_position: tuple, 
                 width: int = singleton.DEFAULT_CHUNK_WIDTH, 
                 height: int = singleton.DEFAULT_CHUNK_HEIGHT, 
                 tile_dimensions: tuple = (singleton.DEFAULT_TILE_WIDTH, singleton.DEFAULT_TILE_HEIGHT)
                ) -> None:
        """ Initialize the (square) chunks """
        self._chunk_id = generate_id()    
        
        self._chunk_position = chunk_position
        self._chunk_dimensions = (width, height)
        self._pixel_coords = (self._chunk_position[0] * width * singleton.DEFAULT_TILE_WIDTH, 
                              self._chunk_position[1] * height * singleton.DEFAULT_TILE_HEIGHT)
        
        self._tiles = [ [ None for j in range(width) ] for i in range(height)]
        self._tile_dimensions = tile_dimensions
        
        self._chunk_offset = pygame.math.Vector2(self._chunk_position[0] * width * singleton.DEFAULT_TILE_WIDTH, 
                                                 self._chunk_position[1] * height * singleton.DEFAULT_TILE_HEIGHT)
    
        # all images need to resized / set to the right dimensions (to the dimension of the tile)
        # this script will cache the loaded sprites for faster access
        self._sprite_cacher = io.SpriteCacher()
    
    # ---------------------------- #
    # logic
    
    def update_and_render(self, surface: pygame.Surface, camera_offset: pygame.math.Vector2):
        """ Update and render the chunk """
        # update all tiles
        for row in self._tiles:
            for tile in row:
                if not tile:
                    continue
                # update logic
                tile.update()
                # render logic -- custom render function

                surface.blit(
                    self._sprite_cacher[tile._sprite_path], 
                    tile[CHUNK_TILE_PIXEL_COORD] - camera_offset + self._chunk_offset
                )
                pygame.draw.rect(surface, (255, 255, 255),
                    pygame.Rect(tile[CHUNK_TILE_PIXEL_COORD] - camera_offset + self._chunk_offset, 
                                self._sprite_cacher[tile._sprite_path].get_size()), 1)
    
    # ---------------------------- #
    # utils
    
    def get_tile_at(self, position: tuple) -> DefaultTile:
        """ Get the tile at the position """
        return self._tiles[position[1]][position[0]]
    
    def set_tile_at(self, position: tuple, tile: DefaultTile):
        """ Set the tile at the position """
        self._tiles[position[1]][position[0]] = tile
        # define the collision rect of the tile
        tile[CHUNK_TILE_RECT] = pygame.Rect(0, 0, self._tile_dimensions[0], self._tile_dimensions[1])
        # define the position of the tile -- topleft
        tile[CHUNK_TILE_PIXEL_COORD] = pygame.math.Vector2(
            self._tile_dimensions[0] * position[0],
            self._tile_dimensions[1] * position[1],
        )
        # cache sprite
        self._sprite_cacher.load_sprite(tile._sprite_path, tile[CHUNK_TILE_RECT])
    
    def __hash__(self):
        """ Hash the chunk """
        return hash(self._chunk_id)
    


# ---------------------------- #
# layer

class Layer:
    def __init__(self) -> None:
        pass


# ---------------------------- #
# world

class World:
    def __init__(self) -> None:
        
        self._layers = []
        pass


    
# ---------------------------- #
# utils

def generate_id() -> str:
    """ Generate a unique id """
    return uuid.uuid4().hex
