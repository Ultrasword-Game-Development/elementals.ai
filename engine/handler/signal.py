import time
import pygame


# ---------------------------- #
# util functions

SIGNAL_CACHE = {}
EVENT_QUEUE = []

DATA = "data"
TIME = "time"
PARENT = "parent"

def cache_signal(signal):
    """ Cache a GLOBAL signal to the cache """
    SIGNAL_CACHE[hash(signal)] = signal

def get_signal(name: str):
    """ Get a signal from the cache """
    return SIGNAL_CACHE.get(hash(name))

def update_signals():
    """ Update all signals """
    EVENT_QUEUE.sort(key=lambda e: [e[PARENT]._urgency, e[TIME]])
    for item in EVENT_QUEUE:
        item[PARENT].handle(item)
    EVENT_QUEUE.clear()

def push_to_signal_queue(parent, time: float, data: dict):
    """ Push a signal event to the queue """
    EVENT_QUEUE.append({PARENT: parent, TIME: time, DATA: data})

# ---------------------------- #
# signal

class Signal:    
    def __init__(self, name: str, urgency: int = 0):
        """ Create a new signal """
        self._name = name
        self._urgency = urgency
        self._registries = []
        self._emitter_handling_functions = []

        # requirements for data sending
        self._data_requirements = []

        # self-register
        cache_signal(self)
    
    def handle(self, blob: dict):
        """ Handle the signal """
        for ifunc in self._emitter_handling_functions:
            # TODO - singleton debug output log
            # blob[TIME]
            # blob[PARENT]
            ifunc(blob[DATA])
    
    def add_data_requirement(self, key: str):
        """ Add a data requirement """
        self._data_requirements.append(key)

    def add_emitter_handling_function(self, func):
        """ Add a handling function for an emitter """
        self._emitter_handling_functions.append(func)

    def get_unique_emitter(self):
        """ Return a signal registry """
        self._registries.append(SignalEmitter(self))
        return self._registries[-1]

    def __hash__(self):
        """ Return the hash of the signal """
        return hash(self._name)
    
    # ---------------------------- #
    # pickle

    def __getstate__(self):
        """ Pickle state """
        state = self.__dict__.copy()
        # remove unpicklable entries
        del state['_registries']
        return state

    def __setstate__(self, state):
        """ Unpickle state """
        self.__dict__.update(state)
        # restore unpicklable entries
        self._registries = []
        cache_signal(self)


# ---------------------------- #
# signal registry

class SignalEmitter:
    def __init__(self, parent: Signal):
        """ Create a new signal register """
        self._name = parent._name
        self._parent = parent
    
    def get_urgency(self):
        """ Return the urgency of the signal """
        return self._parent._urgency
    
    def emit(self, data: dict = {}):
        """ Emit a signal """
        for i in self._parent._data_requirements:
            if i not in data:
                raise ValueError(f"Data requirement not met: {i}\nData for Signal of name: {self._name}")
        push_to_signal_queue(self._parent, time.time(), data)
    
    # ---------------------------- #
    # pickle

    def __getstate__(self):
        """ Pickle state """
        state = self.__dict__.copy()
        # remove unpicklable entries
        del state['_parent']
        return state

    def __setstate__(self, state):
        """ Unpickle state """
        self.__dict__.update(state)
        # restore unpicklable entries
        self._parent = get_signal(state['_name'])

