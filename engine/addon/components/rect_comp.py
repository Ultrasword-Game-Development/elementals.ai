
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
            self._area = self._sprite_comp.get_sprite().get_size()
        if self._has_mask:
            self._mask_comp = gameobject.get_component([mask_comp.COMPONENT_NAME])
        
        self._hitbox = gameobject.get_component([hitbox_comp.COMPONENT_NAME ])
        self._has_hitbox = self._hitbox != None


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

        # cache
        _tentative_rect = pygame.FRect(_gameobject.position, _rect_comp._area)
        _center_chunk = world.get_chunk_from_pixel_position(_gameobject.position)

        # x-axis movement
        _tentative_rect.x += _rect_comp._velocity.x
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
                # check if collided tile is solid
                if not _collided_tile._solid:
                    continue

                if _rect_comp._velocity.x > 0:
                    _tentative_rect.right = _collided_tile._rect.left
                elif _rect_comp._velocity.x < 0:
                    _tentative_rect.left = _collided_tile._rect.right
        
        # y-axis movement
        _tentative_rect.y += _rect_comp._velocity.y
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
                # check if collided tile is solid
                if not _collided_tile._solid:
                    continue

                if _rect_comp._velocity.y > 0:
                    _tentative_rect.bottom = _collided_tile._rect.top
                elif _rect_comp._velocity.y < 0:
                    _tentative_rect.top = _collided_tile._rect.bottom

        # update final coordinates
        _gameobject.position.xy = _tentative_rect.topleft

    def handle_hitbox(self, _world, _rect_comp):
        """ Handle the mask to rect collision """
        _gameobject = _rect_comp.get_gameobject()
        _layer = _world.get_layer_at(_gameobject.zlayer)
        _hitbox = _rect_comp._hitbox

        # cache
        _tentative_rect = pygame.FRect(
            _gameobject.position + _hitbox._rect.topleft,
            _hitbox._rect.size
        )
        _center_chunk = world.get_chunk_from_pixel_position(_gameobject.position)

        # x-axis movement
        _tentative_rect.x += _rect_comp._velocity.x
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
                # TODO - change to bitmask
                if phandler.is_collision_masks_overlap(_collided_tile._collision_mask, _rect_comp._collision_mask):
                    continue

                if _rect_comp._velocity.x > 0:
                    _tentative_rect.right = _collided_tile._rect.left
                elif _rect_comp._velocity.x < 0:
                    _tentative_rect.left = _collided_tile._rect.right
        
        # y-axis movement
        _tentative_rect.y += _rect_comp._velocity.y
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
                # TODO - change to bitmask
                if phandler.is_collision_masks_overlap(_collided_tile._collision_mask, _rect_comp._collision_mask):
                    continue

                if _rect_comp._velocity.y > 0:
                    _tentative_rect.bottom = _collided_tile._rect.top
                elif _rect_comp._velocity.y < 0:
                    _tentative_rect.top = _collided_tile._rect.bottom

        # update final coordinates
        _gameobject.position.xy = (
            _tentative_rect.x - _hitbox._rect.left,
            _tentative_rect.y - _hitbox._rect.top
        )


    def handle(self):
        """ Handle the aspect """
        _world = self._handler._world

        for _rect_comp in self.iter_components():
            # check if rect to rect or bitmask to rect
            if _rect_comp._has_hitbox:
                self.handle_hitbox(_world, _rect_comp)
            else:
                self.handle_rect(_world, _rect_comp)
            # render debug?
            if _rect_comp._has_hitbox and singleton.DEBUG:
                pygame.draw.rect(_world.get_layer_at(_rect_comp.get_gameobject().zlayer)._layer_buffer, (0, 255, 0), 
                        (_rect_comp.get_gameobject().position + _rect_comp._hitbox._rect.topleft - self._handler._world._camera.position, _rect_comp._hitbox._rect.size), 1)
            

# ---------------------------- #
# utils



# caching the component
component.ComponentHandler.cache_component_class(WorldRectComponent)


