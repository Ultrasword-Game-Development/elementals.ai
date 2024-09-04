import pygame

from engine import utils

from engine.handler import world
from engine.handler import signal


# ---------------------------- #
# constants

DEATH_SIGNAL_NAME = "_physics_death_signal"
DEATH_SIGNAL_ID = "_physics_death_signal_id"


# ---------------------------- #
# physics / gameobject handler

class PhysicsHandler:
    def __init__(self, _world: "World") -> None:
        """ Initialize the physics handler """
        self._world = _world
        self._gameobjects = {}
        self._components = []

        # death signal
        self._death_signal = signal.Signal(DEATH_SIGNAL_NAME)
        self._death_signal.add_emitter_handling_function(DEATH_SIGNAL_ID, self.handle_death_signal)

        # gameobjects + chunks
        self._gameobject_chunks = {}
    
    def __post_init__(self):
        """ Post init function """
        self.load_components()

    # ---------------------------- #
    # logic

    def update(self):
        """ Update the physics handler """
        # update physics world components
        for component in self._components:
            component.update() if component._active else None
        for gameobject in self._gameobjects.values():
            gameobject.update()
    
    def add_component(self, component: "PhysicsComponent"):
        """ Add an component to the physics handler """
        self._components.append(component)
        component.__post_init__(self)  

        return component
            
    def add_gameobject(self, gameobject: "GameObject"):
        """ Add an gameobject to the physics handler """
        self._gameobjects[hash(gameobject)] = gameobject
        gameobject._parent_phandler = self
        # add death signal
        gameobject._death_emitter = self._death_signal.get_unique_emitter()
        # setup gameobject chunk
        self.update_gameobject_chunk(gameobject, gameobject.position)
        # post init
        gameobject.__post_init__()
    
    def update_gameobject_chunk(self, gameobject: "GameObject", _new_position: "Vector2"):
        """ Update the gameobject chunk """
        # remove gameobject from old chunk
        _old_chunk = world.get_chunk_from_pixel_position(gameobject.position)
        if _old_chunk in self._gameobject_chunks:
            self._gameobject_chunks[_old_chunk].remove(gameobject._id)
        # add gameobject to new chunk
        _chunk_coords = world.get_chunk_from_pixel_position(_new_position)
        if not _chunk_coords in self._gameobject_chunks:
            self._gameobject_chunks[_chunk_coords] = set()
        self._gameobject_chunks[_chunk_coords].add(gameobject._id)
    
    def get_gameobject(self, gameobject_hash: int):
        """ Get an gameobject by id """
        return self._gameobjects[gameobject_hash]
    
    def handle_death_signal(self, data: dict):
        """ 
        Handle the death signal 
        
        Data found in `data`:
        - id: int
        - data: dict (containing whatever lol)
        """
        
        # get chunk + remove entity from chunk
        _chunk_coords = world.get_chunk_from_pixel_position(self._gameobjects[data['id']].position)
        # remove gameobject from chunk cache
        self._gameobject_chunks[_chunk_coords].remove(self._gameobjects[data['id']])


        self._gameobjects[data['id']]._alive = False
        # run the custom gameobject death function
        self._gameobjects[data['id']].handle_death_signal(data)
        
        # remove the gameobject
        del self._gameobjects[data['id']]
    
    def load_components(self):
        """ Load the components """
        for _gameobject in self._gameobjects.values():
            _gameobject.__post_init__()
        for _comp in self._components:
            _comp.__post_init__(self)
    
    # ---------------------------- #
    # serialize
    
    def __getstate__(self):
        """ Pickle state """
        state = self.__dict__.copy()
        return state
    
    def __setstate__(self, state):
        """ Unpickle state """
        self.__dict__.update(state)
        self.load_components()
    
        
# ---------------------------- #
# utils

def collide_rect_to_rect(rect1: pygame.Rect, rect2: pygame.Rect):
    """ Check if two rects collide """
    return rect1.colliderect(rect2)

def collide_rect_to_bitmask(rect: pygame.Rect, bitmask: pygame.Surface, bitmask_rect: pygame.Rect):
    """ Check if a rect collides with a bitmask """
    if not rect.colliderect(bitmask_rect):
        return False
    # get the overlap
    _rect_mask = pygame.mask.Mask(rect.size, fill=True)
    return _rect_mask.overlap(bitmask, (bitmask_rect.x - rect.x, bitmask_rect.y - rect.y)) != None

