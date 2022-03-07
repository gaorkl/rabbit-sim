from elements import WereRabbit
import math
import numpy as np
import time
from PIL import Image, ImageShow, ImageDraw


from sensors.ray import RaySensor, RayShader, UniqueRaySensor
from env import RabbitWorld, View


def analyze_speed_rays(n_rays, range_rays, n_sensors):
    
    env = RabbitWorld(1000, 1000, 50, 10, 10, 0)
    view = View(env, (0,0), (1000, 1000), 1, False, id_view=True)

    sensors = []

    for i in range(n_sensors):
        sensors.append(UniqueRaySensor(view, n_rays=n_rays, range=range_rays, fov=3*math.pi/2, spatial_res=2))

    view.buf_update()

    cont = True
    x, y = 0, 0

    t1 = time.time()

    for i in range(10000):
        # env.step()
        for sensor in sensors:
            sensor.update_sensor()
            arr = np.frombuffer(sensor.output_pts_coord.read(), dtype=np.dtype('f')).reshape( -1, 8)
     
    print(n_rays, range_rays, n_sensors, 10000/(time.time() - t1))


def analyze_speed_ray_shader(n_rays, range_rays, n_sensors):
    
    env = RabbitWorld(1000, 1000, 50, 10, 10, 0)
    view = View(env, (0,0), (1000, 1000), 1, False, id_view=True)

    ray_shader = RayShader(view)

    for i in range(n_sensors):
        sensor = (RaySensor(n_rays=n_rays, range=range_rays, fov=3*math.pi/2, spatial_resolution=2))
        ray_shader.add_sensor(sensor)
        
    view.buf_update()

    t1 = time.time()

    for i in range(10000):
        # env.step()
        ray_shader.update_sensor()
        arr = np.frombuffer(ray_shader.output_rays_buffer.read(), dtype=np.dtype('f'))
     
    print(n_rays, range_rays, n_sensors, 10000/(time.time() - t1))

    ray_shader.ray_shader.delete()
    ray_shader.ctx.gc()
    del ray_shader


def visualize_ray_shader():

    env = RabbitWorld(1000, 1000, 50, 10, 10, 0)
    view = View(env, (0,0), (1000, 1000), 1, False, id_view=True)
    view_disp = View(env, (0,0), (1000, 1000), 1, False, id_view=False)

    ray_shader = RayShader(view)

    sensor_1 = RaySensor(n_rays=10, range=100, fov=math.pi/2, spatial_resolution=1)
    sensor_1.center = (100, 100)
    sensor_1.angle = 0
    ray_shader.add_sensor(sensor_1)
    
    sensor_2 = RaySensor(n_rays=100, range=200, fov=math.pi, spatial_resolution=1)
    sensor_2.center = (100, 900)
    sensor_2.angle = math.pi/2
    ray_shader.add_sensor(sensor_2)
    
    sensor_3 = RaySensor(n_rays=200, range=400, fov=3*math.pi/2, spatial_resolution=1)
    sensor_3.center = (900, 100)
    sensor_3.angle = math.pi
    ray_shader.add_sensor(sensor_3)
     
    sensor_4 = RaySensor(n_rays=500, range=50, fov=2*math.pi, spatial_resolution=1)
    sensor_4.center = (900, 900)
    sensor_4.angle = -math.pi
    ray_shader.add_sensor(sensor_4)
     

    view.buf_update()
    view_disp.buf_update()

    t1 = time.time()

    ray_shader.update_sensor()
 
    for sensor in ray_shader.sensors:
        array = np.frombuffer(view_disp.fbo.read(), dtype=np.dtype('B')).reshape(view.width, view.height, 3)
        img = Image.fromarray(array, 'RGB')

        d = ImageDraw.Draw(img)

        for pt in sensor.output:

            x, y = pt[:2]
            col = tuple( int(x) for x in pt[4:] )
            d.line((sensor.center[0], sensor.center[1], x, y), col)
    
        ImageShow.show(img, 'test')
    # # sensor.update_sensor()
    # # sensor.update_sensor()
 
def visualize_ray_invisible_elems():

    env = RabbitWorld(1000, 1000, 50, 10, 10, 0)
    view = View(env, (0,0), (1000, 1000), 1, False, id_view=True)
    view_disp = View(env, (0,0), (1000, 1000), 1, False, id_view=False)

    ray_shader = RayShader(view)

    ids_wererabbit = [elem.id for elem in env.elems if isinstance(elem, WereRabbit)]

    sensor_1 = RaySensor(n_rays=200, range=500, fov=2*math.pi, spatial_resolution=1)
    sensor_1.center = (500, 500)
    sensor_1.angle = 0
    sensor_1.invisible_ids = ids_wererabbit
    
    ray_shader.add_sensor(sensor_1)
    # ray_shader.add_sensor(sensor_1)
    
   

    view.buf_update()
    view_disp.buf_update()

    t1 = time.time()

    ray_shader.update_sensor()
 
    for sensor in ray_shader.sensors:
        array = np.frombuffer(view_disp.fbo.read(), dtype=np.dtype('B')).reshape(view.width, view.height, 3)
        img = Image.fromarray(array, 'RGB')

        d = ImageDraw.Draw(img)

        for pt in sensor.output:

            x, y = pt[:2]
            col = tuple( int(x) for x in pt[4:] )
            print(col)
            d.line((sensor.center[0], sensor.center[1], x, y), col)
    
        ImageShow.show(img, 'test')
    # # sensor.update_sensor()
    # # sensor.update_sensor()
    

   

if __name__ == '__main__':

    # visualize_ray_shader()

    visualize_ray_invisible_elems()

    # for n_rays in [100]:
    #     for range_rays in [1000]:
    #         for n_sensors in [100, 200, 300, 500]:

    #             analyze_speed_ray_shader(n_rays, range_rays, n_sensors)

    # env = RabbitWorld(200, 200, 10, 0, 10, 0)
    # view = View(env, (0,0), (300, 300), 1, False, id_view=True)

    # sensors = []

    # for i in range(10):
    #     sensors.append(RaySensor(view, 500, 100, fov=3*math.pi/2, spatial_res=2))

    # view.buf_update()

    # cont = True
    # x, y = 0, 0

    # t1 = time.time()

    # for i in range(1000):
    #     env.step()
    #     for sensor in sensors:
    #         sensor.update_sensor()
    #         # arr = np.frombuffer(sensor.output_pts_coord.read(), dtype=np.dtype('f')).reshape( -1, 8)
        
    #     # print(arr)
    #     # r = arr[4]
    #     # x, y = arr[0], arr[1]

    #     # if r==0: cont = False
   


    # # print(sensor.center)
    # print(1000/(time.time() - t1))
    # # view.imdisplay()
    # array = np.frombuffer(view.fbo.read(), dtype=np.dtype('B')).reshape(view.width, view.height, 3)
    # img = Image.fromarray(array, 'RGB')

    # d = ImageDraw.Draw(img)

    # for pt in arr:

    #     x, y = pt[:2]
    #     col = tuple( int(x) for x in pt[4:] )
    #     d.point((x, y), col)    
    #     d.line((sensor.center[0], sensor.center[1], x, y), col)
    # ImageShow.show(img, 'test')
    # # sensor.update_sensor()
    # # sensor.update_sensor()
    
