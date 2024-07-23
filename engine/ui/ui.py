import pygame

from engine import io
from engine import utils

# ---------------------------- #
# util objects

DEFAULT_BACKGROUND = 



# ---------------------------- #
# ui objects

class UIObject:
    def __init__(self, x: int, y: int, w: int, h: int, offset: list = [0, 0]):
        """ Create a new UI object """
        self.position = [x, y]
        self.area = [w, h]
        self.offset = offset.copy()

        # config
        self._config = {
            "background": utils.
        }
    
    def is_hovering(self):
        """ Check if the mouse is touching the object """
        mpos = pygame.mouse.get_pos()
        return pygame.Rect(self.position + self.area).collidepoint(mpos)
    
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
        return (click_pos[0] - self.position[0], click_pos[1] - self.position[1])
    
    def __setitem__(self, key, val):
        """ Set an item """
        self._config[key] = val
    
    def __getitem__(self, key):
        """ Get an item """
        return self._config[key]
    
    

# ---------------------------- #
# custom ui objects

class Frame(UIObject):
    def __init__(self, x: int, y: int, w: int, h: int, offset: list = [0, 0]):
        """ Create a new Frame Object """
        pass



