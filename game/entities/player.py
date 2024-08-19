
import math
import pygame


from engine import io
from engine import singleton

from engine.physics import gameobject

from engine.addon import components


# ---------------------------- #
# constants



# ---------------------------- #
# player

class Player(gameobject.GameObject):
    
    def __init__(self, x: int, y: int):
        super().__init__(position=(x, y))
        
        # add components
        self._sprite_comp = self.add_component(components.sprite_comp.SpriteComponent())
        self._animation_comp = self.add_component(components.animation_comp.AnimationComponent("assets/sprites/entities/player.json"))
        self._hitbox_comp = self.add_component(components.hitbox_comp.HitBoxComponent())
        self._rect_comp = self.add_component(components.rect_comp.WorldRectComponent())
        
        self.add_component(components.spriterenderer_comp.SpriteRendererComponent())

        components.particlehandler_comp.register_particle_function_combination("playertest", update_func=_DEFAULT_UPDATE_PARTICLE)
        self.add_component(components.particlehandler_comp.ParticleHandlerComponent(update_func_str="playertest", zlayer=-2))
        
        # set up hitbox
        self._hitbox_comp.set_offset((3, 3))
        self._hitbox_comp.set_area((10, 13))
                
        # set up animation
        self._animation_comp.set_animation_type("idle")
    
    # ---------------------------- #
    # logic

    def update(self):
        """ Update the player """
        super().update()
        
        # update movement
        if io.get_key_pressed(pygame.K_a):
            self._rect_comp._velocity.x += -1 * 40 * singleton.DELTA_TIME
        if io.get_key_pressed(pygame.K_d):
            self._rect_comp._velocity.x += 1 * 40 * singleton.DELTA_TIME
        if io.get_key_pressed(pygame.K_w):
            self._rect_comp._velocity.y += -1 * 40 * singleton.DELTA_TIME
        if io.get_key_pressed(pygame.K_s):
            self._rect_comp._velocity.y += 1 * 40 * singleton.DELTA_TIME

    
        
        
# testing

def _DEFAULT_UPDATE_PARTICLE(self, surface: pygame.Surface, camera: "Camera"):
    """ Update all particles """
    for _particle in self._particles.values():
        _particle[1] += _particle[2] * singleton.DELTA_TIME
        _particle[3] -= singleton.DELTA_TIME

        _pos = _particle[1] - camera.position
        # render particle
        pygame.draw.circle(surface, (_pos.x % 255, _pos.y % 255, (math.sin(singleton.ACTIVE_TIME) * 127) + 127), _pos, 2)

        if _particle[3] <= 0:
            self._particle_delete_queue.add(_particle[0])



