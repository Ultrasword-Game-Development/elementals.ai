===v
#version 330 core

in vec2 vert;
in vec2 texcoord;
out vec2 uvs;

void main(){
    uvs = texcoord;
    gl_Position = vec4(vert, 0.0, 1.0);
}

===f
#version 330 core

uniform sampler2D tex;
uniform float time;
uniform long seed;
uniform float z;

in vec2 uvs;
out vec4 color;

float noise3D(long seed, float x, float y, float z);

void main(){
    time;
    // vec2 spos = vec2(uvs.x + sin(uvs.y * 10 + time) * 0.1, uvs.y);
    vec2 spos = uvs;
    float perlin = noise3D(spos.x, spos.y, z);
    color = vec4(texture(tex, spos).xy, texture(tex, spos).z, 1.0);
}


