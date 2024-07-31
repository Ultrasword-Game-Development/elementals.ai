import pygame
import hashlib


# ---------------------------- #
# misc

def hex_to_rgb(_hex: str):
    return tuple(int(_hex.strip('#')[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb: tuple):
    return '#%02x%02x%02x' % rgb

def hash_sha256(item):
    return hashlib.sha256(item)

def normalize_rgb(color: tuple):
    return tuple([c / 255 for c in color])

def clamp(val, min_val, max_val):
    return max(min(val, max_val), min_val)


# ---------------------------- #
# surface

def palette_swap(surf, old_c, new_c):
    """Palette swap function"""
    _storage = surf.get_colorkey()
    surf.set_colorkey(None)

    # background surface
    c_copy = surf.copy()
    c_copy.set_colorkey(None)
    c_copy.fill(new_c)

    # colorkey surface
    c_surf = surf.copy()
    c_surf.set_colorkey(old_c)
    c_copy.blit(c_surf, (0, 0))

    surf.set_colorkey(_storage)
    c_copy.set_colorkey(_storage)
    return c_copy

def clip(image, x, y, w, h):
    """Clip a rect from a surface"""
    return image.subsurface(pygame.Rect(x, y, w, h)).convert_alpha().copy()

def framebuffer_pos_to_screen_pos(pos, framebuffer_size, screen_size):
    """Convert framebuffer position to screen position"""
    x_ratio = screen_size[0] / framebuffer_size[0]
    y_ratio = screen_size[1] / framebuffer_size[1]
    return (pos[0] * x_ratio, pos[1] * y_ratio)

def framebuffer_pos_to_screen_pos_int(pos, framebuffer_size, screen_size):
    """Convert framebuffer position to screen position"""
    ratio = framebuffer_pos_to_screen_pos(pos, framebuffer_size, screen_size)
    return (int(ratio[0]), int(ratio[1]))

def framebuffer_rect_to_screen_rect_int(rect, framebuffer_size, screen_size):
    """Convert framebuffer rect to screen rect"""
    x_ratio = screen_size[0] / framebuffer_size[0]
    y_ratio = screen_size[1] / framebuffer_size[1]
    return pygame.Rect(
        rect.left * x_ratio,
        rect.top * y_ratio,
        rect.width * x_ratio,
        rect.height * y_ratio
    )

# ---------------------------- #
# mouse

def mouse_surface_to_framebuffer_pos(pos, framebuffer_size, screen_size):
    """Convert mouse surface position to framebuffer position"""
    return (pos[0] * framebuffer_size[0] / screen_size[0], pos[1] * framebuffer_size[1] / screen_size[1])

def mouse_surface_to_framebuffer_pos_int(pos, framebuffer_size, screen_size):
    """Convert mouse surface position to framebuffer position"""
    return (int(pos[0] * framebuffer_size[0] / screen_size[0]), int(pos[1] * framebuffer_size[1] / screen_size[1]))

def mouse_framebuffer_to_surface_pos(pos, framebuffer_size, screen_size):
    """Convert mouse framebuffer position to surface position"""
    return (pos[0] * screen_size[0] / framebuffer_size[0], pos[1] * screen_size[1] / framebuffer_size[1])

def mouse_framebuffer_to_surface_pos_int(pos, framebuffer_size, screen_size):
    """Convert mouse framebuffer position to surface position"""
    return (int(pos[0] * screen_size[0] / framebuffer_size[0]), int(pos[1] * screen_size[1] / framebuffer_size[1]))

# ---------------------------- #


