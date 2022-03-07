import arcade
import pymunk
import random
from pymunk import Vec2d
import numpy as np
from elements import Carrot, Rabbit, Wall, WereRabbit
import time
from skimage import io
import math
from PIL import Image
from PIL import ImageShow
from sensors.rgb_topdown import CameraSensor

def dummy_handler(_arbiter, _space, _data):
    w = _data['world']
    w.count_collision += 1
    return True


class RabbitWorld(object):
    
    def __init__(self, w, h, n_rabbits, n_wrabbits, n_carrots, seed):

        random.seed(seed)
        self.w = w
        self.h = h

        self.space = pymunk.Space()
        self.space.damping = 0.9
        self.space.gravity = (0, 0)

        hand = self.space.add_collision_handler(0, 1)
        hand.post_solve = dummy_handler
        hand.data['world'] = self
              
        self.elems = []
        self.ids = {}

        self.count_collision = 0

    
        self.elems.append(Wall(self, (-w/2, -h/2), (-w/2, h/2), 20))
        self.elems.append(Wall(self, (-w/2, h/2), ( w/2, h/2), 20))
        self.elems.append(Wall(self, ( w/2,  h/2), ( w/2, -h/2), 20))
        self.elems.append(Wall(self, (w/2, -h/2), (-w/2, -h/2), 20))

        for _ in range(n_rabbits):
            self.add_element('rabbit')
 
        for _ in range(n_wrabbits):
            self.add_element('wererabbit')

        for _ in range(n_carrots):
            self.add_element('carrot')


        self.views = []

    def get_id(self, elem):

        id = 0
        while True:
            a = random.randint(0, 2**24)
            if a not in self.ids:
                id = a
                break

        self.ids[id] =  elem

        return id

    def add_element(self, elem_name):
              
        x = random.randint(-self.w/2, self.w/2)
        y = random.randint(-self.h/2, self.h/2)

        angle = random.uniform(-2, 2)

        
        if elem_name == 'rabbit':
            elem = Rabbit(self, ((x, y), angle))

        elif elem_name == 'wererabbit':
            elem = WereRabbit(self, ((x, y), angle))

        elif elem_name == 'carrot':
            elem = Carrot(self, ((x, y), angle))
 
        else:
            raise ValueError

        self.elems.append(elem)
    
    def step(self):
       
        for elem in self.elems:

            if isinstance(elem, Rabbit) and random.uniform(0, 1) > 0.9:
                fx = random.uniform(-10, 10)
                fy = random.uniform(-10, 10)
                angular_speed = random.uniform(-1, 1)
                elem.body.velocity = fx, fy
                elem.body.angular_velocity = angular_speed

        self.space.step(dt=0.1)

        for view in self.views:
            view.buf_update()


class View(arcade.Window):

    def __init__(self, env, center, size, scale, visible=False, id_view = False) -> None:
       
        w, h = size
        self.center = center
        self.scale = scale
        self.env = env
        env.views.append(self)
        
        self.id_view = id_view

        super().__init__(w, h, visible=visible)

        self.sprites = arcade.SpriteList()
        
        self.radius = pymunk.Vec2d(w/2, h/2).length / scale 

        self.fbo = self.ctx.framebuffer(
            color_attachments=[
                self.ctx.texture(
                    (size),
                    components=4,
                    wrap_x=self.ctx.CLAMP_TO_BORDER,
                    wrap_y=self.ctx.CLAMP_TO_BORDER,
                ),
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
            self.sprites.draw()

    def on_draw(self):
        self.env.step()
        self.clear()
        self.sprites.draw()
        # self.sprites.draw_hit_boxes(line_thickness=3, color=(255, 0, 0))
    
    def imdisplay(self):
        array = np.frombuffer(self.fbo.read(), dtype=np.dtype('B')).reshape(self.width, self.height, 3)
        img = Image.fromarray(array, 'RGB')
        ImageShow.show(img, 'test')


if __name__ == '__main__':

    n_tries = 10 #50
    n_rabbits = 20 
    n_wrabbits = 0
    n_carrots = 100
    env_size  = 1000
    # view_size = 2000 
    view_scale = 1

    for n_sensor in [ 0,1,2, 3, 5, 10]:
        t = []
        c = []
        seed=120


        for n in range(n_tries):
            env = RabbitWorld(env_size, env_size, n_rabbits, n_wrabbits, n_carrots, seed)
            view = View(env, (0,0), (env_size, env_size), view_scale, False)
            
            master_wrabbit = WereRabbit(env, ((0, 0), 0) )
            env.add_element(master_wrabbit)
            
            sensors = []
            for _ in range(n_sensor):
                sensors.append(CameraSensor(master_wrabbit, view, range=32))

            t1 = time.time()
            for _ in range(10000):
                env.step()
                for sensor in sensors:
                    sensor.update_sensor()

                    # np.frombuffer(sensor.output_fbo.read(), dtype=np.dtype('B'))
                    # array = np.frombuffer(self.output_fbo.read(), dtype=np.dtype('B')).reshape(401, 401, 3)
        # img = Image.fromarray(array, 'RGB')
        # ImageShow.show(img, 'test')

            
            t.append(10000/(time.time()-t1))
            c.append(env.count_collision)
         
            seed += 1
            del env
            del view
            del sensors


        # view.use()
        # np_array_v = np.frombuffer(bgview_2.ctx.fbo.read(), dtype=np.dtype('b'))
        # img_v = np_array_v.reshape((env_size, env_size, 3))

        # bgview.use()
        # np_array_bgv = np.frombuffer(view.ctx.fbo.read(), dtype=np.dtype('b'))
        # img_bgv = np_array_bgv.reshape((env_size, env_size, 3))

        # io.imshow(img_bgv)
        # io.show()
        # assert np.all(img_v == img_bgv)


        # bg_view.close()
        # bgview.close()
        # bgview_2.close()
        print( n_sensor, sum(t)/len(t), sum(c)/len(c))
