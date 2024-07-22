import pygame

from engine import io

# ---------------------------- #
# ui objects

class UIObject:
    def __init__(self, x: int, y: int, w: int, h: int, offset: list = [0, 0]):
        """ Create a new UI object """
        self.position = [x, y]
        self.area = [w, h]
        self.offset = offset
    
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
    

# ---------------------------- #
# custom ui objects





