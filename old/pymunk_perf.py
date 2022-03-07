import arcade
import pymunk
import random
from pymunk import Vec2d
import numpy as np
from dick import Dick, MobiDick
import time
from skimage import io
import math

 
def dummy_handler(_arbiter, _space, _data):
    """ Called for bullet/wall collision """

    w = _data['world']
    w.count_collision += 1
    return True

class DickWorld(arcade.Window):
    
    def __init__(self, w, h, scale, collision=None):

        random.seed(0)


        super().__init__(int(w*scale), int(h*scale), visible=False)

        self.scale = scale
        self.w = w
        self.h = h

        self.env = arcade.PymunkPhysicsEngine(damping = 1, gravity=(0, 0) )

        if collision == 'pm':
            h = self.env.space.add_collision_handler(0, 1)
            h.pre_solve = dummy_handler
            h.data['world'] = self
       
        if collision == 'pm_sh':
            h = self.env.space.add_collision_handler(0, 1)
            h.pre_solve = dummy_handler
            h.data['world'] = self
        
        # self.env.space.use_spatial_hash(50, 50000)
       

    
        self.scale = scale

        spatial_hash = False
        if collision == 'arcade_sh':
             spatial_hash = True

        self.dick_sprites = arcade.SpriteList(use_spatial_hash=spatial_hash)
        self.mobidick_sprites = arcade.SpriteList(use_spatial_hash=spatial_hash)
        
        self.dicks = {}
        self.collision = collision         
        self.count_collision = 0

       
    def add_object(self, dick):
              
        
        x = random.randint(00, self.w)*self.scale
        y = random.randint(00, self.h)*self.scale

        angle = random.uniform(-2, 2)

        if dick == 'dick':
            sprite = arcade.Sprite('dick.png', hit_box_algorithm='Detailed',hit_box_detail=0.1*self.scale, scale=self.scale)
            body_type = pymunk.Body.STATIC
            col = 'dick' 
            self.dick_sprites.append(sprite)
            sprite.center_x = x
            sprite.center_y = y
            sprite.angle = angle*180/math.pi

        else:
            sprite = arcade.Sprite('mobidick.png', hit_box_algorithm='Detailed',hit_box_detail=0.1*self.scale, scale=self.scale)
            body_type = pymunk.Body.DYNAMIC
            col = 'mobidick'
            self.mobidick_sprites.append(sprite)

        self.env.add_sprite(sprite, body_type=body_type, collision_type=col)
        # self.env.set_position(sprite, (x, y))
        
        self.env.get_physics_object(sprite).body.angle = angle 
        self.env.get_physics_object(sprite).body.position = (x, y) 


    def on_update(self):
       
        self.clear()
        for sprite in self.mobidick_sprites: 
            if random.uniform(0, 1) > 0.9:
                fx = random.uniform(-100, 100)*self.scale
                fy = random.uniform(-100, 100)*self.scale
                angular_speed = random.uniform(-1, 1)
                self.env.set_velocity(sprite, (fx, fy))
                self.env.get_physics_object(sprite).body.angular_velocity = angular_speed

            sprite.draw_hit_box((250, 20, 30), 1)

        self.dick_sprites.draw()
        self.mobidick_sprites.draw()

        self.env.step()

        # if self.collision == 'arcade' or self.collision == 'arcade_sh':
        #     for d in self.mobidick_sprites:
        #         self.count_collision += len(arcade.check_for_collision_with_list(d, self.dick_sprites))



def run_perf(n_dicks, n_mobidicks, envir_size, scale):

    size = envir_size, envir_size

    env = DickWorld( *size , scale, None) 

    for _ in range(n_dicks):
        env.add_object('dick')
        
    for _ in range(n_mobidicks):
        env.add_object('mobidick')
        # x = random.randint(-400, 400)
        # y = random.randint(-400, 400)
        # angle = random.uniform(-2, 2)

        # dick = MobiDick(Vec2d(x, y), angle)
        # env.add_object(dick)

    # arcade.run()

    t1 = time.time()

    for _ in range(10000):
        env.on_update()

    print(envir_size, scale,  10000 / (time.time() - t1), env.count_collision)
       

if __name__ == '__main__':

    run_perf(100, 5, 1000, 0.01)
    run_perf(100, 5, 1000, 0.1)
    run_perf(100, 5, 1000, 1)
    run_perf(100, 5, 1000, 0.01)
    run_perf(100, 5, 1000, 0.1)
    run_perf(100, 5, 1000, 1)
    # run_perf(500, 20, 1000, 5)
    # run_perf(500, 20, 1000, 5)
    # run_perf(500, 20, 1000, 10)
