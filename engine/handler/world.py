import os
import dill
import uuid
import pygame
import datetime
import dataclasses

from engine import io
from engine import singleton

from engine.handler import signal

from engine.graphics import camera

from engine.physics import phandler

# ---------------------------- #
# constants

CHUNK_TILE_RECT = "_tile_rect"
CHUNK_TILE_PIXEL_COORD = "_tile_pixel_coords"

WORLD_SIGNAL_HANDLER = "_world_signal_handler"

CAMERA_MOVED_CHUNKS = "_camera_moved_chunks"
CAMERA_OLD_CHUNK = "_old_chunk"
CAMERA_NEW_CHUNK = "_new_chunk"

CHUNK_PARENT_KEY = "_chunk_parent_key"

WORLD_BLOBS_FOLDER = "assets/level/blobs"
WORLD_BLOBS_CHUNKS_FOLDER = "chunkdata/"

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
    
    def render(self, surface, camera: camera.PseudoCamera, offset: tuple):
        """ Render the tile """
        surface.blit(
            
        )
    
    # ---------------------------- #
    # utils

    def __setitem__(self, key, value):
        """ Set the data item """
        # check if item can be serialized
        if key in self._data:
            self._data[key] = value
            return
        # check if it works in dill
        try:
            dill.dumps(value)
            self._data[key] = value
        except:
            raise ValueError(f"Data item {key} cannot be serialized because value: {value} is not serializable")
    
    def __getitem__(self, key):
        """ Get the data item """
        return self._data[key]
    
    def __hash__(self):
        """ Hash the tile """
        return hash(self._tile_id)

    # ---------------------------- #
    # serialize
    
    def __getstate__(self):
        """ Get the state of the tile """
        return self.__dict__

    def __setstate__(self, state):
        """ Set the state of the tile """
        self.__dict__.update(state)

# ---------------------------- #
# chunk

