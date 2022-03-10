import math
from typing import Optional
import arcade
import random
import pymunk
from pymunk import vec2d
from pymunk.vec2d import Vec2d
import numpy as np
import os
from PIL import Image, ImageShow


def id_to_pixel(id):

        id_0 =  id & 255
        id_1 = (id >> 8) & 255
        id_2 = (id >> 16) & 255

        return id_0, id_1, id_2


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
        orig_vertices = orig_sprite.get_hit_box()
        vertices = [[c*physical_scale for c in xy] for xy in orig_vertices]
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

        self.vertices = vertices
        self.borderpoints = self.compute_borderpoints(orig_vertices)
        self.colors_borderpoints = self.compute_colors_borderpoints()


    def compute_borderpoints(self, vertices):

        min_dist_between_points = 1

        points = []
        for index_vert, vert in enumerate(vertices):
            
            prev_vert = vertices[index_vert - 1]
            
            len_segment = (Vec2d(*vert) - Vec2d(*prev_vert)).length 
            n_points = int(len_segment/min_dist_between_points) - 1
            
            xs = np.linspace(vert[0], prev_vert[0], n_points+2)
            ys = np.linspace(vert[1], prev_vert[1], n_points+2)

            for i in range(len(xs)-1):
                points.append((xs[i], ys[i]))

        return points

    def compute_colors_borderpoints(self):

        colors_bp = {}

        img = self.texture.image
        np_img = np.array(img)

        r, c = np.nonzero( np_img.sum(axis=2) )

        for x, y in self.borderpoints:
           
            # convert x to col
            c_pt = x + img.width/2
            r_pt = img.height - (y + img.height/2)

            min_idx = ((r - r_pt)**2 + (c - c_pt)**2).argmin()
    
            coord_min_x = r[min_idx]
            coord_min_y = c[min_idx]

            color = np_img[coord_min_x, coord_min_y]

            colors_bp[(x, y)] = tuple(color)

        return colors_bp

    def get_pixel_from_point(self, pt):

        abs_pt = Vec2d(*pt)
        rel_pt = (abs_pt - self.position).rotated(-self.body.angle)

        x_pt, y_pt = rel_pt

        distances = { (x, y) : (x_pt-x)**2 + (y_pt - y)**2 for (x,y), color in self.colors_borderpoints.items() }

        closets_pt = min(distances, key=distances.get)
       
        return self.colors_borderpoints[closets_pt]


    def _get_sprite(self, scale, id_sprite):
        scale_ = scale * self.physical_scale
     
        if id_sprite:
            id_img = Image.new('RGBA', (self.texture.width, self.texture.height))
       
            pixels = id_img.load()
            pixels_text = self.texture.image.load()
 
           
            id_0, id_1, id_2 = id_to_pixel(self.id)
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
        
        sprite = self._get_sprite(view.zoom, view.id_view)

        self.sprites[view] = sprite

        self._update_sprite_position(view, sprite)

        view.sprites.append(sprite)

    def _update_sprite_position(self, view, sprite):

        pos_x = (self.body.position.x - view.center[0])*view.zoom + view.width // 2
        pos_y = (self.body.position.y - view.center[1])*view.zoom + view.height // 2
        
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

    ind_wall = 0

    def __init__(self, env, start_pt, end_pt, width) -> None:
        
        INITIAL_WIDTH = 16
        ratio = width/INITIAL_WIDTH
    
        start_pt = pymunk.Vec2d(*start_pt)
        end_pt = pymunk.Vec2d(*end_pt)
        pos = (start_pt + end_pt)/2
        angle = (end_pt-start_pt).angle

        width_out_texture = int((end_pt - start_pt).length)
        height_out_texture = int(32*ratio)

        fname = self.get_file_name('wall.png')
        wall_block_texture = arcade.load_texture(fname)
        pixels_wall = wall_block_texture.image.load()

        full_wall_image = Image.new('RGBA', (width_out_texture, height_out_texture))
       
        pixels_full_wall = full_wall_image.load()
        for i in range(full_wall_image.size[0]):
            for j in range(full_wall_image.size[1]):

                j_wall = int(32*j/(32*ratio))
                i_wall = i%32
               
                pixels_full_wall[i, j] = pixels_wall[i_wall, j_wall]

        Wall.ind_wall += 1
        name_wall = 'wall'+str(Wall.ind_wall)

        texture = arcade.Texture(name=name_wall, image=full_wall_image,hit_box_algorithm='Detailed', hit_box_detail=0.1)

        super().__init__(env, (pos, angle), texture=texture, mass=None, physical_scale=1)

