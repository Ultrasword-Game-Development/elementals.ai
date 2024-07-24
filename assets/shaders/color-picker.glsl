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

// Input from the vertex shader
in vec2 uvs;

// Output color
out vec4 fragColor;

// Uniform color variable
uniform vec3 color;

void main()
{
    vec3 white = vec3(1.0, 1.0, 1.0);
    vec3 black = vec3(0.0, 0.0, 0.0);

    // interpolate between topleft, topright based on x coords
    vec3 topColor = mix(white, color, uvs.x);
    vec3 finalColor = mix(topColor, black, uvs.y);    

    // Set the fragment color
    fragColor = vec4(finalColor, 1.0);
}
