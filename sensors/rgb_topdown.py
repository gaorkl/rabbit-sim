
from arcade.gl import geometry


class CameraSensor:

    def __init__(self, element, view, range):

        self.view = view
        self.element = element
        self.range = range

        self.ctx = self.view.ctx
        
        self.output_texture = self.ctx.texture((2*range, 2*range),
                                               components=4,
                                               wrap_x = self.ctx.CLAMP_TO_BORDER,
                                               wrap_y = self.ctx.CLAMP_TO_BORDER,
                                               filter= (self.ctx.NEAREST, self.ctx.NEAREST
                                               ))

        self.output_fbo=self.ctx.framebuffer(color_attachments=[self.output_texture])

        self.quad_2d_fs = geometry.quad_2d_fs()
        
        self.sensor_shader = self.ctx.program(
            vertex_shader="""
            #version 330
            uniform vec2 pos;
            uniform float angle;
            in vec2 in_vert;
            in vec2 in_uv;
            out vec3 uv;
            void main() {
                gl_Position = vec4(in_vert, 0.0, 1.0);
                mat3 trans = mat3(
                    1.0, 0.0, 0.0,
                    0.0, 1.0, 0.0,
                    pos.x, pos.y, 1.0
                );
                float s = 1;
                mat3 scale = mat3(
                    s, 0.0, 0.0,
                    0.0, s, 0.0,
                    0.0, 0.0, s
                );
                mat3 rot = mat3(
                    cos(angle), -sin(angle), 0.0,
                    sin(angle),  cos(angle), 0.0,
                    0.0, 0.0, 1.0
                );
                // uv = trans * rot * scale * vec3(in_uv - vec2(0.5), 1.0) + vec3(0.5);
                uv = scale* rot* trans * vec3(in_uv - vec2(0.5, 0.5), 1.0) + vec3(0.5, 0.5, 0) ; 
            }
            """,
            fragment_shader="""
            #version 330
            uniform sampler2D map;
            in vec3 uv;
            out vec4 fragColor;
            void main() {
                fragColor = texture(map, uv.xy);
            }
            """,
        )


    def update_sensor(self):
        self.output_fbo.clear() 
        self.view.texture.use()
        self.output_fbo.use()
        self.ctx.projection_2d = 0, self.range, 0, self.range
        
        program = self.sensor_shader
        program["pos"] = self.element.body.position.x/self.view.width/2, self.element.body.position.y/self.view.height/2 
        program["angle"] = self.element.body.angle


        self.quad_2d_fs.render(program)

