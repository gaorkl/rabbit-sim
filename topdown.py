import arcade
import pymunk
import numpy as np 
from PIL import Image, ImageShow


class TopDownView:

    def __init__(self, env, center, size, zoom, id_view = False) -> None:
       
        w, h = size
        self.width = w
        self.height = h

        self.size = size

        self.center = center
        self.zoom = zoom
        self.env = env
        env.views.append(self)
       
        self.ctx = env.ctx

        self.id_view = id_view

        # super().__init__(w, h, visible=visible, antialiasing=False)

        self.sprites = arcade.SpriteList()
       
        self.radius = pymunk.Vec2d(w/2, h/2).length / zoom 
        
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

    def imdisplay(self):
        array = np.frombuffer(self.fbo.read(), dtype=np.dtype('B')).reshape(self.height, self.width, 3)
        img = Image.fromarray(array, 'RGB')
        ImageShow.show(img, 'test')



