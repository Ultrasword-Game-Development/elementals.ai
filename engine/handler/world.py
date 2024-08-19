import os
import dill
import uuid
import copy
import pygame
import pickle
import datetime
import dataclasses

from engine import io
from engine import utils
from engine import singleton

from engine.handler import signal
from engine.handler import component
from engine.handler import aspect

from engine.graphics import camera
from engine.graphics import spritesheet

from engine.physics import phandler

from engine.addon import spritecacher

# ---------------------------- #
# constants

CHUNK_TILE_RECT = "_tile_rect"
CHUNK_TILE_PIXEL_COORD = "_tile_pixel_coords"
CHUNK_TILE_PARENT_POSITION_KEY = "_chunk_parent_key"

WORLD_SIGNAL_HANDLER = "_world_signal_handler"

CAMERA_MOVED_CHUNKS = "_camera_moved_chunks"
CAMERA_OLD_CHUNK = "_old_chunk"
CAMERA_NEW_CHUNK = "_new_chunk"


WORLD_LEVEL_FOLDER = "assets/level/"
WORLD_LEVEL_CHUNKS_FOLDER = "chunkdata/"

WORLD_CACHE = {}

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
    _rect: "pygame.Rect"
    _collision_mask: int
    _data: dict
    
    def __init__(self, position: tuple, sprite: str, solid: bool = True) -> None:
        """ Initialize the default tile """
        if not "__parent_class__" in self.__dict__:
            self.__parent_class__ = DefaultTile
        
        self._tile_id = generate_id()
        
        self._index_position = position
        self._sprite_path = sprite
        self._rect = pygame.FRect(
            position[0] * singleton.DEFAULT_TILE_WIDTH,
            position[1] * singleton.DEFAULT_TILE_HEIGHT, 
            singleton.DEFAULT_TILE_WIDTH, 
            singleton.DEFAULT_TILE_HEIGHT
        )
        self._collision_mask = 0b0000000000000001
        
        # extra data storage for custom data objects (child classes)
        self._data = {}
    
    # ---------------------------- #
    # to be overriden
    
    def __post_init__ (self, chunk: "Chunk"):
        """ Post init function """
        pass
    
    def update(self):
        """ Update the tile """
        pass
    
    def render(self, surface, camera: camera.PseudoCamera, offset: tuple):
        """ Render the tile """
        pass
    
    def copy(self) -> "Tile Type Class":
        """ Create a copy """
        print(self._data)
        return self.__parent_class__(self._index_position, self._sprite_path)

    # ---------------------------- #
    # utils

    def set_mask_value(self, mask_index: int, value: bool):
        """ Set the mask value """
        if mask_index < 0 or mask_index > 15:
            raise ValueError("mask_index must be between 0 and 15")
        if value:
            self._collision_mask |= 0b1 << (mask_index)
        else:
            self._collision_mask &= ~(0b1 << (mask_index))
    
    def get_mask_value(self, mask_index: int):
        """ Get the mask value """
        if mask_index < 0 or mask_index > 15:
            raise ValueError("mask_index must be between 0 and 15")
        return (self._collision_mask >> (mask_index - 1)) & 0b1
    
    def get_mask(self):
        """ Get the mask """
        return self._collision_mask

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
        except Exception as e:
            raise ValueError(f"Data item `{key}` cannot be serialized because value: `{value}` is not serializable\nError as : {e}")
    
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
        state = self.__dict__.copy()
        del state['_data']
        return state

    def __setstate__(self, state):
        """ Set the state of the tile """
        self.__dict__.update(state)
        self._data = {}
        # check if sprite is loaded in global
        

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
        
        self.__tile_pixel_area = (tile_dimensions[0], tile_dimensions[1])
        self._tile_pixel_area = (
            singleton.DEFAULT_TILE_WIDTH if not tile_dimensions[0] else tile_dimensions[0],
            singleton.DEFAULT_TILE_HEIGHT if not tile_dimensions[1] else tile_dimensions[1]
        )

        self._chunk_rect = pygame.Rect(self._pixel_coords, (singleton.DEFAULT_CHUNK_PIXEL_WIDTH, singleton.DEFAULT_CHUNK_PIXEL_HEIGHT))
        
        self._chunk_offset = pygame.math.Vector2(get_chunk_offset(self._chunk_position))
    
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
        self._sprite_cacher = spritecacher.SpriteCacher(self._tile_pixel_area)
    
    # ---------------------------- #
    # logic
    
    def update_and_render(self, surface: pygame.Surface, _camera: camera.PseudoCamera):
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
                    tile[CHUNK_TILE_PIXEL_COORD] - _camera.position + self._chunk_offset
                )
                if singleton.DEBUG or singleton.EDITOR_DEBUG:
                    pygame.draw.rect(surface, (255, 255, 255, 150),
                        pygame.Rect(tile[CHUNK_TILE_PIXEL_COORD] - _camera.position + self._chunk_offset, 
                            self._sprite_cacher[tile._sprite_path].get_size()), 1)

    def collide_tiles(self, rect: pygame.Rect) -> "Iterable":
        """ Collide the tiles """
        for j in range(self._chunk_tile_dimensions[1]):
            for i in range(self._chunk_tile_dimensions[0]):
                # check if tile exists
                if not self._tiles[j][i]:
                    continue
                # check if colliding
                if phandler.collide_rect_to_rect(rect, self._tiles[j][i]._rect):
                    yield self._tiles[j][i]

    # ---------------------------- #
    # utils
    
    def get_tile_at(self, position: tuple) -> DefaultTile:
        """ Get the tile at the position """
        return self._tiles[position[1]][position[0]]
    
    def set_tile_at(self, position: tuple, tile: DefaultTile):
        """ Set the tile at the position """
        # check if need to just REMOVE the tile
        if not tile:
            self._tiles[position[1]][position[0]] = None
            return
        self._tiles[position[1]][position[0]] = tile
        tile._index_position = (position[0], position[1])
        # define the collision rect of the tile
        tile._rect.topleft = (
            position[0] * self._tile_pixel_area[0] + self._pixel_coords[0],
            position[1] * self._tile_pixel_area[1] + self._pixel_coords[1]
        )
        tile._rect.size = (self._tile_pixel_area[0], self._tile_pixel_area[1])
        # define the position of the tile -- topleft
        tile[CHUNK_TILE_PIXEL_COORD] = pygame.math.Vector2(
            self._tile_pixel_area[0] * position[0],
            self._tile_pixel_area[1] * position[1],
        )
        # cache sprite
        self._sprite_cacher.load_sprite(tile._sprite_path)
        
        # set parent definition into tile
        tile[CHUNK_TILE_PARENT_POSITION_KEY] = self.get_chunk_hash_str(self._chunk_position)
        tile.__post_init__(self)
    
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

    @classmethod
    def generate_chunk_rect_given_chunk_position(cls, chunk_pos: tuple, camera: camera.PseudoCamera):
        """ Generate the chunk rect given the chunk position """
        return pygame.Rect(
            get_chunk_offset(chunk_pos) - camera.position,
            (singleton.DEFAULT_CHUNK_PIXEL_HEIGHT, singleton.DEFAULT_CHUNK_PIXEL_WIDTH)
        )

    # ---------------------------- #
    # serializable
    
    def __getstate__(self) -> object:
        """ Get the state of the chunk """
        state = self.__dict__.copy()
        # load all chunks into a chunk save file
        _filename = self._chunk_hash_str + "==" + str(self._layer._layer_id)
        
        if not singleton.SAVING_WORLD_FLAG:
            del state["_tiles"]
            del state["_sprite_cacher"]
            return state

        # the chunk save folder should already exist
        # we save the chunkdata into the file to isolate chunk data and world data (transferrable terrain) 
        with open(WORLD_LEVEL_FOLDER + self._world_storage_key + "/" + WORLD_LEVEL_CHUNKS_FOLDER + _filename, 'wb') as f:
            print("Saving Chunk: ", self._chunk_hash_str, " | to file: ", WORLD_LEVEL_FOLDER + self._world_storage_key + "/" + WORLD_LEVEL_CHUNKS_FOLDER + _filename)
            f.write(pickle.dumps(self._tiles))
        del state["_tiles"]
        del state["_sprite_cacher"]
        # return the state
        return state
    
    def __setstate__(self, state: object):
        """ Set the state of the chunk """
        # recreate the hash str
        self.__dict__.update(state)
        # update size
        self._tile_pixel_area = (
            singleton.DEFAULT_TILE_WIDTH if not self.__tile_pixel_area[0] else self.__tile_pixel_area[0],
            singleton.DEFAULT_TILE_HEIGHT if not self.__tile_pixel_area[1] else self.__tile_pixel_area[1]
        )
        # create a new sprite cacher
        self._sprite_cacher = spritecacher.SpriteCacher(self._tile_pixel_area)

    def load_chunk_data(self):
        """ Load the chunk data """
        # load up the chunk save file
        _filename = self._chunk_hash_str + "==" + str(self._layer._layer_id)
        with open(WORLD_LEVEL_FOLDER + "/" + self._world_storage_key + "/" + WORLD_LEVEL_CHUNKS_FOLDER + _filename, 'rb') as f:
            _tiles = dill.load(f)
        self._tiles = [ [ None for x in range(len(_tiles[y])) ] for y in range(len(_tiles)) ]
        # re "place" all the tiles
        for y in range(len(_tiles)):
            for x in range(len(_tiles[y])):
                if _tiles[y][x]:
                    self.set_tile_at((x, y), _tiles[y][x])        
    
        
