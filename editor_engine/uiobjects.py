
import pygame

from array import array

from engine import io
from engine import utils
from engine import singleton

from engine.ui import ui

from engine.handler import world

from engine.graphics import gl
from engine.graphics import shader
from engine.graphics import camera

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
        self._camera_scale = 2.0
        self._camera_scale_ratio = 0.5
        self._camera_scale_ratio_increment = 0.1
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
        
        self._selected_tile_overlay_rect.topleft = (x_coord * singleton.DEFAULT_TILE_WIDTH, y_coord * singleton.DEFAULT_TILE_HEIGHT) - self._camera.position
        
        # camera movement
        self._move_vec *= 0.1
        if io.get_key_pressed(pygame.K_d):
            self._move_vec += (self._camera_move_speed * singleton.DELTA_TIME, 0)
        if io.get_key_pressed(pygame.K_a):
            self._move_vec += (-self._camera_move_speed * singleton.DELTA_TIME, 0)
        if io.get_key_pressed(pygame.K_w):
            self._move_vec += (0, self._camera_move_speed * singleton.DELTA_TIME)
        if io.get_key_pressed(pygame.K_s):
            self._move_vec += (0, -self._camera_move_speed * singleton.DELTA_TIME)
        if io.get_key_pressed(pygame.K_LSHIFT):
            self._move_vec *= 1.4
        self._camera += self._move_vec

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
        # super().render(surface)
    
    def resize_screen(self, new_size: tuple):
        """ Resize the screen """
        self._camera.area = new_size
        # create new frame
        self._frame = pygame.Surface(self._camera.area, 0, 16).convert_alpha()
        self._frame.fill((0, 0, 0, 0))
    
    def close(self):
        """ Close the editor window """
        # reset the world camera
        editor_singleton.CURRENT_EDITING_WORLD._camera = self._world_camera
        editor_singleton.CURRENT_EDITING_WORLD.camera = self._world_camera

        print('Note: Closing Editor')

# ---------------------------- #
# sprite selection window

class SpriteSelect(ui.UIObject):
    pass


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

        
        
        



