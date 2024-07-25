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

in vec2 uvs;
uniform vec4 color;

out vec4 fcolor;

uniform float time;

void main()
{
    time;
    vec4 white = vec4(1.0, 1.0, 1.0, 1.0);
    vec4 black = vec4(0.0, 0.0, 0.0, 1.0);

    // // interpolate between topleft, topright based on x coords
    // vec4 brightness = mix(white, black, uvs.y);
    // vec4 sideColor = mix(black, color, uvs.x);

    // // Set the fragment color
    // fcolor = ;
        // Interpolate between white and the specified color based on the x-coordinate
    vec4 topColor = mix(white, color, uvs.x);

    // Interpolate between the top color and black based on the y-coordinate
    vec4 finalColor = mix(black, topColor, uvs.y);

    fcolor = finalColor;
    
}
