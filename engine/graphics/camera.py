import pygame


from engine import singleton


# ---------------------------- #
# constants



# ---------------------------- #
# pseudo camera

class PseudoCamera:
    """
    A pseudo camera class 

    - center: used to calcualte current chunk (everything is rendered AROUND this chunk)
    - position: the position of the camera

    Note: All addition/subtraction calculations for position are reversed
    - pygame is RIGHT, DOWN for positive axis
    - we want RIGHT, UP for positive axis

    """
    def __init__(self, position: tuple, area: tuple):
        """ Create a new pseudo camera """
        self.__position = pygame.math.Vector2(position)
        self._rect = pygame.Rect(position, area)

        # since we use center for rendering, set the topleft to be `-center`
        self.position = -1 * self.center

    # ---------------------------- #
    # core properties
    def __add__(self, other: tuple):
        """ Add to the camera """
        self.__position += (other[0], -other[1])
        self._rect.topleft = self.__position
        return self
    
    def __sub__(self, other: tuple):
        """ Subtract from the camera """
        self.__position -= (other[0], 0-other[1])
        self._rect.topleft = self.__position
        return self
    
    def __mul__(self, other: tuple):
        """ Multiply the camera """
        self.__position *= other
        self._rect.topleft = self.__position
        return self
    
    def __truediv__(self, other: tuple):
        """ Divide the camera """
        self.__position /= other
        self._rect.topleft = self.__position
        return self

    def __floordiv__(self, other: tuple):
        """ Floor divide the camera """
        self.__position //= other
        self._rect.topleft = self.__position
        return self

    @property
    def position(self):
        """ Get the position of the camera """
        return pygame.math.Vector2(self._rect.topleft)
    
    @position.setter
    def position(self, other: tuple):
        """ Set the position of the camera """
        self.__position = pygame.math.Vector2(other)
        self._rect.topleft = self.__position
    
    @property
    def area(self):
        """ Get the area of the camera """
        return pygame.math.Vector2(self._rect.size)
    
    @area.setter
    def area(self, other: tuple):
        """ Set the area of the camera """
        _center = self.center
        self._rect.size = other
        # recalculate center position
        self.position = _center - self.area // 2

    @property
    def rect(self):
        """ Get the rect of the camera """
        return self._rect

    # ---------------------------- #
    # properties

    @property
    def center(self):
        """ Get the center of the camera """
        return pygame.math.Vector2(self._rect.center)
    
    @property
    def topleft(self):
        """ Get the topleft of the camera """
        return pygame.math.Vector2(self._rect.topleft)
    
    @property
    def topright(self):
        """ Get the topright of the camera """
        return pygame.math.Vector2(self._rect.topright)
    
    @property
    def bottomleft(self):
        """ Get the bottomleft of the camera """
        return pygame.math.Vector2(self._rect.bottomleft)
    
    @property
    def bottomright(self):
        """ Get the bottomright of the camera """
        return pygame.math.Vector2(self._rect.bottomright)

    def __str__(self):
        """ String representation """
        return f"PseudoCamera || position: {str(self.__position):10}, area: {str(self.area):10}, center: {str(self.center):10}, chunk: {str(
            (int(self.center[0] // singleton.DEFAULT_CHUNK_PIXEL_WIDTH), int(self.center[1] // singleton.DEFAULT_CHUNK_PIXEL_HEIGHT))
        ):10}"

# ---------------------------- #
# gl camera
