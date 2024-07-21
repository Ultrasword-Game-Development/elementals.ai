===v
#version 330 core

in vec2 vert;
in vec2 texcoord;
out vec2 uvs;

uniform float time;

void main(){
    uvs = texcoord;
    gl_Position = vec4(vert, 0.0, 1.0);
}

===f
#version 330 core

uniform sampler2D tex;
uniform float time;

in vec2 uvs;
out vec4 color;

void main(){
    vec2 spos = vec2(uvs.x + sin(uvs.y * 10 + time) * 0.1, uvs.y);
    color = vec4(texture(tex, spos).xy, texture(tex, spos).z * 1.5, 1.0);
}