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

# ---------------------------- #
# surface

def palette_swap(surf, old_c, new_c):
    """Palette swap function"""
    c_copy = surf.copy()
    c_copy.fill(new_c)
    c_surf = surf.copy()
    c_surf.set_colorkey(old_c)
    c_copy.blit(c_surf, (0, 0))
    return c_copy

def clip(image, x, y, w, h):
    """Clip a rect from a surface"""
    return image.subsurface(pygame.Rect(x, y, w, h)).convert_alpha().copy()

def framebuffer_pos_to_screen_pos(pos, framebuffer_size, screen_size):
    """Convert framebuffer position to screen position"""
    return (pos[0] * screen_size[0] / framebuffer_size[0], pos[1] * screen_size[1] / framebuffer_size[1])

def framebuffer_pos_to_screen_pos_int(pos, framebuffer_size, screen_size):
    """Convert framebuffer position to screen position"""
    return (int(pos[0] * screen_size[0] / framebuffer_size[0]), int(pos[1] * screen_size[1] / framebuffer_size[1]))


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