# ---------------------------- #
# layer

class Layer:

    # ---------------------------- #

    def __init__(self, layer_num: int) -> None:
        """ Initialize the layer """
        self._layer_buffer = pygame.Surface(singleton.FB_SIZE, singleton.DEFAULT_SURFACE_FLAGS, 16).convert_alpha()
        self._layer_buffer.fill((0, 0, 0, 0))
        self._layer_id = layer_num

        # chunk handler
        self._chunks = {}
        self._world = None

        # data
        self._data = {}

    # ---------------------------- #
    # logic

    def update(self, camera: camera.PseudoCamera):
        """ Update and render the layer """
        self._layer_buffer.fill((0, 0, 0, 0))
        # update the chunks
        for chunk_hash_str in self._world._renderable_chunks_hash_strs:
            if chunk_hash_str not in self._chunks:
                continue
            self._chunks[chunk_hash_str].update_and_render(self._layer_buffer, camera)
            
            if not singleton.DEBUG and not singleton.EDITOR_DEBUG:
                continue
            # draw chunk rect
            pygame.draw.rect(self._layer_buffer, (255, 255, 255, 150), 
                Chunk.generate_chunk_rect_given_chunk_position(self._chunks[chunk_hash_str]._chunk_position, camera), 1)
    
    def render(self, surface: pygame.Surface):
        """ Render the layer """
        # TODO - add opengl rendering + custom shaders to each layer
        surface.blit(self._layer_buffer, (0, 0))

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
    # data

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

    def get_chunk_at_or_default(self, position: tuple) -> Chunk:
        """ Get the chunk at the position or create a default chunk """
        result = self._chunks.get(Chunk.get_chunk_hash(position))
        if result:
            return result
        # generate default chunk
        result = Chunk(position)
        self.set_chunk_at(result)
        return result

    def get_tile_at(self, global_tile_position: tuple) -> DefaultTile:
        """ Get the tile at the global position """
        chunk_pos = (
            global_tile_position[0] // singleton.DEFAULT_CHUNK_WIDTH,
            global_tile_position[1] // singleton.DEFAULT_CHUNK_HEIGHT
        )
        chunk = self.get_chunk_at(chunk_pos)
        if not chunk:
            return None
        return chunk.get_tile_at(
            (
                global_tile_position[0] % singleton.DEFAULT_CHUNK_WIDTH,
                global_tile_position[1] % singleton.DEFAULT_CHUNK_HEIGHT
            )
        )
    
    def set_tile_at(self, global_tile_position: tuple, tile: DefaultTile = None):
        """ Set the tile at the global position """
        chunk_pos = (
            global_tile_position[0] // singleton.DEFAULT_CHUNK_WIDTH,
            global_tile_position[1] // singleton.DEFAULT_CHUNK_HEIGHT
        )
        chunk = self.get_chunk_at(chunk_pos)
        if not chunk:
            chunk = self.create_default_chunk(chunk_pos)
        chunk.set_tile_at(
            (
                global_tile_position[0] % singleton.DEFAULT_CHUNK_WIDTH,
                global_tile_position[1] % singleton.DEFAULT_CHUNK_HEIGHT
            ),
            tile
        )

    def create_default_chunk(self, position: tuple):
        """ Create a default chunk """
        _c = Chunk(position)
        _c._layer = self
        _c._world_storage_key = self._world._world_storage_key
        self._chunks[hash(_c)] = _c
        print(hash(_c), _c._chunk_hash_str)
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
        self._layer_buffer = pygame.Surface(singleton.FB_SIZE, pygame.SRCALPHA, 16).convert_alpha()
        self._layer_buffer.fill((0, 0, 0, 0))
    
    def load_layer_data(self):
        """ Load the layer data """
        for _chunk in self._chunks.values():
            _chunk.load_chunk_data()

