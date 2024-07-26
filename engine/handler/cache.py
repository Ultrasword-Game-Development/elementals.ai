


# ---------------------------- #
# constants


# ---------------------------- #
# cache

class MobileCache:
    def __init__(self) -> None:
        """ Initialize the mobile cache """
        self._cache = {}
    
    def __getitem__(self, key):
        """ Get the item """
        return self._cache[key]
    
    def __setitem__(self, key, value):
        """ Set the item """
        self._cache[key] = value