


# ---------------------------- #

def hex_to_rgb(_hex: str):
    return tuple(int(_hex.strip('#')[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb: tuple):
    return '#%02x%02x%02x' % rgb

def hash_sha256(item):
    return hashlib.sha256(item)

# ---------------------------- #



