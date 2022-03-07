import arcade
import pymunk
import numpy as np 
from PIL import Image, ImageShow


class TopDownView(arcade.Window):

    def __init__(self, env, center, size, scale, visible=False, id_view = False) -> None:
       
        w, h = size
        self.center = center
        self.scale = scale
        self.env = env
        env.views.append(self)
        
        self.id_view = id_view

        super().__init__(w, h, visible=visible, antialiasing=False)

        self.sprites = arcade.SpriteList()
        
        self.radius = pymunk.Vec2d(w/2, h/2).length / scale 
        
        # self.ctx.enable_only(self.ctx.ONE)
        self.ctx.blend_func = self.ctx.ONE, self.ctx.ZERO
        
        self.fbo = self.ctx.framebuffer(
            color_attachments=[
                self.ctx.texture(
                    (size),
                    components=4,
                    wrap_x=self.ctx.CLAMP_TO_BORDER,
                    wrap_y=self.ctx.CLAMP_TO_BORDER,
                    filter= (self.ctx.NEAREST, self.ctx.NEAREST
                )),
            ]
        )

    @property
    def texture(self):
        """The OpenGL texture containing the map pixel data"""
        return self.fbo.color_attachments[0]
    
    def update_sprites(self):

        for elem in self.env.elems:
            elem.update_sprite(self)

    def buf_update(self):
        # self.ctx.projection_2d = 0, self.width, 0, self.height
        self.update_sprites()
        with self.fbo.activate() as fbo:
            fbo.clear()
            # Change projection to match the contents
            self.ctx.projection_2d = 0, self.width, 0, self.height
            self.sprites.draw(pixelated=True)

    def on_draw(self):
        self.env.step()
        self.clear()
        self.sprites.draw()
        # self.sprites.draw_hit_boxes(line_thickness=3, color=(255, 0, 0))
    
    def imdisplay(self):
        array = np.frombuffer(self.fbo.read(), dtype=np.dtype('B')).reshape(self.height, self.width, 3)
        img = Image.fromarray(array, 'RGB')
        ImageShow.show(img, 'test')



