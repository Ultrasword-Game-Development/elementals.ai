

import pygame

from engine import io
from engine import utils
from engine import singleton

from engine.handler import component
from engine.handler import aspect

from engine.addon import components

from game import singleton as game_singleton

# ---------------------------- #
# constants

COMPONENT_NAME = "PlayerComponent"

# ---------------------------- #
# component

class PlayerComponent(component.Component):
    
    def __init__(self, _main_player: bool = True, inputs_config: dict = {
        "w": pygame.K_w,
        "a": pygame.K_a,
        "s": pygame.K_s,
        "d": pygame.K_d,
    }):
        """ Initialize the Player Component """
        super().__init__()

        self._input_config = inputs_config
        self._main_player = _main_player
    
    # ---------------------------- #
    # logic

    def __post_gameobject__(self, _parent_gameobject: "GameObject"):
        """ Called after being added to a gameobject """
        super().__post_gameobject__(_parent_gameobject)

        # set the player object
        if self._main_player:
            game_singleton.PLAYER_ENTITY = self._parent_gameobject
    
    # ---------------------------- #
    # dill

    def __getstate__(self):
        """ Get the state of the component """
        _state = super().__getstate__()
        return _state
    
    def __setstate__(self, state: dict):
        """ Set the state of the component """
        super().__setstate__(state)
        game_singleton.PLAYER_ENTITY = self._parent_gameobject



# ---------------------------- #
# aspect

class PlayerAspect(aspect.Aspect):

    def __init__(self):
        """ Initialize the Sprite Renderer Aspect """
        super().__init__(target_component_classes=[PlayerComponent])

    # ---------------------------- #
    # logic
    
    def handle(self, camera: "Camera"):
        """ Handle the Sprite Renderer aspect """
        for _c in self.iter_components():
            self._handle_player_code(_c)
    
    def _handle_player_code(self, player_comp: PlayerComponent):
        """ Handle the player code """
        _gameobject = player_comp.get_gameobject()

        # update movement
        if io.get_key_pressed(player_comp._input_config["a"]):
            _gameobject._rect_comp._acceleration.x += -_gameobject._agility
        if io.get_key_pressed(player_comp._input_config["d"]):
            _gameobject._rect_comp._acceleration.x += _gameobject._agility
        
        if _gameobject._rect_comp._touching[components.physics_comp.TOUCHING_BOTTOM] and io.get_key_pressed(pygame.K_SPACE):
            _gameobject._rect_comp._velocity.y = -200
        
        # touching ladders
        if _gameobject._can_climb and not io.get_key_pressed(pygame.K_LSHIFT):
            # cancel gravity
            _gameobject._rect_comp._acceleration -= game_singleton.GAME_GRAVITY
            
            # climbing up + down
            if io.get_key_pressed(pygame.K_w) or io.get_key_pressed(pygame.K_SPACE):
                _gameobject._rect_comp._acceleration.y += -_gameobject._climbing_factor * _gameobject._agility
            if io.get_key_pressed(pygame.K_s):
                _gameobject._rect_comp._acceleration.y += _gameobject._climbing_factor * _gameobject._agility 
        
        # set flipx
        _gameobject._sprite_comp.set_flipx(_gameobject._rect_comp._velocity.x < 0)

        # set animation)
        _velocity_mag = _gameobject._rect_comp._velocity.length()
        if _velocity_mag < 5:
            # is idle
            _gameobject._animation_comp.set_animation_type("Idle")
        else:
            # is walking
            _gameobject._animation_comp.set_animation_type("Walk")
        
        # clamp max speed
        _gameobject._rect_comp._velocity.x = utils.clamp(_gameobject._rect_comp._velocity.x, -game_singleton.MAX_GAMEOBJECT_SPEED, game_singleton.MAX_GAMEOBJECT_SPEED)
        _gameobject._rect_comp._velocity.y = utils.clamp(_gameobject._rect_comp._velocity.y, -game_singleton.MAX_GAMEOBJECT_SPEED, game_singleton.MAX_GAMEOBJECT_SPEED)

        # reset stats
        _gameobject._can_climb = False

# ---------------------------- #
# utils




# caching the component class
component.ComponentHandler.cache_component_class(PlayerComponent)
