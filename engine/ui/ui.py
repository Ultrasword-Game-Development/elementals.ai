import pygame

import dataclasses

from engine import io
from engine import utils
from engine import singleton

from engine.ui import pixelfont

from engine.physics import entity

# ---------------------------- #
# util objects

DEFAULT = "DEFAULT"
HOVER = "HOVER"
ACTIVE = "ACTIVE"
TEXT = "TEXT"
TEXT_HOVER = "TEXT_HOVER"

COLOR_THEME = {
    DEFAULT: (0, 30, 61),
    HOVER: (0, 50, 81),
    ACTIVE: (0, 70, 101),
    TEXT: (255, 255, 255),
    TEXT_HOVER: (200, 200, 200),
}

GLOBAL_FONT = None

GLOBAL_UI_CHACHE = []
GLOBAL_UI_SCREEN_CACHE = []

# ---------------------------- #
# ui objects

PADDING_LEFT = 0
PADDING_TOP = 1
PADDING_RIGHT = 2
PADDING_BOTTOM = 3

class UIObject(entity.Entity):
    def __init__(self, relx = 0, rely = 0, w = None, h = None , offset: list = [0, 0], parent = None, padding = 0, horizontal_align: bool = False):
        """ Create a new UI object """
        super().__init__()
        self.abs_area = [0, 0]
        self.abs_position = [0, 0]
        self.abs_offset = offset.copy()
        self._position = [0, 0]
        self._area = [0, 0]
        self._layer = 0
        self._horizontal_align = horizontal_align
        self._child_number = 0

        # add a child to the parent if there is a parent
        if parent:
            parent.add_child(self)

        max_size = singleton.FB_SIZE
        # no parent
        if parent == None:
            if not w:
                ww = singleton.FB_SIZE[0]
            elif type(w) == float:
                ww = int(w * singleton.FB_SIZE[0])
            if not h:
                hh = singleton.FB_SIZE[1]
            elif type(h) == float:
                hh = int(h * singleton.FB_SIZE[1])
            
            self.abs_area = [ww, hh]
            self.abs_position = (relx, rely)
        # yes parent
        else:
            max_size = parent.abs_area
            if not w:
                ww = parent.abs_area[0]
            elif type(w) == float:
                ww = int(w * parent.abs_area[0])
            if not h:
                hh = parent.abs_area
            elif type(h) == float:
                hh = int(h * parent.abs_area[1])
            
            self._layer = parent._layer + 1
            self.abs_area = [ww, hh]
            self.abs_position = (parent.get_abs_position()[0] + relx, 
                            parent.get_abs_position()[1] + rely)  
        
        # calculating relative position
        if not relx:
            relx = 0
        elif type(relx) == float:
            relx = int(relx * max_size[0])
        if not rely:
            rely = 0
        elif type(rely) == float:
            rely = int(rely * max_size[1])
        
        # check for padding
        if type(padding) == list:
            if len(padding) < 4:
                for i in range(4 - len(padding)):
                    padding.append(0)
        elif type(padding) == int:
            padding = [padding, padding, padding, padding]
        
        # set variables
        self._position = [self.abs_position[0] + relx + padding[PADDING_LEFT], 
                self.abs_position[1] + rely + padding[PADDING_TOP]]
        self._area = [self.abs_area[0] - padding[PADDING_LEFT] - padding[PADDING_RIGHT], 
                        self.abs_area[1] - padding[PADDING_BOTTOM] - padding[PADDING_TOP]]
        self._text = None
        self._padding = padding
        self._id = str(hash(self))
        
        self._children = []
        self._background_color = COLOR_THEME[DEFAULT]

        # post init
        self.__post_init__()
    
    def __post_init__(self):
        """ Post init function """
        pass

    # ---------------------------- #
    # base functions
    
    def render(self, surface: pygame.Surface):
        """ Render the object """
        pygame.draw.rect(surface, self._background_color, self.get_ui_rect())    
    
    def update(self):
        """ Update the object """
        pass
    
    @property
    def area(self):
        """ Get the area of the object """
        return self.abs_area
    
    @area.setter
    def area(self, value):
        """ Set the area of the object """
        self.abs_area[0] = value[0]
        self.abs_area[1] = value[1]
        
        self._area[0] = self.abs_area[0] - self._padding * 2
        self._area[1] = self.abs_area[1] - self._padding * 2
        
    # ---------------------------- #
    # mouse functions
    
    def is_hovering(self):
        """ Check if the mouse is touching the object """
        mpos = io.get_mouse_pos()
        return self.get_ui_rect().collidepoint(mpos)
    
    def is_left_clicked(self):
        """ Check if the left mouse button is clicked """
        return self.is_hovering and io.is_left_clicked()
    
    def is_right_clicked(self):
        """ Check if the right mouse button is clicked """
        return self.is_hovering and io.is_right_clicked()
    
    def is_dragged(self):
        """ Check if the object is being dragged """
        return self.is_hovering and tuple(io.get_mouse_rel()) != (0, 0)
    
    def get_clicked_relative_pos(self, click_pos: tuple):
        """ Get relative position of a mouse click """
        return (click_pos[0] - self.abs_position[0], click_pos[1] - self.abs_position[1])

    # ---------------------------- #
    # ui functions
    
    def get_ui_rect(self):
        """ Get the pygame rect of the object """
        return pygame.Rect(self._position + self._area)    
    
    def find_child(self, _id: str):
        """ Find a child by id """
        for c in self._children:
            if c._id == _id:
                return c
        return None
    
    def add_child(self, child):
        """ Add a child to the object """
        self._children.append(child)
        self._child_number = len(self._children)
    
    def remove_child(self, child):
        """ Remove a child from the object """
        self._children.remove(child)
        
    def get_abs_position(self):
        """ Get the absolute position of the object """
        return self.abs_position

    def get_rel_position(self):
        """ Get the relative position of the object """
        return self._position
    
    def get_layer(self):
        """ Get the layer of the object """
        return self._layer
    
    def set_layer(self, layer: int):
        """ Set the layer of the object """
        self._layer = layer
    
    def conform_child_rect(self, child_rect: pygame.Rect):
        """ Conform the child rect to the parent rect """
        if not self._horizontal_align:
            return pygame.Rect(self.abs_position[0] + child_rect.x, self.abs_position[1] + child_rect.y, child_rect.width, child_rect.height)
        # return with horizontal conformation
        return pygame.Rect(
            
        )


    # ---------------------------- #
    # misc

    def __len__(self):
        """ Get the number of children """
        return len(self._children)
    
    def set_background_color(self, color: tuple):
        """ Set the background color of the object """
        self._background_color = color
    

