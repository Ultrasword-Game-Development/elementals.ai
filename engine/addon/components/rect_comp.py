
import pygame

from engine import singleton

from engine.handler import world
from engine.handler import aspect
from engine.handler import component

from engine.physics import phandler

from engine.addon.components import sprite_comp
from engine.addon.components import mask_comp
from engine.addon.components import physics_comp
from engine.addon.components import hitbox_comp

# ---------------------------- #
# constants

COMPONENT_NAME = "WorldRectComponent"

# ---------------------------- #
# component

class WorldRectComponent(physics_comp.PhysicsComponent):
    def __init__(self, area: tuple = (0, 0), has_sprite: bool = True, has_mask: bool = False):
        """ Create a new Rect Component that collides with the World """
        super().__init__()

        self._rect = pygame.FRect(0, 0, *area)
        self._area = area
        self._mask_comp = None
        
        self._has_sprite = has_sprite
        self._has_mask = has_mask

        self._has_hitbox = False
        self._hitbox = None
    
    def __post_gameobject__(self, gameobject: "GameObject"):
        """ Post init function """
        super().__post_gameobject__(gameobject)

        if self._has_sprite:
            self._sprite_comp = gameobject.get_component([sprite_comp.COMPONENT_NAME, mask_comp.COMPONENT_NAME])
            self._area = self._sprite_comp.get_size()
            self._rect.size = self._area
        if self._has_mask:
            self._mask_comp = gameobject.get_component([mask_comp.COMPONENT_NAME])
            self._area = self._mask_comp._rect.size
            self._rect.size = self._area
        
        self._hitbox = gameobject.get_component([hitbox_comp.COMPONENT_NAME])
        self._has_hitbox = self._hitbox != None

        # set initial pos
        self._rect.center = gameobject.position
    
    # ---------------------------- #
    # logic
    
    def get_hitbox(self) -> "hitbox_comp.HitboxComponent":
        """ Get the hitbox component """
        if not self._has_hitbox:
            return self._rect
        return pygame.FRect(
            self._hitbox._rect.topleft + self._parent_gameobject.position,
            self._hitbox._rect.size
        )
    
    # ---------------------------- #
    # serialize
    
    def __getstate__(self):
        """ Pickle state """
        state = self.__dict__.copy()
        return state

    def __setstate__(self, state):
        """ Unpickle state """
        self.__dict__.update(state)


# ---------------------------- #
# aspect

