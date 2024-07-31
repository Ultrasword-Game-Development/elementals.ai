import pygame

from engine import io
from engine import utils


# ---------------------------- #
# constants

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

PIXELFONT_CACHE = {}



LEFT_ALIGN = 0
CENTER_ALIGN = 1
RIGHT_ALIGN = 2


DEFAULT_TEXT_RENDER_OPTIONS = {
    'lines_align': [],
    'text_align': LEFT_ALIGN,
    'line_spacing': 1,
    'char_spacing': 0,
}

# ---------------------------- #
# pixelfont

class PixelFont:

    def __init__(self, path: str):
        """Initialize the PixelFont object"""
        self.path = path
        self.surface = io.load_image(self.path)
        self.surface.set_colorkey((0, 0, 0))
        self._chars = {}
        self._color = (255, 0, 0)
        
        # update color
        self.color = (255, 255, 255)

        # -------------------------------- #
        # load the chars + store them
        self.load_sprites()
    
    # ---------------------------- #
    # logic

    def load_sprites(self):
        """Load the sprites"""
        c_count = 0
        c_width = 0
        for x in range(self.surface.get_width()):
            if self.surface.get_at((x, 0))[0] == 127:
                # cut out / is end of previous character
                self._chars[CHAR_ORDER[c_count]] = utils.clip(
                    self.surface, x - c_width, 0, c_width, self.surface.get_height()
                )
                c_width = 0
                c_count += 1
            else:
                c_width += 1

    def render(self, surface: "Surface", text: str, loc: tuple, char_spacing: int = 0):
        """Render input text to a surface"""
        c_width = 0
        for c in text:
            # render the character
            if c in self._chars:
                surface.blit(self[c], (loc[0] + c_width, loc[1]))
                c_width += self[c].get_width()
            else:
                c_width += 4
            c_width += char_spacing
    
    def render_to_surface(self, text: str, newline: bool = False, options: dict = DEFAULT_TEXT_RENDER_OPTIONS, scale: int = 1):
        """ Render the text to a surface """
        # check if keys are included in options
        if 'lines_align' not in options:
            options['lines_align'] = []
        if 'text_align' not in options:
            options['text_align'] = LEFT_ALIGN
        if 'line_spacing' not in options:
            options['line_spacing'] = 1
        if 'char_spacing' not in options:
            options['char_spacing'] = 0


        _lines = text.split("\n")
        _total_lines = len(_lines)
        _widths = [0 for i in range(_total_lines)]
        _height = self.surface.get_height() * _total_lines + options['line_spacing'] * (_total_lines - 1)
        _line_rects = [None for i in range(_total_lines)]

        # calculate rects
        for i, line in enumerate(_lines):
            for j, c in enumerate(line):
                # add the width of the character
                if c in self._chars:
                    _widths[i] += self[c].get_width()
                else:
                    _widths[i] += 4
                
                # add spacing between characters
                if j < len(line) - 1: _widths[i] += options['char_spacing']

            # create line rect
            _line_rects[i] = pygame.Rect(0, i * self.surface.get_height() + options['line_spacing'] * (i - 1 if i > 0 else 0), _widths[i], self.surface.get_height())
        
        # create the surface
        result = pygame.Surface((max(_widths), _height), pygame.SRCALPHA, 16).convert_alpha()

        # align text
        if options['lines_align']:
            if len(options['lines_align']) == _total_lines:
                for i, align in enumerate(options['lines_align']):
                    if align == CENTER_ALIGN:
                        _line_rects[i].centerx = result.get_width() // 2
                    elif align == RIGHT_ALIGN:
                        _line_rects[i].right = result.get_width()
                    elif align == LEFT_ALIGN:
                        _line_rects[i].left = 0
        else:
            for _rect in _line_rects:
                if options['text_align'] == CENTER_ALIGN:
                    _rect.centerx = result.get_width() // 2
                elif options['text_align'] == RIGHT_ALIGN:
                    _rect.right = result.get_width()
                elif options['text_align'] == LEFT_ALIGN:
                    _rect.left = 0

        # render the text
        for i, line in enumerate(_lines):
            self.render(result, line, (_line_rects[i].left, _line_rects[i].top), options['char_spacing'])
            if i < len(_lines) - 1:
                _line_rects[i + 1].top = _line_rects[i].bottom + options['line_spacing']

        return pygame.transform.scale(result, (int(result.get_width() * scale), int(result.get_height() * scale)))

    # ---------------------------- #
    # properties

    @property
    def color(self):
        """Get the color of the font"""
        return self._color
    
    @color.setter
    def color(self, value):
        """Set the color of the font"""
        self.palette_swap(self._color, value)
        # self.surface.set_colorkey(self._color)
        self._color = value

    # ---------------------------- #
    # utils

    def palette_swap(self, old_c, new_c):
        """Palette swap function"""
        self.surface = utils.palette_swap(self.surface, old_c, new_c)
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

# ---------------------------- #
# utils

def load_pixelfont(path: str):
    """Load a pixelfont"""
    if path in PIXELFONT_CACHE:
        return PIXELFONT_CACHE[path]
    PIXELFONT_CACHE[path] = PixelFont(path)
    return PIXELFONT_CACHE[path]