class ExternalUIObject(UIObject):
    """ 
    The only functions contained in this class are:

    - mouse collision
    - mouse click detection
    - mouse resizing
    """

    def __post_init__(self):
        """ Post init function """
        self._screen_pos = utils.framebuffer_pos_to_screen_pos(self.abs_position, singleton.FB_SIZE, singleton.WIN_SIZE)
        self._screen_area = utils.framebuffer_pos_to_screen_pos(self.abs_area, singleton.FB_SIZE, singleton.WIN_SIZE)

    # ---------------------------- #
    # mouse

    def is_hovering_screen(self):
        """ Check if the mouse is touching the object """
        mpos = io.get_abs_mouse_pos()
        return self.get_screen_ui_rect().collidepoint(mpos)
    
    def is_left_clicked_screen(self):
        """ Check if the left mouse button is clicked """
        return self.is_hovering_screen() and io.is_left_clicked()
    
    def is_right_clicked_screen(self):
        """ Check if the right mouse button is clicked """
        return self.is_hovering_screen() and io.is_right_clicked()
    
    def is_dragged_screen(self):
        """ Check if the object is being dragged """
        return self.is_hovering_screen() and tuple(io.get_mouse_rel()) != (0, 0)
    
    def get_clicked_relative_pos_screen(self, click_pos: tuple):
        """ Get relative position of a mouse click """
        return (click_pos[0] - self._screen_pos[0], click_pos[1] - self._screen_pos[1])

    # ---------------------------- #
    # utils

    def get_screen_ui_rect(self):
        """ Get the pygame rect of the object """
        return pygame.Rect(self._screen_pos + self._screen_area)


# ---------------------------- #
# custom ui objects

class Frame(UIObject):
    
    def __post_init__(self):
        """ Post init function """
        self._frame = pygame.Surface(self._area, 0, 16).convert_alpha()
        self._frame.fill((0, 0, 0, 0))
    
    def render(self, surface: pygame.Surface):
        """ Render the object """
        super().render(surface)
        surface.blit(self._frame, self.get_ui_rect().topleft)



# ---------------------------- #
# ui functions


def start_ui():
    """ Start the UI """
    global GLOBAL_FONT
    GLOBAL_FONT = pixelfont.PixelFont("assets/fonts/small_font.png")

def add_ui_object(*args):
    """ Add a UI object to the cache """
    for item in args:
        if ExternalUIObject in item.__class__.__mro__:
            GLOBAL_UI_SCREEN_CACHE.append(item)
        else:
            GLOBAL_UI_CHACHE.append(item)
    GLOBAL_UI_CHACHE.sort(key=lambda x: x.get_layer())
    GLOBAL_UI_SCREEN_CACHE.sort(key=lambda x: x.get_layer())

def update_ui_items():
    """ Update all UI items """
    for item in GLOBAL_UI_CHACHE:
        item.update()
    for item in GLOBAL_UI_SCREEN_CACHE:
        item.update()
    
def render_ui_items(surface: pygame.Surface):
    """ Render all UI items """
    for item in GLOBAL_UI_CHACHE:
        item.render(surface)

def render_screen_ui_items(surface: pygame.Surface):
    """ Render all screen UI items """
    for item in GLOBAL_UI_SCREEN_CACHE:
        item.render(surface)


