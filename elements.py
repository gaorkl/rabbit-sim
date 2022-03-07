import math
from typing import Optional
import arcade
import random
import pymunk
from pymunk.vec2d import Vec2d
import numpy as np
import os
from PIL import Image, ImageShow

class BaseElement(object):

    def __init__(self,
                 env,
                 coord,
                 texture,
                 mass: Optional[float] = None,
                 physical_scale = 1,
                 group = None,
                 ) -> None:

        self.env = env
        self.physical_scale = physical_scale
        self.texture = texture

        self.group = group
        self.id = self.env.get_id(self)
        
        orig_sprite = self._get_sprite(scale=1, id_sprite=False)
        vertices = orig_sprite.get_hit_box()
        vertices = [[c*physical_scale for c in xy] for xy in vertices]
        self.radius = max([pymunk.Vec2d(*vert).length for vert in vertices])


        if mass:
            moment = pymunk.moment_for_poly(mass, vertices)
            body = pymunk.Body(mass, moment, pymunk.Body.DYNAMIC)
        else:
            body = pymunk.Body(body_type=pymunk.Body.STATIC)
        shape = pymunk.Poly(body=body, vertices=vertices)

        pos, angle = coord
        body.position, body.angle = pos, angle
        self.env.space.add(body, shape)

        self.body = body
        self.shape = shape

        self.sprites = {}

    def get_id_pixel(self):

        id_0 =  self.id & 255
        id_1 = (self.id >> 8) & 255
        id_2 = (self.id >> 16) & 255

        return id_0, id_1, id_2

    def _get_sprite(self, scale, id_sprite):
        scale_ = scale * self.physical_scale
     
        if id_sprite:
            id_img = Image.new('RGBA', (self.texture.width, self.texture.height))
       
            pixels = id_img.load()
            pixels_text = self.texture.image.load()
 
 
            # id_0 = random.randint(0, 255)
            # id_1 = random.randint(0, 255)
            # id_group = random.randint(0, 255)
            # id_el_type = 255
           
            id_0, id_1, id_2 = self.get_id_pixel()
            alpha = 255 

            for i in range(id_img.size[0]):
                for j in range(id_img.size[1]):

                    if pixels_text[i, j] != (0,0,0,0):
                        px = (id_0, id_1, id_2, alpha)
                        pixels[i, j] = px

            name = str(self.id) # Add view id too!

            texture = arcade.Texture(name=name, image=id_img,hit_box_algorithm='Detailed', hit_box_detail=0.1)
            sprite = arcade.Sprite(texture=texture, scale=scale_, hit_box_algorithm='Detailed', hit_box_detail=0.1)

        else:
            sprite = arcade.Sprite(texture=self.texture, scale=scale_, hit_box_algorithm='Detailed', hit_box_detail=0.1)

        # sprite = arcade.Sprite(texture=texture, scale=scale_, hit_box_algorithm='Detailed', hit_box_detail=0.1)
        # self._center_sprite(sprite)

        return sprite

    def _center_sprite(self, sprite):
        vertices = sprite.get_hit_box()
        vertices_np = np.array(vertices)
        center = np.mean(vertices_np, axis=0)
        # new_vertices = 
        # sprite.hitimage_x, sprite.offset_y = center[0], center[1]

        
    @property
    def position(self):
        return self.body.position

    def _add_sprite(self, view):
        
        sprite = self._get_sprite(view.scale, view.id_view)

        self.sprites[view] = sprite

        self._update_sprite_position(view, sprite)

        view.sprites.append(sprite)

    def _update_sprite_position(self, view, sprite):

        pos_x = self.body.position.x*view.scale + view.width // 2
        pos_y = self.body.position.y*view.scale + view.height // 2
        
        sprite.set_position(pos_x, pos_y)
        sprite.angle = int(self.body.angle*180/math.pi)


    def update_sprite(self, view):

        if view not in self.sprites.keys():
            self._add_sprite(view)

        sprite = self.sprites[view]

        if self.body.body_type == pymunk.Body.DYNAMIC:
             
            # dist = (self.position - view.center).length

            # if dist < self.radius + view.radius:
            self._update_sprite_position(view, sprite)

    def get_file_name(self, name):
         return os.path.join(os.path.dirname(__file__), 'assets', name)


class Carrot(BaseElement):

    def __init__(self, env, coord) -> None:

        fname = self.get_file_name('carrot.png')
        texture = arcade.load_texture(fname, hit_box_algorithm='Detailed', hit_box_detail=0.1)
       
        
        super().__init__(env, coord, texture, mass=None, physical_scale=1)


class Rabbit(BaseElement):

    def __init__(self, env, coord) -> None:

        mass_rabbit = 5
        
        fname = self.get_file_name('rabbit.png')
        texture = arcade.load_texture(fname, hit_box_algorithm='Detailed', hit_box_detail=0.1)

        super().__init__(env, coord, texture, mass=mass_rabbit, physical_scale=1)


class WereRabbit(BaseElement):

    def __init__(self, env, coord) -> None:

        mass_wrabbit = 10
        
        fname = self.get_file_name('wererabbit.png')
        texture = arcade.load_texture(fname, hit_box_algorithm='Detailed', hit_box_detail=0.1)

        super().__init__(env, coord, texture, mass=mass_wrabbit, physical_scale=1.5)


class Wall(BaseElement):
    def __init__(self, env, start_pt, end_pt, width) -> None:
        
        INITIAL_WIDTH = 16
        ratio = width/INITIAL_WIDTH
    
        start_pt = pymunk.Vec2d(*start_pt)
        end_pt = pymunk.Vec2d(*end_pt)
        pos = (start_pt + end_pt)/2
        angle = (end_pt-start_pt).angle
        length_wall = int((end_pt - start_pt).length*ratio)
        
        fname = self.get_file_name('wall.png')
        wall_block_texture = arcade.load_texture(fname)
        pixels_wall = wall_block_texture.image.load()

        full_wall_image = Image.new('RGBA', (length_wall, wall_block_texture.size[1]))
        
       
        pixels_full_wall = full_wall_image.load()
        for i in range(full_wall_image.size[0]):
            for j in range(full_wall_image.size[1]):

                i_wall = i%wall_block_texture.width
                j_wall = j%wall_block_texture.height
                pixels_full_wall[i, j] = pixels_wall[i_wall, j_wall]

        texture = arcade.Texture(name='test', image=full_wall_image,hit_box_algorithm='Detailed', hit_box_detail=0.1)

        super().__init__(env, (pos, angle), texture=texture, mass=None, physical_scale=1/ratio)


