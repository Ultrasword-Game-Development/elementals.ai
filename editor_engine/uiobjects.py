import json
import pygame

from array import array

from engine import io
from engine import utils
from engine import singleton

from engine.ui import ui
from engine.ui import pixelfont

from engine.handler import world
from engine.handler import signal

from engine.graphics import gl
from engine.graphics import shader
from engine.graphics import camera
from engine.graphics import spritesheet

from editor_engine import editor_singleton

# ---------------------------- #
# constants



# ---------------------------- #
# editor window

class Editor(ui.Frame):
    
    def __post_init__(self):
        """ Post init function """
        # store world current data
        self._world_camera = editor_singleton.CURRENT_EDITING_WORLD.camera
        self._camera_scale = 1.0
        self._camera_scale_ratio = 0.25
        self._camera_scale_ratio_increment = 0.05
        self._camera = camera.PseudoCamera((0, 0), pygame.math.Vector2(self.area) * self._camera_scale * self._camera_scale_ratio)
        self._frame = pygame.Surface(self._camera.area, 0, 16).convert_alpha()
        self._frame.fill((0, 0, 0, 0))
        # set new value
        editor_singleton.CURRENT_EDITING_WORLD._camera = self._camera
        editor_singleton.CURRENT_EDITING_WORLD.camera = self._camera
        # selection stats
        self._selection_tile_coordinate = (0, 0)
        
        self._raw_buffer_pos = (0, 0)
        self._buffer_tile_pos = (0, 0)
        self._selected_tile_overlay_rect = pygame.Rect(0, 0, singleton.DEFAULT_TILE_WIDTH, singleton.DEFAULT_TILE_HEIGHT)
        self._selected_tile_overlay_surface = pygame.Surface((singleton.DEFAULT_TILE_WIDTH, singleton.DEFAULT_TILE_HEIGHT), 0, 16).convert_alpha()
        self._selected_tile_overlay_surface.fill((255, 0, 0, 100))
        self._move_vec = pygame.math.Vector2(0, 0)
        
        # camera move speed
        self._camera_move_speed = 50

        # signal
        signal.get_signal(singleton.GLOBAL_FILE_DROP_SIGNAL_KEY).add_emitter_handling_function("editor_file_drop", self.load_config_file)

        
    # ---------------------------- #
    # logic

    def update(self):
        """ Update the object """
        # zooming in + zooming out :)
        if io.get_key_pressed(singleton.CONTROL_KEY_EQUIV) and io.get_key_clicked(pygame.K_EQUALS):
            self._camera_scale_ratio = utils.clamp(self._camera_scale_ratio - self._camera_scale_ratio_increment, 0.1, self._camera_scale)
            self._camera.area = pygame.math.Vector2(self.area) * self._camera_scale * self._camera_scale_ratio
            self._frame = pygame.Surface(self._camera.area, 0, 16).convert_alpha()
            self._frame.fill((0, 0, 0, 0))
            print(__file__, 'Note: Zooming in', self._camera)
        elif io.get_key_pressed(singleton.CONTROL_KEY_EQUIV) and io.get_key_clicked(pygame.K_MINUS):
            self._camera_scale_ratio = utils.clamp(self._camera_scale_ratio + self._camera_scale_ratio_increment, 0.1, self._camera_scale)
            self._camera.area = pygame.math.Vector2(self.area) * self._camera_scale * self._camera_scale_ratio
            self._frame = pygame.Surface(self._camera.area, 0, 16).convert_alpha()
            self._frame.fill((0, 0, 0, 0))
            print(__file__, 'Note: Zooming out', self._camera)

        # convert screen mouse pos to world pos
        self._raw_buffer_pos = pygame.math.Vector2(utils.framebuffer_pos_to_screen_pos_int(self.get_relative_mouse_pos(), self._area, self._camera.area)) + self._camera.position
        # find selected tile coords
        x_coord = int(self._raw_buffer_pos.x // singleton.DEFAULT_TILE_WIDTH)
        y_coord = int(self._raw_buffer_pos.y // singleton.DEFAULT_TILE_HEIGHT)
        self._buffer_tile_pos = (x_coord, y_coord)
        self._buffer_chunk_pos = (x_coord // singleton.DEFAULT_CHUNK_WIDTH, y_coord // singleton.DEFAULT_CHUNK_HEIGHT)
        # calculate chunk tile position
        self._buffer_chunk_tile_pos = (
            (singleton.DEFAULT_CHUNK_WIDTH + x_coord % singleton.DEFAULT_CHUNK_WIDTH) % singleton.DEFAULT_CHUNK_WIDTH,
            (singleton.DEFAULT_CHUNK_HEIGHT + y_coord % singleton.DEFAULT_CHUNK_HEIGHT) % singleton.DEFAULT_CHUNK_HEIGHT)
        
        self._selected_tile_overlay_rect.topleft = (x_coord * singleton.DEFAULT_TILE_WIDTH, y_coord * singleton.DEFAULT_TILE_HEIGHT) - self._camera.position
        
        # camera movement
        self._move_vec *= 0.7
        if io.get_key_pressed(pygame.K_RIGHT):
            self._move_vec += (self._camera_move_speed * singleton.DELTA_TIME, 0)
        if io.get_key_pressed(pygame.K_LEFT):
            self._move_vec += (-self._camera_move_speed * singleton.DELTA_TIME, 0)
        if io.get_key_pressed(pygame.K_UP):
            self._move_vec += (0, self._camera_move_speed * singleton.DELTA_TIME)
        if io.get_key_pressed(pygame.K_DOWN):
            self._move_vec += (0, -self._camera_move_speed * singleton.DELTA_TIME)
        if io.get_key_pressed(pygame.K_LSHIFT):
            self._move_vec *= 1.4
        self._camera += self._move_vec

        if self.is_hovering():
            # use mouse right drag to move camera
            if io.is_right_pressed():
                self._camera -= pygame.math.Vector2(io.get_mouse_rel()) // 2
            # use scrolling to move
            self._move_vec += pygame.math.Vector2(io.get_scroll_rel()) * 50 * singleton.DELTA_TIME
            # check for left clicking
            if io.is_left_clicked() and self.is_hovering():
                print('Note: Left clicked at', self._buffer_tile_pos, " | and chunk pos: ", self._buffer_chunk_pos, " | and chunk tile pos: ", self._buffer_chunk_tile_pos)

    def render(self, surface: pygame.Surface):
        """ Render the object """
        # render the world into the frame
        editor_singleton.CURRENT_EDITING_WORLD.update_and_render(self._frame)

        # TODO - scaling the image???

        if singleton.EDITOR_DEBUG:
            # render all rects in chunks to the screen lol
            for active_chunk in editor_singleton.CURRENT_EDITING_WORLD.iterate_renderable_chunk_positions():
                for layer in editor_singleton.CURRENT_EDITING_WORLD._layers:
                    # render the chunk rect
                    pygame.draw.rect(self._frame, (255, 0, 0, 150), world.Chunk.generate_chunk_rect_given_chunk_position(active_chunk, self._camera), 1)

        # draw a circle
        pygame.draw.circle(self._frame, (255, 0, 0, 255), self._raw_buffer_pos - self._camera.position, 2)
        # draw an overlay rect
        self._frame.blit(self._selected_tile_overlay_surface, self._selected_tile_overlay_rect.topleft)

        surface.blit(pygame.transform.scale(self._frame, self._area), self.get_ui_rect())
        # print(self.get_ui_rect())
        # super().render(surface)
    
    def resize_screen(self, new_size: tuple):
        """ Resize the screen """
        self._camera.area = new_size
        # create new frame
        self._frame = pygame.Surface(self._camera.area, 0, 16).convert_alpha()
        self._frame.fill((0, 0, 0, 0))
    
    # ---------------------------- #
    # editor function

    def close(self):
        """ Close the editor window """
        # reset the world camera
        editor_singleton.CURRENT_EDITING_WORLD._camera = self._world_camera
        editor_singleton.CURRENT_EDITING_WORLD.camera = self._world_camera
        print('Note: Closing Editor')

    # ---------------------------- #
    # admin functions

    def load_config_file(self, path: str):
        """ Load a config file """
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            
            if "type" not in data:
                # could be a spritesheet file
                if "meta" not in data:
                    raise Exception("Invalid config file or spritesheet")
                # load the spritesheet
                editor_singleton.TABSMANAGER_ELEMENT.on_file_drop(path)
                return
            
            # check if necessary keys exist
            data['tabs']
            data['world']
        except Exception as e:
            print(e)
            return
        
        # load the data
        _tabdata = data['tabs']
        _worlddata = data['world']
        # TODO -- include other paramters

        # load the world
        editor_singleton.CURRENT_EDITING_WORLD = singleton.load_world(_worlddata)
        editor_singleton.WORLD_NAME_TITLE_ELEMENT.set_text(editor_singleton.CURRENT_EDITING_WORLD._world_storage_key)
        editor_singleton.CURRENT_EDITING_WORLD._camera = self._camera
        editor_singleton.CURRENT_EDITING_WORLD.camera = self._camera
        # load tabdata
        editor_singleton.TABSMANAGER_ELEMENT.load_config(_tabdata)
        
# ---------------------------- #
# sprite selection

class SpriteSelect(ui.Frame):
    
    def __post_init__(self):
        """ Post init function """
        super().__post_init__()
        # include tabs
        self._tabs = {}
        self._selected_tab = None

        self._font = pixelfont.load_pixelfont("assets/fonts/small_font.png")

        self._empty_text = self._font.render_to_surface("No Tab\nSelected", newline=True, options={
            'text_align': pixelfont.CENTER_ALIGN
        }, scale = 10)
        self._empty_text_rect = self._empty_text.get_rect()
        self._empty_text_rect.center = self.get_ui_rect().center
        
        editor_singleton.SPRITESELECT_ELEMENT = self
        
        # ui attributes
        self._zoom = 0
        self._grid_size = 3 # -1 for infinite  height
        self._grid_item_size = [self._area[0] // self._grid_size, 
                                self._area[0] // self._grid_size]
        
    # ---------------------------- #
    # logic

    def update(self):
        """ Update the object """
        if not self._selected_tab:
            # render empty page
            return
        # update all objects for mouse clicks
        # TODO - update for mouse clicking

    def render(self, surface: pygame.Surface):
        """ Render the object """
        super().render(surface)
        surface.blit(self._empty_text, self._empty_text_rect)
        # pygame.draw.rect(surface, (255, 255, 255), self._empty_text_rect, 1)
        if self._border_flag:
            pygame.draw.rect(surface, self._border_color, self.get_ui_rect(), self._border_width)
        # render selected tab
        if self._selected_tab == None:
            return
        self._frame.blit(pygame.transform.scale(io.load_image(self._selected_tab._tab_content[0]._sprite_path), self._grid_item_size), (0, 0))
    
    # ---------------------------- #
    # grid functions
    
    def set_grid_blocks(self, x: int, y: int):
        """ Set the grid blocks """
        self._grid_size = [x, y]
        self._grid_item_size = [self._area[0] // self._grid_size[0], self._area[1] // self._grid_size[1]]

    def set_selected_tab(self, new_tab):
        """ Set the new selected tab """
        if not self._selected_tab:
            self._selected_tab = new_tab
            return
        # check if same tab
        if new_tab._tab_name == self._selected_tab._tab_name:
            return
        # set new tab
        self._selected_tab = new_tab

# ---------------------------- #
# tab

class Tab(ui.Text):
    """ 
    Tab object 
    
    Is stored within a list in the TabsManager. Has attribute called: `_frame` (is a frame type object)
    
    SpriteSelect simply renders the contents of this frame into itself and 
    forwards events into the tab object.
    
    """
    
    def __init__(self, name: str = "Tab", tab_data: list = None, parent: ui.UIObject = None):
        """ Post init function """
        super().__init__(0, 0, w=None, h=1.0, padding=1, parent=parent)
        self._tab_name = name
        self._tab_content = []
        self._tab_data = tab_data
        if self._tab_data:
            self._load_tab_data()
        
        # render text
        self._frame = None
        self.set_font("assets/fonts/Roboto-Medium.ttf")
        self.set_text(self._tab_name)

        self._p_rect = self._rendered_text_rect.copy()
        self._p_rect.topleft = self._position.copy()

        self._signal_emitter = None

    # ---------------------------- #
    # logic
    
    def update(self):
        """ Update the object """
        if self.is_left_clicked() and self._signal_emitter:
            self._signal_emitter.emit({"tab": self})
    
    def is_hovering(self):
        """ Check if the tab is hovering """
        mpos = io.get_framebuffer_mouse_pos()
        return self._p_rect.collidepoint(mpos)

    def update_text(self):
        """ Update the text x position """
        super().update_text()
        # make sure to update the _frame object too
        if not self._rendered_text:
            return
        self._frame = pygame.Surface(self._rendered_text_rect.size, 0, 16).convert_alpha()
        self._frame.fill(self._main_color)
        # copy over
        self._frame.blit(self._rendered_text, (0, 0))
    
    def _load_tab_data(self):
        """ Load the tab data """
        for item in self._tab_data:
            _file = item["file"]
            _position = (item["x"], item["y"])
            # load the spritesheets
            _spritesheet = spritesheet.load_spritesheet(_file)
            _areas = (_spritesheet._config[spritesheet.WIDTH], _spritesheet._config[spritesheet.HEIGHT])
            _coords = (_position[0] // _areas[0], _position[1] // _areas[1])
            _sprite_str = _spritesheet.get_sprite_str_id(_coords[1] * _spritesheet._config[spritesheet.HORIZONTAL_TILES] + _coords[0])
            # create defaulttile
            _tile = world.DefaultTile(_position, _sprite_str)
            # save data
            self._tab_content.append(_tile)
            

class TabsManager(ui.Frame):

    def __post_init__(self):
        """ Post init function """
        super().__post_init__()
        self._tabs = []
        editor_singleton.TABSMANAGER_ELEMENT = self

        # is scrollable
        self._x_scroll = 0
        self._max_x_scroll = 0
        self._column_padding = 10
        
        # signals
        # tab manager
        self._signal = signal.Signal("_tabs_manager_signal")
        self._signal.add_emitter_handling_function("click", self._signal_click, parent=self)

    # ---------------------------- #
    # logic

    def update(self):
        """ Update the object """
        if self.is_hovering():
            # check for horizontal scroll
            self._x_scroll = utils.clamp(self._x_scroll + io.get_scroll_rel()[0] * 50 * singleton.DELTA_TIME, 0, self._max_x_scroll)
        # update tabs
        for tab in self._tabs:
            tab.update()

    def render(self, surface: pygame.Surface):
        """ Render the object """
        self._frame.fill(self._main_color)
        # render each tab
        left = -self._x_scroll
        y_level = self.get_ui_rect().h // 2
        for tab in self._tabs:
            tab._p_rect.left = tab.get_ui_rect().left + left
            # render the tab
            self._frame.blit(tab._frame, pygame.math.Vector2(tab._p_rect.topleft) - tab._position)
            left += tab._rendered_text_rect.w + self._column_padding
        # render the frame to the surface
        surface.blit(self._frame, self.get_ui_rect())

    # ---------------------------- #
    # tab management

    def add_tab(self, tab: Tab):
        """ Add a tab """
        self._max_x_scroll = max(0, len(self._tabs) * 100 - self._area[0])
        self._tabs.append(tab)
        tab._signal_emitter = self._signal.get_unique_emitter()
    
    def _signal_click(self, data: dict, parent: ui.UIObject):
        """ Handle the click signal from tab objects """
        editor_singleton.SPRITESELECT_ELEMENT.set_selected_tab(data["tab"])

    def load_config(self, _tab_data: list) -> None:
        """ Load a config file """
        # clear all tabs (don't save data)
        # TODO: create savedata prompt?
        self._tabs.clear()
        # create tabs
        for item in _tab_data:
            _tab = Tab(item["name"], item["items"], parent=self)
            self.add_tab(_tab)
        # set active tab to first tab
        editor_singleton.SPRITESELECT_ELEMENT.set_selected_tab(self._tabs[0])
        
    def export_tab_data(self) -> dict:
        """ Export the tab data """
        pass

    def on_file_drop(self, file_path: str):
        """ Handle a file drop """
        # TODO: later -- for loading indiviudal files
        """
        I need to implement:
        - check if spritesheet or image file
        - if spritesheet
            - load the spritesheet
            - extract all image data 
            - store dimensions + snippets from original image
        - if image file
            - load image
        - resize all images to fit inside of grid
        - store all images in a list + give ordering + id
        - add to current tab
        """
        
        if file_path.endswith('.json'):
            # is a spritesheet
            _spritesheet = spritesheet.load_spritesheet(file_path)
            
        else:
            # not a spritesheet
            pass


# ---------------------------- #
# save button

class SaveButton(ui.Button):
    
    def __post_init__(self):
        """ Post init function """
        super().__post_init__()
        
        # add the signal
        self._signal.add_emitter_handling_function("click", self.save_world)
        
    # ---------------------------- #
    # logic
    
    def save_world(self, data: dict):
        """ Save the world """
        print('Note: Saving the world (but not for real)')
        print(editor_singleton.CURRENT_EDITING_WORLD)

# ---------------------------- #
# new world button

class NewWorldButton(ui.Button):
    
    def __post_init__(self):
        """ Post init function """
        super().__post_init__()
        
        # add the signal
        self._signal.add_emitter_handling_function("click", self.new_world)
        
    # ---------------------------- #
    # logic
    
    def new_world(self, data: dict):
        """ Create a new world """
        print('Note: Creating a new world (but not for real)')

# -------------------------------------------------- #
# editor objects

# ---------------------------- #
# color picker / selector

class ColorPicker(ui.ExternalUIObject):
    DEFAULT_COLORPICKER_SHADER = "assets/shaders/color-picker.glsl"
    DEFAULT_COLORPICKER_VAO = "color_picker_quad"
    
    """
    the actual colorpicker object is a small 8x8 icon
    - drawn onto the framebuffer

    the actual picker window is a 256x256 window 
    - drawn onto the main surface
    - graphics used include: 
        - opengl to render colors
        - color gradient
        - mouse resizing capabilities

    """

    def __post_init__(self):
        """ Post init function """
        super().__post_init__()
        self._color = (0, 0, 0)
        self._padding = 1

        self._color_picker = pygame.Surface((self._screen_area[0] - self._padding, self._screen_area[1] - self._padding), 0, 16).convert_alpha()
        self._color_picker.fill(self._color)
        
        # create an opengl framebuffer
        self._rgb_surface = pygame.Surface((256, 256), 0, 16).convert_alpha()
        self._rgb_texture = singleton.CONTEXT.texture(self._rgb_surface.get_size(), 4)
        self._rgb_texture.filter = (gl.moderngl.LINEAR, gl.moderngl.LINEAR)

        self._framebuffer = singleton.CONTEXT.framebuffer(color_attachments=[self._rgb_texture])

        # load up shader + quad
        self._color_shader = shader.load_shader(self.DEFAULT_COLORPICKER_SHADER)
        self._color_render_quad = self._color_shader.load_quad_vertexarray(self.DEFAULT_COLORPICKER_VAO, [
            (singleton.CONTEXT.buffer(
                data=array('f', [
                    # position (x, y), uv coords (x, y)
                    1.0, -1.0, 1.0, 1.0,  # bottomright
                    -1.0, -1.0, 0.0, 1.0, # bottomleft (but not rly)
                    1.0, 1.0, 1.0, 0.0,   # topright (but not rly)
                    -1.0, 1.0, 0.0, 0.0,  # topleft
                ])
            ), '2f 2f', 'vert', 'texcoord')
        ])
    
    def render(self, surface: pygame.Surface):
        """ Render the object """
        # pygame.draw.rect(surface, (255, 255, 255), self.get_screen_ui_rect())
        surface.blit(self._rgb_surface, self.get_screen_ui_rect())

    def update(self):
        """ Update the object """
        # handle stuff if mouse clicked

        # have to use self.color_selector = (r, g, b, a) to update the color        
        pass
    
    @property
    def color_selection(self):
        """ Get the color selection """
        return self._color

    @color_selection.setter
    def color_selection(self, new: tuple):
        """ Set the new color sleection """
        if len(new) != 4: raise ValueError("Color must be a 4-tuple (255, 255, 255, 255)")
        self._color = new
        
        # render new color selector
        self._framebuffer.use()
        self._framebuffer.clear()
        self._rgb_texture.use(0)

        self._color_shader["color"] = self.color_selection
        self._color_shader["time"] = singleton.ACTIVE_TIME
        self._color_render_quad.render(mode=gl.moderngl.TRIANGLE_STRIP)

        # ´extract framebuffer data to surface
        data = self._framebuffer.read(viewport=self._rgb_surface.get_size(), components=4)
        
        # create pygame surface
        self._rgb_surface = pygame.image.fromstring(data, self._rgb_surface.get_size(), 'RGBA')

        
        
        



