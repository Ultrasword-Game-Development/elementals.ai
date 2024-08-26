

from engine.handler import world

from game import singleton

from game.entities import entity


# ---------------------------- #
# constants

LADDER_SPRITE = "assets/sprites/entities/ladder.png"

# ---------------------------- #
# ladder

class LadderTile(world.DefaultTile):
    def __init__(self, position: tuple):
        """ Create a new ladder tile """
        super().__init__(position=position, sprite=LADDER_SPRITE, transparent=True)
        
        self.set_mask_value(singleton.BASIC_COLLISION_LAYER, True)
        self.set_mask_value(singleton.LADDER_COLLISION_LAYER, True)

    def __post_init__(self, chunk: "world.Chunk"):
        """ Post init """
        print('ladder rect: ', self._rect)

    # ---------------------------- #
    # logic

    def on_collision(self, gameobject: "GameObject"):
        """ On collision with a gameobject """

        if issubclass(gameobject.__class__, entity.Entity):
            gameobject._can_climb = True
            



