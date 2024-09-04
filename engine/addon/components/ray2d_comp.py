
import pygame

from engine import io
from engine import utils
from engine import singleton

from engine.handler import world
from engine.handler import aspect
from engine.handler import component

from engine.physics import phandler

from engine.addon.components import renderable_comp
from engine.addon.components import animation_comp
from engine.addon.components import line_comp
from engine.addon.components import hitbox_comp
from engine.addon.components import rect_comp

# ---------------------------- #
# constants

COMPONENT_NAME = "Ray2DComponent"

# ---------------------------- #
# component

class Ray2DComponent(line_comp.LineComponent):
    
    def __init__(self, start: "Vector2", magnitude: float, angle: float, zlayer: int = 0, tilecast: bool = False, entitycast: bool = False):
        super().__init__(
            start = start, 
            end = pygame.math.Vector2(1, 0).rotate(angle) * magnitude, 
            zlayer = zlayer, 
            tilecast = tilecast, 
            entitycast = entitycast
        )

        self._angle = angle
        self._magnitude = magnitude
        self._n_direction = pygame.math.Vector2(1, 0).rotate(angle)

        self._cast_end = pygame.math.Vector2(0, 0)
        
    def __post_gameobject__(self, gameobject: "GameObject"):
        """ Post init function """
        super().__post_gameobject__(gameobject)


# ---------------------------- #
# aspect

class Ray2DAspect(aspect.Aspect):

    def __init__(self):
        super().__init__(target_component_classes=[Ray2DComponent])
    
    def __post_init__(self):
        """ Post init function """
        # grab the hitbox component
        self._hitbox_aspect = self._handler.get_aspect(hitbox_comp.HitboxAspect)
        self._rect_aspect = self._handler.get_aspect(rect_comp.WorldRectAspect)
        self._world = self._handler._world

    # ---------------------------- #
    # logic

    def handle(self, camera: "Camera"):
        """ Handle the aspect """
        for _comp in self.iter_components():
            # grab first entity / tile that collides with the object
            _layer = self._handler._world.get_layer_at(_comp.get_zlayer())
            _gameobject = _comp.get_gameobject()

            _comp._collidedentities.clear()
            _comp._collidedtiles.clear()
            _comp._cast_end = _comp.get_start() + _comp._n_direction * _comp._magnitude

            if _comp._tile_cast:
                _current_chunk_coords = world.get_chunk_from_pixel_position(_comp.get_start() + _gameobject.position)
                _current_pos = _comp.get_start() + _gameobject.position
                _travel = 0
                _comp._cast_end.xy = _comp._start + _comp._n_direction * _comp._magnitude + _gameobject.position

                while _travel < _comp._magnitude:
                    # check current tile
                    _tilecoords = world.pixel_to_tile_coords(_current_pos)
                    _ctile = _layer.get_tile_at(_tilecoords)

                    # check if tile exists / if a collision exists
                    if _ctile is not None:
                        _comp._collidedtiles.append(_ctile)
                        _comp._cast_end.xy = _current_pos
                        _travel = _comp._magnitude + 1e9
                        break
                    
                    # else move the current position
                    _current_pos += _comp._n_direction * singleton.DEFAULT_TILE_WIDTH * 0.5
                    _travel += singleton.DEFAULT_TILE_WIDTH * 0.5
                
            if _comp._entity_cast:
                # TODO - optimize later -- REWRITE
                _closest = None
                _closest_distance = 1e9

                for rect in self._rect_aspect.iter_components():
                    # check if self
                    if rect.get_gameobject()._id == _gameobject._id:
                        continue
                    
                    # check if this is a closer hitbox
                    _distance = pygame.math.Vector2(rect.get_gameobject().position - _gameobject.position).magnitude()
                    if _distance > _closest_distance:
                        continue
                    
                    # check for collision
                    if phandler.collide_line_to_rect((_comp.get_start() + _gameobject.position, _comp.get_end() + _gameobject.position), rect.get_hitbox(), 0):
                        if _distance > _comp._magnitude:
                            continue
                        _closest = rect
                        _closest_distance = _distance
                
                # found closest entity
                _comp._collidedentities.append(_closest.get_gameobject()) if _closest is not None else None


class Ray2DDebugAspect(aspect.Aspect):
    def __init__(self):
        super().__init__(priority=-1, target_component_classes=[Ray2DComponent])
    
    # ---------------------------- #
    # logic

    def handle(self, camera: "Camera"):
        """ Render all the rays """
        for _comp in self.iter_components():
            _layer = self._handler._world.get_layer_at(_comp.get_zlayer())
            _start = _comp.get_start() - camera.position + _comp.get_gameobject().position
            _end = _comp._cast_end - camera.position

            # render the base line
            pygame.draw.line(_layer._layer_buffer, (0, 0, 255), _start, _start + _comp._n_direction * _comp._magnitude, 1)

            if _comp._tile_cast:
                pygame.draw.line(_layer._layer_buffer, (255, 0, 0), _start, _end, 1)

            if _comp._entity_cast:

                # print(_comp._collidedentities, singleton.ACTIVE_TIME)
                if _comp._collidedentities != []:
                    # draw a single line
                    pygame.draw.line(
                        _layer._layer_buffer, 
                        (0, 255, 0),
                        _start, 
                        _comp._collidedentities[0].position - camera.position, 
                        1
                    )
            
        # print()



# ---------------------------- #
# utils




# caching the component class
component.ComponentHandler.cache_component_class(Ray2DComponent)
