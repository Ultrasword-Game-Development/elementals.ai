

from engine.handler import world

from game import singleton


# ---------------------------- #
# constants

LADDER_SPRITE = "assets/sprites/entities/ladder.png"

# ---------------------------- #
# ladder

class LadderTile(world.DefaultTile):
    def __init__(self, position: tuple):
        """ Create a new ladder tile """
        super().__init__(position=position, sprite=LADDER_SPRITE)
        
        self.set_mask_value(singleton.BASIC_COLLISION_LAYER, False)
        self.set_mask_value(singleton.LADDER_COLLISION_LAYER, True)

    def __post_init__(self, chunk: "world.Chunk"):
        """ Post init """
        print('ladder rect: ', self._rect)

    # ---------------------------- #
    # logic
    
    def update(self):
        """ Update the ladder """
        # print(self._rect, end='\t')
        
        # check if the player object is colliding against it
        if singleton.PLAYER_ENTITY._rect_comp.get_hitbox().colliderect(self._rect):
            # if colliding, check if player is climbing
            singleton.PLAYER_ENTITY._can_climb = True
            



