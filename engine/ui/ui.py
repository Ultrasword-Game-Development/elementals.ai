import pygame

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


def start_ui():
    """ Start the UI """
    global GLOBAL_FONT
    GLOBAL_FONT = pixelfont.PixelFont("assets/fonts/small_font.png")

def add_ui_object(*args):
    """ Add a UI object to the cache """
    for item in args:
        GLOBAL_UI_CHACHE.append(item)
    GLOBAL_UI_CHACHE.sort(key=lambda x: x.get_layer())

def update_ui_items():
    """ Update all UI items """
    for item in GLOBAL_UI_CHACHE:
        item.update()
    
def render_ui_items(surface: pygame.Surface):
    """ Render all UI items """
    for item in GLOBAL_UI_CHACHE:
        item.render(surface)


# ---------------------------- #
# ui objects

class UIObject(entity.Entity):
    def __init__(self, relx: int, rely: int, w = None, h = None , offset: list = [0, 0], parent = None, margin: int = 0, padding: int = 0):
        """ Create a new UI object """
        super().__init__()
        self.abs_area = [0, 0]
        self.abs_position = [0, 0]
        self._position = [relx, rely]
        self._area = [0, 0]
        self.abs_offset = offset.copy()
        self._layer = 0
        
        # no parent
        if parent == None:
            if not w:
                w = singleton.FB_SIZE[0]
            elif type(w) == float:
                w = int(w * singleton.FB_SIZE[0])
            if not h:
                h = singleton.FB_SIZE[1]
            elif type(h) == float:
                h = int(h * singleton.FB_SIZE[1])
            
            self.abs_area = [w, h]
            self.abs_position = (relx, rely)
        # yes parent
        else:
            if not w:
                w = parent.abs_area[0]
            elif type(w) == float:
                w = int(w * parent.abs_area[0])
            if not h:
                h = parent.abs_area
            elif type(h) == float:
                h = int(h * parent.abs_area[1])
            
            self._layer = parent._layer + 1
            self.abs_area = [w, h]
            self.abs_position = (parent.get_abs_position()[0] + relx, parent.get_abs_position()[1] + rely)  
        
        self._position = [self.abs_position[0] + relx + padding, self.abs_position[1] + rely + padding]
        self._area = [self.abs_area[0] - padding * 2, self.abs_area[1] - padding * 2]
        
        self._padding = padding
        self._text = None
        self._id = str(hash(self))
        
        self._children = []
        self._background_color = COLOR_THEME[DEFAULT]
    
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
        mpos = pygame.mouse.get_pos()
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

    # ---------------------------- #
    # misc
    
    def set_background_color(self, color: tuple):
        """ Set the background color of the object """
        self._background_color = color
    
    
# ---------------------------- #
# custom ui objects

class Frame(UIObject):
    def __init__(self, x: int, y: int, w: int = -1, h: int = -1, offset: list = [0, 0], parent=None):
        """ Create a new Frame Object """
        super().__init__(x, y, w=w, h=h, offset=offset, parent=parent)
        self._surface = pygame.Surface((w, h), 0, 16).convert_alpha()

    def render(self, surface: pygame.Surface):
        """ Render the object """
        surface.blit(self._surface, self.abs_position)
    
    def update(self):
        """ Update the object """
        pass


