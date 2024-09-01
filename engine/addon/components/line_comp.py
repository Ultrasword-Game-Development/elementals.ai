
import pygame

from engine import io
from engine import singleton

from engine.handler import world
from engine.handler import aspect
from engine.handler import component

from engine.physics import phandler

from engine.addon.components import renderable_comp
from engine.addon.components import animation_comp
from engine.addon.components import hitbox_comp

# ---------------------------- #
# constants

COMPONENT_NAME = "LineComponent"

CHUNK_STEP_LENGTH = int(singleton.DEFAULT_CHUNK_PIXEL_WIDTH * 0.3)


# ---------------------------- #
# component

class LineComponent(component.Component):
    
    def __init__(self, start: "Vector2", end: "Vector2", zlayer: int = 0, tilecast: bool = False, entitycast: bool = False):
        super().__init__()

        self._start = pygame.math.Vector2(start)
        self._end = pygame.math.Vector2(end)
        self._zlayer = zlayer

        self._entity_cast = entitycast
        self._tile_cast = tilecast

        self._collidedentities = []
        self._collidedtiles = []

    def __post_gameobject__(self, gameobject: "GameObject"):
        """ Post init function """
        super().__post_gameobject__(gameobject)
    
    # ---------------------------- #
    # logic

    def get_zlayer(self):
        """ Get the zlayer """
        return self._zlayer
    
    def get_start(self):
        """ Get the start """
        return self._start
    
    def get_end(self):
        """ Get the end """
        return self._end
    
    def set_start(self, start: "Vector2"):
        """ Set the start """
        self._start = start
    
    def set_end(self, end: "Vector2"):
        """ Set the end """
        self._end = end
    
    def set_zlayer(self, zlayer: int):
        """ Set the zlayer """
        self._zlayer = zlayer
    

# ---------------------------- #
# aspect

class LineAspect(aspect.Aspect):

    def __init__(self):
        super().__init__(target_component_classes=[LineComponent])
        self._hitbox_aspect = None
        self._world = None
    
    def __post_init__(self):
        """ Post init function """
        # grab the hitbox component
        self._hitbox_aspect = self._handler.get_aspect(hitbox_comp.HitboxAspect)
        self._world = self._handler._world
    
    # ---------------------------- #
    # logic

    def handle(self, camera: "Camera"):
        """ Handle the aspect """
        for _comp in self.iter_components():
            # check which tiles / entities collide with the line
            _layer = self._handler._world.get_layer_at(_comp.get_zlayer())
            _gameobject = _comp._parent_gameobject

            _comp._collidedentities.clear()
            _comp._collidedtiles.clear()

            if _comp._entity_cast:
                for _hitbox in self._hitbox_aspect.iter_components():
                    if phandler.collide_line_to_rect((_comp.get_start(), _comp.get_end()), _hitbox.get_rect(), 0):
                        _comp._collidedentities.append(_hitbox._parent_gameobject)

            if _comp._tile_cast:
                _start_chunk = world.get_chunk_from_pixel_position(_comp.get_start() + _gameobject.position)
                _direction = pygame.math.Vector2((
                    _comp.get_end()[0] - _comp.get_start()[0],
                    _comp.get_end()[1] - _comp.get_start()[1]
                ))
                _distance = _direction.magnitude()
                _layer = self._world.get_layer_at(_comp.get_zlayer())

                _travel = 0
                chunks_to_check = []

                current = pygame.math.Vector2(_comp.get_start() + _gameobject.position)
                while _travel < _distance:
                    chunks_to_check.append(_layer.get_chunk_at(world.get_chunk_from_pixel_position(current)))

                    current += _direction.normalize() * CHUNK_STEP_LENGTH
                    _travel += CHUNK_STEP_LENGTH
                
                __last_chunk = _layer.get_chunk_at(world.get_chunk_from_pixel_position(_comp.get_end() + _gameobject.position))
                if chunks_to_check[-1] != __last_chunk:
                    chunks_to_check.append(_layer.get_chunk_at(world.get_chunk_from_pixel_position(_comp.get_end() + _gameobject.position)))
                
                # travel down the slope
                slope = pygame.math.Vector2(_comp.get_end()) - _comp.get_start()
                slope = slope.normalize() * singleton.DEFAULT_TILE_WIDTH
                _magnitude = slope.magnitude()
                dx, dy = slope.x, slope.y
                _startpos = list(_comp.get_start() + _gameobject.position)
                _travel = 0

                for chunk in chunks_to_check:
                    if not chunk:
                        continue
                    # walk thorugh chunk
                    while phandler.collide_point_to_rect(_startpos, chunk._chunk_rect) and _distance > _travel:
                        _tilepos = world.pixel_to_tile_coords(_startpos)

                        # add tile to list of tiles
                        result = _layer.get_tile_at(_tilepos)
                        if result:
                            _comp._collidedtiles.append(result)

                        # draw a circle at the point we are checking
                        pygame.draw.circle(
                            _layer._layer_buffer, (255, 0, 0), _startpos - camera.position, 2
                        )

                        _startpos[0] += dx
                        _startpos[1] += dy
                        _travel += _magnitude


class LineDebugAspect(aspect.Aspect):

    def __init__(self):
        super().__init__(target_component_classes=[LineComponent])
    
    # ---------------------------- #
    # logic

    def handle(self, camera: "Camera"):
        """ Handle the aspect """
        for _comp in self.iter_components():
            # draw the line
            _gameobject = _comp._parent_gameobject
            _start = _comp.get_start() + _gameobject.position
            _end = _comp.get_end() + _gameobject.position

            pygame.draw.line(
                _gameobject._parent_phandler._world.get_layer_at(_gameobject.zlayer)._layer_buffer, 
                (0, 255, 255), 
                _start - camera.position, 
                _end - camera.position, 
                1
            )





# ---------------------------- #
# utils




# caching the component class
component.ComponentHandler.cache_component_class(LineComponent)