class WorldRectAspect(aspect.Aspect):
    def __init__(self):
        """ Create a new World Rect Aspect """
        super().__init__(priority=3, target_component_classes=[WorldRectComponent])
    
    # ---------------------------- #
    # logic

    def handle_rect(self, _world, _rect_comp):
        """ Handle the rect to rect collision """
        _gameobject = _rect_comp.get_gameobject()
        _layer = _world.get_layer_at(_gameobject.zlayer)

        # add acceleration
        _rect_comp._velocity += _rect_comp._acceleration * 0.5 * singleton.DELTA_TIME

        # cache
        _tentative_rect = pygame.FRect(
            _rect_comp._rect.topleft,
            _rect_comp._area
        )
        _center_chunk = world.get_chunk_from_pixel_position(_gameobject.position)
        
        _rect_comp._touching[0] = False
        _rect_comp._touching[1] = False
        _rect_comp._touching[2] = False
        _rect_comp._touching[3] = False

        # x-axis movement
        _tentative_rect.x += _rect_comp._velocity.x * singleton.DELTA_TIME
        for dx, dy in singleton.ITER_CHUNK_3x3:
            cx, cy = _center_chunk[0] + dx, _center_chunk[1] + dy
            # get chunk
            if (_chunk := _layer.get_chunk_at((cx, cy))) == None:
                continue
            # check if gameobject even contact with chunk
            if not phandler.collide_rect_to_rect(_tentative_rect, _chunk._chunk_rect):
                continue

            # check if gameobject collides with any tiles in chunk
            for _collided_tile in _chunk.collide_tiles(_tentative_rect):
                if not phandler.is_collision_masks_overlap(_collided_tile._collision_mask, _rect_comp._collision_mask):
                    continue
                
                if _rect_comp._velocity.x > 0:
                    _tentative_rect.right = _collided_tile._rect.left
                    _rect_comp._velocity.x = 0
                    _rect_comp._touching[physics_comp.TOUCHING_RIGHT] = True
                elif _rect_comp._velocity.x < 0:
                    _tentative_rect.left = _collided_tile._rect.right
                    _rect_comp._velocity.x = 0
                    _rect_comp._touching[physics_comp.TOUCHING_LEFT] = True

                _collided_tile.on_collision(_gameobject)
        
        # y-axis movement
        _tentative_rect.y += _rect_comp._velocity.y * singleton.DELTA_TIME
        for dx, dy in singleton.ITER_CHUNK_3x3:
            cx, cy = _center_chunk[0] + dx, _center_chunk[1] + dy
            # get chunk
            if (_chunk := _layer.get_chunk_at((cx, cy))) == None:
                continue
            # check if gameobject even contact with chunk
            if not phandler.collide_rect_to_rect(_tentative_rect, _chunk._chunk_rect):
                continue

            # check if gameobject collides with any tiles in chunk
            for _collided_tile in _chunk.collide_tiles(_tentative_rect):
                if not phandler.is_collision_masks_overlap(_collided_tile._collision_mask, _rect_comp._collision_mask):
                    continue

                if _rect_comp._velocity.y > 0:
                    _tentative_rect.bottom = _collided_tile._rect.top
                    _rect_comp._velocity.y = 0
                    _rect_comp._touching[physics_comp.TOUCHING_BOTTOM] = True
                elif _rect_comp._velocity.y < 0:
                    _tentative_rect.top = _collided_tile._rect.bottom
                    _rect_comp._velocity.y = 0
                    _rect_comp._touching[physics_comp.TOUCHING_TOP] = True

                _collided_tile.on_collision(_gameobject)

        # add acceleration again
        _rect_comp._velocity += _rect_comp._acceleration * 0.5 * singleton.DELTA_TIME

        # update final coordinates
        _rect_comp._rect.topleft = _tentative_rect.topleft
        _gameobject.position.xy = _tentative_rect.center

    def handle_hitbox(self, _world, _rect_comp):
        """ Handle the mask to rect collision """
        _gameobject = _rect_comp.get_gameobject()
        _layer = _world.get_layer_at(_gameobject.zlayer)
        _hitbox = _rect_comp._hitbox

        # add acceleration
        _rect_comp._velocity += _rect_comp._acceleration * 0.5 * singleton.DELTA_TIME

        # cache
        _tentative_rect = pygame.FRect(
            _hitbox._rect.topleft + _gameobject.position,
            _hitbox._rect.size
        )
        _center_chunk = world.get_chunk_from_pixel_position(_gameobject.position)
        
        _rect_comp._touching[0] = False
        _rect_comp._touching[1] = False
        _rect_comp._touching[2] = False
        _rect_comp._touching[3] = False

        # x-axis movement
        _tentative_rect.x += _rect_comp._velocity.x * singleton.DELTA_TIME
        for dx, dy in singleton.ITER_CHUNK_3x3:
            cx, cy = _center_chunk[0] + dx, _center_chunk[1] + dy
            # get chunk
            if (_chunk := _layer.get_chunk_at((cx, cy))) == None:
                continue
            # check if gameobject even contact with chunk
            if not phandler.collide_rect_to_rect(_tentative_rect, _chunk._chunk_rect):
                continue

            # check if gameobject collides with any tiles in chunk
            for _collided_tile in _chunk.collide_tiles(_tentative_rect):
                if not phandler.is_collision_masks_overlap(_collided_tile._collision_mask, _rect_comp._collision_mask):
                    continue

                _collided_tile.on_collision(_gameobject)
                if _collided_tile._transparent:
                    continue
                
                if _rect_comp._velocity.x > 0:
                    _tentative_rect.right = _collided_tile._rect.left
                    _rect_comp._velocity.x = 0
                    _rect_comp._acceleration.x = 0
                    _rect_comp._touching[physics_comp.TOUCHING_RIGHT] = True
                elif _rect_comp._velocity.x < 0:
                    _tentative_rect.left = _collided_tile._rect.right
                    _rect_comp._velocity.x = 0
                    _rect_comp._acceleration.x = 0
                    _rect_comp._touching[physics_comp.TOUCHING_LEFT] = True
                
        # y-axis movement
        _tentative_rect.y += _rect_comp._velocity.y * singleton.DELTA_TIME
        for dx, dy in singleton.ITER_CHUNK_3x3:
            cx, cy = _center_chunk[0] + dx, _center_chunk[1] + dy
            # get chunk
            if (_chunk := _layer.get_chunk_at((cx, cy))) == None:
                continue
            # check if gameobject even contact with chunk
            if not phandler.collide_rect_to_rect(_tentative_rect, _chunk._chunk_rect):
                continue

            # check if gameobject collides with any tiles in chunk
            for _collided_tile in _chunk.collide_tiles(_tentative_rect):
                if not phandler.is_collision_masks_overlap(_collided_tile._collision_mask, _rect_comp._collision_mask):
                    continue
                
                _collided_tile.on_collision(_gameobject)
                if _collided_tile._transparent:
                    continue
                
                if _rect_comp._velocity.y > 0:
                    _tentative_rect.bottom = _collided_tile._rect.top
                    _rect_comp._velocity.y = 0
                    _rect_comp._acceleration.y = 0
                    _rect_comp._touching[physics_comp.TOUCHING_BOTTOM] = True
                elif _rect_comp._velocity.y < 0:
                    _tentative_rect.top = _collided_tile._rect.bottom
                    _rect_comp._velocity.y = 0
                    _rect_comp._acceleration.y = 0
                    _rect_comp._touching[physics_comp.TOUCHING_TOP] = True


        # add acceleration again
        _rect_comp._velocity += _rect_comp._acceleration * 0.5 * singleton.DELTA_TIME

        # update final coordinates
        _gameobject.position.xy  = (
            _tentative_rect.x - _hitbox._rect.x,
            _tentative_rect.y - _hitbox._rect.y
        )
        _rect_comp._rect.center = _gameobject.position

    def handle(self, camera: "Camera"):
        """ Handle the aspect """
        _world = self._handler._world

        for _rect_comp in self.iter_components():
            # check if rect to rect or bitmask to rect
            if _rect_comp._has_hitbox:
                self.handle_hitbox(_world, _rect_comp)
            else:
                self.handle_rect(_world, _rect_comp)
            
            # reset acceleration
            _rect_comp._acceleration.xy = (0, 0)


class WorldRectDebugAspect(aspect.Aspect):

    def __init__(self):
        """ Create a new World Rect Debug Aspect """
        super().__init__(priority=1, target_component_classes=[WorldRectComponent])
    
    # ---------------------------- #
    # logic

    def handle(self, camera: "Camera"):
        """ Handle the aspect """
        if not singleton.DEBUG:
            return

        for _rect_comp in self.iter_components():
            _gameobject = _rect_comp.get_gameobject()
            _layer_surface = _gameobject._parent_phandler._world.get_layer_at(_gameobject.zlayer)._layer_buffer
            
            # render rect into world
            _pos = _rect_comp._rect.topleft - camera.position
            pygame.draw.rect(
                _layer_surface,
                (255, 255, 0), 
                (_pos, _rect_comp._rect.size),
                1
            )

# ---------------------------- #
# utils



# caching the component
component.ComponentHandler.cache_component_class(WorldRectComponent)


