from topdown import TopDownView
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
    
    def __init__(self, size, n_rabbits, n_wrabbits, n_carrots, seed):

        random.seed(seed)
        self.w, self.h = size
        self.size = size

        self.space = pymunk.Space()
        self.space.damping = 0.9
        self.space.gravity = (0, 0)

        hand = self.space.add_collision_handler(0, 1)
        hand.post_solve = dummy_handler
        hand.data['world'] = self
              
        self.elems = []
        self.ids = {}

        self.count_collision = 0

    
        self.elems.append(Wall(self, (-self.w/2, -self.h/2), (-self.w/2, self.h/2), 20))
        self.elems.append(Wall(self, (-self.w/2, self.h/2), ( self.w/2, self.h/2), 20))
        self.elems.append(Wall(self, ( self.w/2,  self.h/2), ( self.w/2, -self.h/2), 20))
        self.elems.append(Wall(self, (self.w/2, -self.h/2), (-self.w/2, -self.h/2), 20))

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

    @property
    def all_ids(self):

        return [elem.get_id_pixel() for elem in self.elems]

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

if __name__ == '__main__':

    env = RabbitWorld( (1000, 200), n_rabbits=50, n_wrabbits=10, n_carrots=20, seed=42)
    view = TopDownView(env, (0,0), env.size, scale=1, id_view=False)
            
    env.step()
    view.buf_update()
    
    view.imdisplay()
