
from engine import singleton

from engine.handler import world


# ---------------------------- #
# constants



# ---------------------------- #
# animated - semi-dynamic tiles

class SemiAnimatedTile(world.DefaultTile):
    def __init__(self, animation: str, position: tuple, sprite: str, width: int = singleton.DEFAULT_TILE_WIDTH, height: int = singleton.DEFAULT_TILE_HEIGHT) -> None:
        super().__init__(position, sprite, width, height)
        self._animation_id = animation
        self._animation_registry = None
        
        # make sure spritesheet is loaded
        

    def update(self):
        """ Update the tile """
        pass

# ---------------------------- #
# animated - dynamic tiles

class AnimatedTile(world.DefaultTile):
    def __init__(self, position: tuple, sprite: str, width: int = singleton.DEFAULT_TILE_WIDTH, height: int = singleton.DEFAULT_TILE_HEIGHT) -> None:
        super().__init__(position, sprite, width, height)

    def update(self):
        """ Update the tile """
        pass
    

