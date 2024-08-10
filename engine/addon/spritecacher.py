
import pygame

from engine import io

from engine.graphics import spritesheet


# ---------------------------- #
# sprite cacher (glorified dictionary)

class SpriteCacher:
    def __init__(self, size: pygame.Rect) -> None:
        """ Initialize the sprite cacher """
        self._cached_sprites = {}
        self._size = size
        
    # ---------------------------- #
    # caching functions
    
    def load_sprite(self, path: str, cut_rect: pygame.Rect = None) -> pygame.Surface:
        """ Load a sprite and cache it """
        if path in self._cached_sprites:
            return self._cached_sprites[path]
        
        # check if sprite is an image or spritesheet
        if '|' in path:
            spritesheet.load_spritesheet(path.split(spritesheet.SPRITESHEET_PADDING)[0])
        
        sprite = io.load_image(path)
        if cut_rect:
            sprite = sprite.subsurface(cut_rect).copy()
        # TODO - consider simply using opengl to just render the images instead of caching them
        self[path] = pygame.transform.scale(sprite, self._size)
        return sprite
        
    # ---------------------------- #
    # utils
        
    def __getitem__(self, key):
        """ Get the sprite """
        return self._cached_sprites[key]
    
    def __setitem__(self, key, value):
        """ Set the sprite """
        self._cached_sprites[key] = value

