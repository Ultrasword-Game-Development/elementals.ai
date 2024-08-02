import pygame

import dataclasses

from engine import io
from engine import utils
from engine import singleton

from engine.ui import pixelfont

from engine.handler import signal

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

        max_size = singleton.FB_SIZE if parent == None else parent.abs_area
        
        # calculating relative position
        if not relx:
            relx = 0
        elif type(relx) == float:
            relx = int(relx * max_size[0])
        if not rely:
            rely = 0
        elif type(rely) == float:
            rely = int(rely * max_size[1])
        self._rel_position = (relx, rely)
        
        # check for padding
        if type(padding) == list:
            if len(padding) < 4:
                for i in range(4 - len(padding)):
                    padding.append(0)
        elif type(padding) == int:
            padding = [padding, padding, padding, padding]
        
        # no parent
        if parent == None:
            if not w:
                ww = singleton.FB_SIZE[0] - relx
            elif type(w) == float:
                ww = int(w * singleton.FB_SIZE[0])
            if not h:
                hh = singleton.FB_SIZE[1] - rely
            elif type(h) == float:
                hh = int(h * singleton.FB_SIZE[1])
            
            self.abs_area = [ww, hh]
            self.abs_position = (relx, rely)
        # yes parent
        else:
            self._layer = parent._layer + 1
            result = parent.conform_child_abs_rect(relx, rely, w, h)
            self.abs_area = result[2:]
            self.abs_position = result[:2]
        
        # set variables
        self._position = [self.abs_position[0] + padding[PADDING_LEFT], 
                        self.abs_position[1] + padding[PADDING_TOP]]
        self._area = [self.abs_area[0] - padding[PADDING_LEFT] - padding[PADDING_RIGHT], 
                        self.abs_area[1] - padding[PADDING_BOTTOM] - padding[PADDING_TOP]]
        self._padding = padding
                
        # graphics settings
        self._text = None
        self._id = str(hash(self))
                
        self._children = []
        self._background_color = COLOR_THEME[DEFAULT]
        
        # graphics
        self._border_flag = False
        self._border_color = (0, 0, 0)
        self._border_width = 1
        
        self._main_color = COLOR_THEME[DEFAULT]
        self._secondary_color = COLOR_THEME[HOVER]

        # post init
        self.__post_init__()
    
    def __post_init__(self):
        """ Post init function """
        pass

    # ---------------------------- #
    # base functions
    
    def update(self):
        """ Update the object """
        pass

    def render(self, surface: pygame.Surface):
        """ Render the object """
        pygame.draw.rect(surface, self._background_color, self.get_ui_rect())  
        # draw rect
        if self._border_flag:
            pygame.draw.rect(surface, self._border_color, self.get_ui_rect(), self._border_width)
    
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
        mpos = io.get_framebuffer_mouse_pos()
        return self.get_ui_rect().collidepoint(mpos)
    
    def is_left_clicked(self):
        """ Check if the left mouse button is clicked """
        return self.is_hovering() and io.is_left_clicked()
    
    def is_right_clicked(self):
        """ Check if the right mouse button is clicked """
        return self.is_hovering and io.is_right_clicked()
    
    def is_dragged(self):
        """ Check if the object is being dragged """
        return self.is_hovering and tuple(io.get_mouse_rel()) != (0, 0)
    
    def get_relative_mouse_pos(self):
        """ Get the relative mouse position """
        mouse_pos = io.get_framebuffer_mouse_pos()
        return (mouse_pos[0] - self.abs_position[0], mouse_pos[1] - self.abs_position[1])
    
    def get_clicked_relative_pos_from(self, click_pos: tuple):
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
        self.conform_child_area(child)
    
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
    
    def conform_child_abs_rect(self, relx, rely, w = None, h = None):
        """ Conform the child rect """
        max_size = self.abs_area
        if not w:
            ww = max_size[0] - relx
        elif type(w) == float:
            ww = int(w * max_size[0])
        if not h:
            hh = max_size[1] - rely
        elif type(h) == float:
            hh = int(h * max_size[1])
        
        return [self.abs_position[0] + relx, self.abs_position[1] + rely, ww, hh]
    
    def set_background_color(self, color: tuple):
        self._main_color = color
        self._background_color = color    
    
    def set_secondary_color(self, color: tuple):
        self._secondary_color = color
    
    # ---------------------------- #
    # graphics functions
    
    def set_border(self, color: tuple, width: int):
        """ Set the border of the object """
        # update the border
        self._border_flag = True
        self._border_color = color
        self._border_width = width
    
    def toggle_border(self):
        """ Enable the border of the object """
        self._border_flag = True
        return self._border_flag
    
    # ---------------------------- #
    # misc

    def __len__(self):
        """ Get the number of children """
        return len(self._children)
    
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
        self._frame.fill(self._background_color)
    
    def render(self, surface: pygame.Surface):
        """ Render the object """
        super().render(surface)
        surface.blit(self._frame, self.get_ui_rect().topleft)
    
    # ---------------------------- #
    # misc
    
    def set_background_color(self, color: tuple):
        self._frame.fill(color)
        return super().set_background_color(color)


# ---------------------------- #
# text 

class Text(UIObject):
    def __post_init__(self):
        """ Post init function """
        super().__post_init__()
        self._font_path = None
        self._font = None
        self._text = None
        self._rendered_text = None
        self._rendered_text_rect = None
        self._center_rect = False
        
    # ---------------------------- #
    # logic
    
    def render(self, surface: pygame.Surface):
        """ Render the object """
        super().render(surface)
        if self._text:
            surface.blit(self._rendered_text, self._rendered_text_rect)
    
    # ---------------------------- #
    # text
    
    def update_text(self):
        """ Update the text and rendered text """
        if self._text and self._font:
            # render the text
            self._rendered_text = self._font.render(self._text, True, COLOR_THEME[TEXT])
            self._rendered_text_rect = self._rendered_text.get_rect()
            # clip out of bounds text
            if self._rendered_text_rect.width > self._area[0]:
                result = pygame.Surface(self._area, 0, 16).convert_alpha()
                result.fill((0, 0, 0, 0))
                result.blit(self._rendered_text, (0, 0))
                self._rendered_text = result
            # center the text
            if self._center_rect:
                self._rendered_text_rect.center = self.get_ui_rect().center
            else:
                self._rendered_text_rect.left = self.get_ui_rect().left
                self._rendered_text_rect.centery = self.get_ui_rect().centery
    
    def set_text(self, text: str, center: bool = False):
        """ Set the text of the object """
        self._text = text
        self._center_rect = center
        self.update_text()
        
    def set_font(self, font_path: str, pixelfont: bool = False):
        """ Set the font of the object """
        self._font_path = font_path
        if pixelfont:
            self._font = pixelfont.PixelFont(font_path)
        else:
            self._font = io.load_font(font_path, 22)
        self.update_text()


# ---------------------------- #
# button

class Button(Text):
    
    MFBPOS = "mouse_fb_pos"
    
    def __post_init__(self):
        super().__post_init__()
        # create a signal
        self._signal = signal.Signal(self._id + "_clicked")
        self._signal_emitter = self._signal.get_unique_emitter()
    
    # ---------------------------- #
    # events
    
    def update(self):
        """ Update the object """
        if self.is_hovering():
            self._background_color = self._secondary_color
        else:
            self._background_color = self._main_color
    
        # check if clicked
        if self.is_left_clicked():
            self._signal_emitter.emit(data = {Button.MFBPOS: io.get_framebuffer_mouse_pos()})
        

    

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