def collide_bitmask_to_bitmask(bitmask1: pygame.Surface, bitmask1_rect: pygame.Rect, bitmask2: pygame.Surface, bitmask2_rect: pygame.Rect):
    """ Check if two bitmasks collide """
    if not bitmask1_rect.colliderect(bitmask2_rect):
        return False
    # get the overlap
    # TODO - bitmask + bitmask collision
    return bitmask1.overlap(bitmask2, (bitmask2_rect.x - bitmask1_rect.x, bitmask2_rect.y - bitmask1_rect.y)) != None

def is_collision_masks_overlap(mask1: int, mask2: int):
    """ Check if two collision masks overlap """
    return mask1 & mask2 != 0

def collide_line_to_rect(line: "Tuple(Tuple(start), Tuple(end))", rect: pygame.Rect, rect_rotation: float):
    """ Check if a line collides with a rect """
    _lines = utils.get_rect_lines(rect, rect_rotation)
    for _line in _lines:
        if collide_line_to_line(line, _line):
            return True
    return False

def collide_line_to_rect_aa(line: "Tuple(Tuple(start), Tuple(end))", rect: pygame.Rect):
    """ Check if a line collides with a rect """
    collide_line_to_rect(line, rect, 0)

def collide_line_to_line(line1: "Tuple(Tuple(start), Tuple(end))", line2: "Tuple(Tuple(start), Tuple(end))"):
    """ Check if two lines collide """
    x1 = line1[0][0]
    y1 = line1[0][1]
    x2 = line1[1][0]
    y2 = line1[1][1]
    x3 = line2[0][0]
    y3 = line2[0][1]
    x4 = line2[1][0]
    y4 = line2[1][1]

    ua1 = ((x4-x3)*(y1-y3) - (y4-y3)*(x1-x3))
    ua2 = ((y4-y3)*(x2-x1) - (x4-x3)*(y2-y1))
    ub1 = ((x2-x1)*(y1-y3) - (y2-y1)*(x1-x3))
    ub2 = ((y4-y3)*(x2-x1) - (x4-x3)*(y2-y1))

    ua = ua1 / (ua2 if ua2 != 0 else 1e9)
    ub = ub1 / (ub2 if ub2 != 0 else 1e9)

    # if ua and ub are between 0 and 1, the lines are colliding
    return 0 <= ua <= 1 and 0 <= ub <= 1

def collide_line_to_line_point(line1: "Tuple(Tuple(start), Tuple(end))", line2: "Tuple(Tuple(start), Tuple(end))"):
    """ Check if two lines collide and return the point of collision """
    x1 = line1[0][0]
    y1 = line1[0][1]
    x2 = line1[1][0]
    y2 = line1[1][1]
    x3 = line2[0][0]
    y3 = line2[0][1]
    x4 = line2[1][0]
    y4 = line2[1][1]

    ua = ((x4-x3)*(y1-y3) - (y4-y3)*(x1-x3)) / ((y4-y3)*(x2-x1) - (x4-x3)*(y2-y1))
    ub = ((x2-x1)*(y1-y3) - (y2-y1)*(x1-x3)) / ((y4-y3)*(x2-x1) - (x4-x3)*(y2-y1))

    # if ua and ub are between 0 and 1, the lines are colliding
    if 0 <= ua <= 1 and 0 <= ub <= 1:
        ix = x1 + ua * (x2 - x1)
        yy = y1 + ua * (y2 - y1)
        return (ix, iy)
    return None

def collide_line_to_rects(line: "Tuple(Tuple(start), Tuple(end))", rects: "List[pygame.Rect]"):
    """ Check if a line collides with a list of rects """
    for rect in rects:
        if collide_line_to_rect(line, rect):
            yield rect

def collide_line_to_lines(line: "Tuple(Tuple(start), Tuple(end))", lines: "List[Tuple(Tuple(start), Tuple(end))]"):
    """ Check if a line collides with a list of lines """
    for _line in lines:
        if collide_line_to_line(line, _line):
            yield _line

def collide_line_to_lines_point(line: "Tuple(Tuple(start), Tuple(end))", lines: "List[Tuple(Tuple(start), Tuple(end))]"):
    """ Check if a line collides with a list of lines and return the point of collision """
    for _line in lines:
        _point = collide_line_to_line_point(line, _line)
        if _point:
            yield _point

def collide_point_to_rect(point: "Tuple(x, y)", rect: pygame.Rect):
    """ Check if a point collides with a rect """
    return rect.collidepoint(point)

