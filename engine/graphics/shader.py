import pygame

from engine import singleton

# ---------------------------- #
# utils

SHADER_CACHE = {}

SHADER_TYPE = 0
SHADER_CODE = 1

CALL_VERTEX = "===v"
CALL_FRAGMENT = "===f"
CALL_COMPUTE = "===c"
CALL_RTX = "===r"

TYPE_VERTEX = 0
TYPE_FRAGMENT = 1
TYPE_COMPUTE = 2
TYPE_RTX = 3

CALL_MAPPING = {
    CALL_VERTEX: TYPE_VERTEX,
    CALL_FRAGMENT: TYPE_FRAGMENT,
    CALL_COMPUTE: TYPE_COMPUTE,
    CALL_RTX: TYPE_RTX
}

TYPE_MAPPING = {
    TYPE_VERTEX: CALL_VERTEX,
    TYPE_FRAGMENT: CALL_FRAGMENT,
    TYPE_COMPUTE: CALL_COMPUTE,
    TYPE_RTX: CALL_RTX
}


def load_shader(path: str):
    """ Loads a shader to the cache """
    if path in SHADER_CACHE:
        return SHADER_CACHE[path]
    shader = ShaderProgram(path)
    shader.create()
    SHADER_CACHE[path] = shader
    return shader

# ---------------------------- #
# shader class

class ShaderProgram:
    """ Only Supports Framgent+Vertex Simple Shaders """

    def __init__(self, path: str):
        """ Create a new shader """
        self._path = path

        self._shaders = []
        self._program = None
        
        self._vertex_arrays = {}

    def create(self):
        """ Create the shader program """
        # read the text file
        with open(self._path, "r") as f:
            data = f.read()
        
        # read data
        layers = []
        code = []
        shadertype = -1
        for line in data.split('\n'):
            if line in CALL_MAPPING:
                if shadertype != -1:
                    self._shaders.append((shadertype, "\n".join(code)))
                    code = []
                shadertype = CALL_MAPPING[line]
            else:
                code.append(line)
        self._shaders.append((shadertype, "\n".join(code)))
        self._shaders.sort(key=lambda x: x[0])

        # create the program
        self._program = singleton.CONTEXT.program(
                    vertex_shader = self._shaders[0][SHADER_CODE],
                    fragment_shader = self._shaders[1][SHADER_CODE])
    
    def load_quad_vertexarray(self, name: str, program=None, buffer: list = None, *args, **kwargs):
        """ Create a quad buffer """
        if not program:
            if name not in self._vertex_arrays:
                raise ValueError(f"Shader Program of name : `{name}` not found")
            return self._vertex_arrays[name]
        vao = singleton.CONTEXT.vertex_array(program, buffer, *args, **kwargs)
        self._vertex_arrays[name] = vao
        return self._vertex_arrays[name]

    def __getitem__(self, key):
        """ Get an item """
        return self._program[key]
    
    def __setitem__(self, key, value):
        """ Set an item """
        self._program[key] = value


