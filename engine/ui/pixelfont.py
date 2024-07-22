""" 
pixelfont.py

Contains the PixelFont class that takes in user defined .png font files and generates 
    a usable font object for text rendering.

"""

import pygame as pg

from . import asset
from ..utils import *

class PixelFont:
    CHAR_ORDER = [
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
        "G",
        "H",
        "I",
        "J",
        "K",
        "L",
        "M",
        "N",
        "O",
        "P",
        "Q",
        "R",
        "S",
        "T",
        "U",
        "V",
        "W",
        "X",
        "Y",
        "Z",
        "a",
        "b",
        "c",
        "d",
        "e",
        "f",
        "g",
        "h",
        "i",
        "j",
        "k",
        "l",
        "m",
        "n",
        "o",
        "p",
        "q",
        "r",
        "s",
        "t",
        "u",
        "v",
        "w",
        "x",
        "y",
        "z",
        ".",
        "-",
        ",",
        ":",
        "+",
        "'",
        "!",
        "?",
        "0",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "(",
        ")",
        "/",
        "_",
        "=",
        "\\",
        "[",
        "]",
        "*",
        '"',
        "<",
        ">",
        ";",
    ]

    def __init__(self, file: str):
        """Initialize the PixelFont object"""
        self.file = file
        self.surface = asset.ImageHandler[file]
        self.surface.set_colorkey((0, 0, 0))
        self._chars = {}

        # -------------------------------- #
        # load the chars + store them
        self.load_sprites()

    def load_sprites(self):
        """Load the sprites"""
        c_count = 0
        c_width = 0
        for x in range(self.surface.get_width()):
            if self.surface.get_at((x, 0))[0] == 127:
                # cut out / is end of previous character
                self._chars[self.CHAR_ORDER[c_count]] = clip(
                    self.surface, x - c_width, 0, c_width, self.surface.get_height()
                )
                c_width = 0
                c_count += 1
            else:
                c_width += 1

    def render(self, surface, text: str, loc: tuple):
        """Render input text to a surface"""
        c_width = 0
        for c in text:
            # render the character
            if c in self._chars:
                surface.blit(self[c], (loc[0] + c_width, loc[1]))
                c_width += self[c].get_width()
            else:
                c_width += 4

    def palette_swap(self, old_c, new_c):
        """Palette swap function"""
        self.surface = palette_swap(self.surface, old_c, new_c)
        self.load_sprites()

    def alter_palette(self, function):
        """Alter the palette with a custom function"""
        for x in range(self.surface.get_width()):
            for y in range(self.surface.get_height()):
                self.surface.set_at((x, y), function(self.surface.get_at((x, y))))
        # update the sprites
        self.load_sprites()

    def __getitem__(self, key):
        """GetItem overload function"""
        return self._chars.get(key)