# ---------------------------- #
# world

class World:
    def __init__(self, name: str = None) -> None:
        """ Initialize the world """
        # store a "save file" with the creatino date and world name
        __num = 1
        __base = "New World"
        if "New World" in os.listdir(WORLD_LEVEL_FOLDER):
            while (end_result_string := f"{__base} ({__num})") in os.listdir(WORLD_LEVEL_FOLDER):
                __num += 1
        
        self._world_storage_key = f"{name if name else ("New World" + end_result_string)}"
        
        # cache the world
        self.cache_world(self)

        # background color
        self._background_color = singleton.WIN_BACKGROUND
        
        # physics handler
        self._physics_handler = phandler.PhysicsHandler(self)

        # ECS system
        self._aspect_handler = aspect.AspectHandler(self)
        self._component_handler = component.ComponentHandler(self)

        # camera data
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
        self._layers = {_ - 2 : Layer(_ - 2) for _ in range(singleton.DEFAULT_LAYER_COUNT)}
        # give each layer a signal emitter
        for layer in self._layers.values():
            layer._signal_emitter = self._layer_signals.get_unique_emitter()
            layer._world = self
        
        # special data object
        self._data = {
            "EDITOR_TAB_SPRITESHEETS": {},
            "GAMEOBJECT_ID_COUNT": 0,
            "COMPONENT_ID_COUNT": 0,
            "PHYSICS_COMP_ID_COUNT": 0
        }
    
        self.__post_init__()

    def __post_init__(self):
        """ Post init function """
        self.update_renderable_chunks()

    # ---------------------------- #
    # logic

    def update_and_render_world(self, surface: pygame.Surface):
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
            self._layers[layer].update(self.camera)
        # update aspects
        self._aspect_handler.handle(self.camera)
        # render layers
        for layer in self._layers:
            self._layers[layer].render(surface)
            
        
    def update_and_render_physics(self):
        """ Update and render the physics """
        self._physics_handler.update()

    def get_layer_at(self, layer: int):
        """ Get the layer at the index """
        return self._layers[layer]
    
    def add_layer(self, layer: Layer):
        """ Add a layer to the world """
        self._layers[layer._layer_id] = (layer)
        # setup layer
        layer._signal_emitter = self._layer_signals.get_unique_emitter()
        layer._world = self
    
    def remove_layer(self, layer: int) -> Layer:
        """ Remove a layer from the world """
        return self._layers.pop(layer)
    
    # ---------------------------- #
    # utils

    # gameobject 

    def add_gameobject(self, gameobject: "GameObject"):
        """ Add an gameobject to the world """
        self._physics_handler.add_gameobject(gameobject)
        return gameobject
    
    def get_gameobject(self, gameobject_id: int) -> "GameObject":
        """ Get the gameobject """
        return self._physics_handler.get_gameobject(gameobject_id)

    def remove_gameobject(self, gameobject_id: int):
        """ Remove gameobject - set to be dead """
        self._physics_handler.get_gameobject(gameobject_id).kill()

    # aspects

    def add_aspect(self, aspect: "Aspect"):
        """ Add an aspect to the world """
        self._aspect_handler.add_aspect(aspect)
    
    def get_aspect(self, _aspect_class: "Aspect Class") -> "Aspect":
        """ Get the aspect """
        return self._aspect_handler.get_aspect(_aspect_class)
    
    def remove_aspect(self, aspect: "Aspect"):
        """ Remove an aspect from the world """
        self._aspect_handler.remove_aspect(aspect)
    
    def remove_aspect_by_str(self, _aspect_class: str):
        """ Remove an aspect by string """
        self._aspect_handler.remove_aspect_by_str(_aspect_class)
    
    # chunk stuff

    def update_renderable_chunks(self):
        """ Update the renderable chunks """
        self._renderable_chunks_hash_strs.clear()
        for rx, ry in self.iterate_renderable_chunk_positions():
            self._renderable_chunks_hash_strs.add(Chunk.get_chunk_hash((rx, ry)))

    def iterate_renderable_chunk_positions(self):
        """ Iterate the renderable chunks """
        for cx in range(self._camera_old_chunk[0] - self._render_distance[0], self._camera_old_chunk[0] + self._render_distance[0] + 1):
            for cy in range(self._camera_old_chunk[1] - self._render_distance[0], self._camera_old_chunk[1] + self._render_distance[0] + 1):
                yield (cx, cy)

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
        
        # check if actually saving (officially)
        if not singleton.SAVING_WORLD_FLAG:
            return state
        
        # create a blob storage file - this should run first
        if not os.path.exists(WORLD_LEVEL_FOLDER + self._world_storage_key):
            print("Creating world folder: ", WORLD_LEVEL_FOLDER + self._world_storage_key)
            os.mkdir(WORLD_LEVEL_FOLDER + self._world_storage_key)
        if not os.path.exists(WORLD_LEVEL_FOLDER + self._world_storage_key + "/" + WORLD_LEVEL_CHUNKS_FOLDER):
            print("Creating world chunk folder: ", WORLD_LEVEL_FOLDER + self._world_storage_key + "/" + WORLD_LEVEL_CHUNKS_FOLDER)
            os.mkdir(WORLD_LEVEL_FOLDER + self._world_storage_key + "/" + WORLD_LEVEL_CHUNKS_FOLDER)
        
        return state
    
    def __setstate__(self, state):
        """ Set the state of the world """
        # update the editor injected tab spritesheet data
        for _path, _data in state["_data"]["EDITOR_TAB_SPRITESHEETS"].items():
            spritesheet.load_spritesheet(_path, framedata=_data)
            
        self.__dict__.update(state)

        # load world data
        for layer in self._layers:
            self._layers[layer].load_layer_data()
    
    def get_world_saving_main_file(self):
        """ Get the world saving folder """
        return WORLD_LEVEL_FOLDER + self._world_storage_key + "/save.elal"

    def get_world_saving_folder(self):
        """ Get the world saving folder """
        return WORLD_LEVEL_FOLDER + self._world_storage_key

    # ---------------------------- #
    # caching
    
    @classmethod
    def cache_world(cls, world):
        """ Cache the world """
        if world._world_storage_key in WORLD_CACHE:
            raise ValueError(f"World with key {world._world_storage_key} already exists in cache")
        WORLD_CACHE[world._world_storage_key] = world
    
    @classmethod
    def save_world(cls, world: "World"):
        """ Save the world """
        world._data["GAMEOBJECT_ID_COUNT"] = singleton.GAMEOBJECT_ID_COUNT
        world._data["COMPONENT_ID_COUNT"] = singleton.COMPONENT_ID_COUNT
        world._data["PHYSICS_COMP_ID_COUNT"] = singleton.PHYSICS_COMP_ID_COUNT
        
        singleton.save_world(world)

    @classmethod
    def load_world(cls, world_key: str):
        """ Load the world from the cache """
        if world_key in WORLD_CACHE:
            return WORLD_CACHE[world_key]
        # load the world
        result = singleton.load_world((WORLD_LEVEL_FOLDER if not world_key.startswith(WORLD_LEVEL_FOLDER) else "") + world_key)
        cls.cache_world(result)
        # update constants
        singleton.GAMEOBJECT_ID_COUNT = result._data["GAMEOBJECT_ID_COUNT"]
        singleton.COMPONENT_ID_COUNT = result._data["COMPONENT_ID_COUNT"]
        singleton.PHYSICS_COMP_ID_COUNT = result._data["PHYSICS_COMP_ID_COUNT"]
        return result
    
    @classmethod
    def reload_world(cls, world_key: str):
        """ Reload the world """
        result = singleton.load_world(world_key)
        WORLD_CACHE[world_key] = result
        return result
    
# ---------------------------- #
# utils

def generate_id() -> str:
    """ Generate a unique id """
    return uuid.uuid4().hex

def get_chunk_from_pixel_position(pos: tuple):
    """ Get the chunk from the position """
    return (
        int(pos[0] // singleton.DEFAULT_CHUNK_PIXEL_WIDTH),
        int(pos[1] // singleton.DEFAULT_CHUNK_PIXEL_HEIGHT)
    )

def get_chunk_offset(chunk_pos: tuple):
    """ Get the chunk offset """
    return (
        chunk_pos[0] * singleton.DEFAULT_CHUNK_PIXEL_WIDTH,
        chunk_pos[1] * singleton.DEFAULT_CHUNK_PIXEL_HEIGHT
    )