import arcade
from pymunk import Vec2d
import random
import math
import numpy as np
import time
from skimage import io

from  dick import SPGDick

class SPGView(arcade.Window):
    
    def __init__(self, w, h, scale):

        super().__init__(w, h, center_window=True, visible=False)

        self.scale = scale
        self.dick_sprites = arcade.SpriteList()
        self.dicks = []
        

    def add_object(self, dick):
        sprite = dick.sprite
        sprite.scale = self.scale
              
        dick.view_sprites[self] = dick.sprite

        self.dicks.append(dick)
        self.dick_sprites.append(dick.view_sprites[self])

        dick.setup(self)
        

    def on_draw(self):
       
        self.clear()
        for dick in self.dicks: 
            dick.update(self)

        self.dick_sprites.draw()

size = 1000, 1000
wind_1 = SPGView( *size , 1)

for _ in range(400):
    x = random.randint(-200, 200)
    y = random.randint(-200, 200)
    angle = random.uniform(-2, 2)

    movable = random.uniform(0, 1) > 0.9

    dick = SPGDick(Vec2d(x, y), angle, movable=movable)
    wind_1.add_object(dick)

wind_1.on_draw()

t1 = time.time()

for _ in range(10000):
    wind_1.on_draw()

print(10000 / (time.time() - t1))
np_array = np.frombuffer(wind_1.ctx.fbo.read(), dtype=np.dtype('b'))
img = np_array.reshape((*size, 3))

io.imshow(img)
io.show()

# arcade.run()