class Chunk:
    
    def __init__(self, chunk_position: tuple, 
                 width: int = 0, 
                 height: int = 0, 
                 tile_dimensions: tuple = (0, 0)
                ) -> None:
        """ Initialize the (square) chunks """
        self._chunk_id = generate_id()
        self._chunk_hash_str = f"{chunk_position[0]}=={chunk_position[1]}"
        self._layer = None
        self._world_storage_key = None
        
        self._chunk_position = chunk_position
        self._chunk_tile_dimensions = (
            singleton.DEFAULT_CHUNK_WIDTH if not width else width, 
            singleton.DEFAULT_CHUNK_HEIGHT if not height else height
        )
        self._pixel_coords = (
            self._chunk_position[0] * self._chunk_tile_dimensions[0] * singleton.DEFAULT_TILE_WIDTH, 
            self._chunk_position[1] * self._chunk_tile_dimensions[1] * singleton.DEFAULT_TILE_HEIGHT
        )
        
        self._tile_pixel_area = (
            singleton.DEFAULT_TILE_WIDTH if not tile_dimensions[0] else tile_dimensions[0],
            singleton.DEFAULT_TILE_HEIGHT if not tile_dimensions[1] else tile_dimensions[1]
        )
        
        self._chunk_offset = pygame.math.Vector2(
            self._chunk_position[0] * singleton.DEFAULT_CHUNK_PIXEL_WIDTH,
            self._chunk_position[1] * singleton.DEFAULT_CHUNK_PIXEL_HEIGHT
        )
    
        # create tile storage
        self._tiles = [ 
            [ 
                None 
                for j in range(self._chunk_tile_dimensions[0]) 
            ] 
            for i in range(self._chunk_tile_dimensions[1])
        ]

        # all images need to resized / set to the right dimensions (to the dimension of the tile)
        # this script will cache the loaded sprites for faster access
        self._sprite_cacher = io.SpriteCacher()
    
    # ---------------------------- #
    # logic
    
    def update_and_render(self, surface: pygame.Surface, camera: camera.PseudoCamera):
        """ Update and render the chunk """
        # update all tiles
        for row in self._tiles:
            for tile in row:
                if not tile:
                    continue
                # update logic
                tile.update()
                # render logic
                surface.blit(
                    self._sprite_cacher[tile._sprite_path], 
                    tile[CHUNK_TILE_PIXEL_COORD] - camera.position + self._chunk_offset
                )
                if singleton.DEBUG:
                    pygame.draw.rect(surface, (255, 255, 255),
                        pygame.Rect(tile[CHUNK_TILE_PIXEL_COORD] - camera.position + self._chunk_offset, 
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
        tile[CHUNK_TILE_RECT] = pygame.Rect(0, 0, self._tile_pixel_area[0], self._tile_pixel_area[1])
        # define the position of the tile -- topleft
        tile[CHUNK_TILE_PIXEL_COORD] = pygame.math.Vector2(
            self._tile_pixel_area[0] * position[0],
            self._tile_pixel_area[1] * position[1],
        )
        # cache sprite
        self._sprite_cacher.load_sprite(tile._sprite_path, tile[CHUNK_TILE_RECT])
        
        # set parent definition into tile
        tile[CHUNK_PARENT_KEY] = self
    
    def __hash__(self):
        """ Hash the chunk """
        return hash(self._chunk_hash_str)

    def __str__(self):
        """ String representation of the chunk """
        return f"Chunk || position: {self._chunk_position}, pixel_coords: {self._pixel_coords}, dimensions: {singleton.DEFAULT_CHUNK_AREA_VEC2}, pixel_dimensions: {singleton.DEFAULT_CHUNK_PIXEL_WIDTH}x{singleton.DEFAULT_CHUNK_PIXEL_HEIGHT}"

    # ---------------------------- #
    # classmethod
    
    @classmethod
    def get_chunk_hash_str(cls, position: tuple) -> str:
        """ Get the chunk hash """
        return f"{position[0]}=={position[1]}"
    
    @classmethod
    def get_chunk_hash(cls, position: tuple) -> str:
        """ Get the chunk hash """
        return hash(cls.get_chunk_hash_str(position))

    # ---------------------------- #
    # serializable
    
    def __getstate__(self) -> object:
        """ Get the state of the chunk """
        state = self.__dict__.copy()
        # load all chunks into a chunk save file
        _filename = self._chunk_hash_str
        # the chunk save folder should already exist
        # we save the chunkdata into the file to isolate chunk data and world data (transferrable terrain)
        with open(WORLD_BLOBS_FOLDER + "/" + self._world_storage_key + "/" + WORLD_BLOBS_CHUNKS_FOLDER + _filename, 'wb') as f:
            dill.dump(self._tiles, f)
        del state["_tiles"]
        # return the state
        return state
    
    def __setstate__(self, state: object):
        """ Set the state of the chunk """
        self.__dict__.update(state)
        # load up the chunk save file
        _filename = self._chunk_hash_str
        with open(WORLD_BLOBS_FOLDER + "/" + self._world_storage_key + "/" + WORLD_BLOBS_CHUNKS_FOLDER + _filename, 'rb') as f:
            self._tiles = dill.load(f)
        

# ---------------------------- #
# layer

class Layer:
    def __init__(self) -> None:
        """ Initialize the layer """
        self._layer_buffer = pygame.Surface(singleton.FB_SIZE, 0, 16).convert_alpha()
        self._physics_handler = phandler.PhysicsHandler()

        # chunk handler
        self._chunks = {}

        # parent
        self._world = None

    # ---------------------------- #
    # logic

    def update_and_render(self, surface: pygame.Surface, camera: camera.PseudoCamera):
        """ Update and render the layer """
        # update the chunks
        for chunk_hash_str in self._world._renderable_chunks_hash_strs:
            if chunk_hash_str not in self._chunks:
                continue
            self._chunks[chunk_hash_str].update_and_render(surface, camera)

        # render the physics
        self._physics_handler.update_and_render(self._layer_buffer, camera)

    # ---------------------------- #
    # signal logic

    def _layer_signal_handler(self):
        """ 
        Handle received layer signals
        
        - entities moving between layers
        - multi-layer entities
        - etc
        """
        # TODO - create signal handling code
        pass

    # ---------------------------- #
    # utils

    def set_chunk_at(self, chunk: Chunk):
        """ Set the chunk at the position """
        self._chunks[hash(chunk)] = chunk
        # set world variables
        chunk._layer = self
        chunk._world_storage_key = self._world._world_storage_key
    
    def get_chunk_at(self, position: tuple) -> Chunk:
        """ Get the chunk at the position """
        return self._chunks.get(Chunk.get_chunk_hash(position))

    def create_default_chunk(self, position: tuple):
        """ Create a default chunk """
        _c = Chunk(position)
        _c._layer = self
        _c._world_storage_key = self._world._world_storage_key
        self._chunks[position] = _c
        return _c

    # ---------------------------- #
    # serializable
    
    def __getstate__(self):
        """ Get the state of the layer """
        state = self.__dict__.copy()
        del state["_layer_buffer"]
        return state
    
    def __setstate__(self, state):
        """ Set the state of the layer """
        self.__dict__.update(state)
        # load unserializable data
        self._layer_buffer = pygame.Surface(singleton.FB_SIZE, 0, 16).convert_alpha()

# ---------------------------- #
# world

class World:
    def __init__(self, name: str = None) -> None:
        """ Initialize the world """
        # store a "save file" with the creatino date and world name
        self._world_storage_key = f"{name if name else "New World"}=={str(datetime.datetime.now()).split()[0]}"
        
        self._camera = camera.PseudoCamera((0, 0), singleton.FB_SIZE)
        self.camera = self._camera
        self._camera_old_chunk = (
            int(self._camera.center[0] // singleton.DEFAULT_CHUNK_PIXEL_WIDTH),
            int(self._camera.center[1] // singleton.DEFAULT_CHUNK_PIXEL_HEIGHT)
        )

        # chunk handling
        self._center_chunk = (
            int(self.camera.center[0] // singleton.DEFAULT_CHUNK_PIXEL_WIDTH),
            int(self.camera.center[1] // singleton.DEFAULT_CHUNK_PIXEL_HEIGHT)
        )
        self._render_distance = singleton.DEFAULT_CHUNK_RENDER_DISTANCE
        self._renderable_chunks_hash_strs = set()
        self._update_invisible_chunks = singleton.UPDATE_INVISIBLE_CHUNKS

        # signal handler
        self._layer_signals = signal.Signal(WORLD_SIGNAL_HANDLER)
        self._layers = [Layer() for _ in range(singleton.DEFAULT_LAYER_COUNT)]
        # give each layer a signal emitter
        for layer in self._layers:
            layer._signal_emitter = self._layer_signals.get_unique_emitter()
            layer._world = self
    
        self.__post_init__()

    def __post_init__(self):
        """ Post init function """
        self.update_renderable_chunks()

    # ---------------------------- #
    # logic

    def update_and_render(self, surface: pygame.Surface):
        """ Update and render the world """
        # check if camera entered new chunk
        new_c_chunk = (
            int(self.camera.center[0] // singleton.DEFAULT_CHUNK_PIXEL_WIDTH), 
            int(self.camera.center[1] // singleton.DEFAULT_CHUNK_PIXEL_HEIGHT)
        )
        if self._camera_old_chunk != new_c_chunk:
            self._camera_old_chunk = new_c_chunk
            self.update_renderable_chunks()
        
        # update layers
        for layer in self._layers:
            layer.update_and_render(surface, self._camera)
    
    def get_layer_at(self, layer: int):
        """ Get the layer at the index """
        return self._layers[layer]
    
    def add_layer(self, layer: Layer):
        """ Add a layer to the world """
        self._layers.append(layer)
        # setup layer
        layer._signal_emitter = self._layer_signals.get_unique_emitter()
        layer._world = self
    
    def remove_layer(self, layer: int) -> Layer:
        """ Remove a layer from the world """
        return self._layers.pop(layer)
    
    # ---------------------------- #
    # utils

    def update_renderable_chunks(self):
        """ Update the renderable chunks """
        self._renderable_chunks_hash_strs.clear()
        for cx in range(self._camera_old_chunk[0] - self._render_distance, self._camera_old_chunk[0] + self._render_distance + 1):
            for cy in range(self._camera_old_chunk[1] - self._render_distance, self._camera_old_chunk[1] + self._render_distance + 1):
                self._renderable_chunks_hash_strs.add(Chunk.get_chunk_hash((cx, cy)))

    def get_camera_chunk(self):
        """ Get the camera chunk """
        return (
            int(self.camera.center[0] // singleton.DEFAULT_CHUNK_PIXEL_WIDTH),
            int(self.camera.center[1] // singleton.DEFAULT_CHUNK_PIXEL_HEIGHT)
        )
    
    # ---------------------------- #
    # serializable
    
    def __getstate__(self):
        """ Get the state of the world """
        state = self.__dict__.copy()
        # create a blob storage file - this should run first
        if not os.path.exists(WORLD_BLOBS_FOLDER + "/" + self._world_storage_key):
            os.mkdir(WORLD_BLOBS_FOLDER + "/" + self._world_storage_key)
        if not os.path.exists(WORLD_BLOBS_FOLDER + "/" + self._world_storage_key + "/" + WORLD_BLOBS_CHUNKS_FOLDER):
            os.mkdir(WORLD_BLOBS_FOLDER + "/" + self._world_storage_key + "/" + WORLD_BLOBS_CHUNKS_FOLDER)
        return state
    
# ---------------------------- #
# utils

def generate_id() -> str:
    """ Generate a unique id """
    return uuid.uuid4().hex
