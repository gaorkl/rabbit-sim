from elements import Rabbit, WereRabbit, id_to_pixel
import math
import numpy as np
import time
from PIL import Image, ImageShow, ImageDraw


from sensors.ray import RaySensor, RayShader, UniqueRaySensor
from env import RabbitWorld, TopDownView


def analyze_speed_rays(n_rays, range_rays, n_sensors):
    
    env = RabbitWorld((1000, 1000), 50, 10, 10, 0)
    view = TopDownView(env, (0,0), (1000, 1000), 1, False, id_view=True)

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
    
    env = RabbitWorld((1000, 1000), 50, 10, 10, 0)
    view = TopDownView(env, (0,0), (1000, 1000), 1, False, id_view=True)

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

    env = RabbitWorld((1000, 1000), 30, 5, 30, 43)
    view = TopDownView(env, (0,0), (1000, 1000), 1, False, id_view=True)
    view_disp = TopDownView(env, (0,0), (1000, 1000), 1, False, id_view=False)

    ray_shader = RayShader(view)

    wrabbits = [elem for elem in env.elems if isinstance(elem, WereRabbit)]

    ids_rabbit = [elem.id for elem in env.elems if isinstance(elem, Rabbit)]
    

    sensor_1 = RaySensor(wrabbits[0], n_rays=100, range=200, fov=2*math.pi, spatial_resolution=1)
    sensor_1.invisible_ids = ids_rabbit
    ray_shader.add_sensor(sensor_1)
    
    sensor_2 = RaySensor(wrabbits[1], n_rays=100, range=200, fov=2*math.pi, spatial_resolution=1)
    sensor_2.invisible_ids = ids_rabbit
    ray_shader.add_sensor(sensor_2)
    
    sensor_3 = RaySensor(wrabbits[2], n_rays=100, range=200, fov=2*math.pi, spatial_resolution=1)
    sensor_3.invisible_ids = ids_rabbit
    ray_shader.add_sensor(sensor_3)
     
    sensor_4 = RaySensor(wrabbits[3], n_rays=100, range=200, fov=2*math.pi, spatial_resolution=1)
    sensor_4.invisible_ids = ids_rabbit
    ray_shader.add_sensor(sensor_4)

    view.buf_update()
    view_disp.buf_update()

    t1 = time.time()

    ray_shader.update_sensor()
    array = np.frombuffer(view_disp.fbo.read(), dtype=np.dtype('B')).reshape(view.width, view.height, 3)
    img = Image.fromarray(array, 'RGB')

    d = ImageDraw.Draw(img)


    for sensor in ray_shader.sensors:
        print(sensor.center)
        for pt in sensor.output:

            x, y = pt[:2]
            id_detection = int(pt[2])
  
            # Verify that what we hit exist!
            if id_detection != 0:
                assert id_detection in env.ids.keys()
                d.line((sensor.center[0], sensor.center[1], x, y), id_to_pixel(id_detection))
            else:

                d.line((sensor.center[0], sensor.center[1], x, y), (124, 124, 124, 123))

    ImageShow.show(img, 'test')
    # # sensor.update_sensor()
    # # sensor.update_sensor()
 
def visualize_ray_invisible_elems():

    env = RabbitWorld((1000, 1000), 50, 10, 10, 0)
    view = TopDownView(env, (0,0), (1000, 1000), 1, False, id_view=True)
    view_disp = TopDownView(env, (0,0), (1000, 1000), 1, False, id_view=False)

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

    ray_shader.update_sensor()
    array = np.frombuffer(view_disp.fbo.read(), dtype=np.dtype('B')).reshape(view.width, view.height, 3)
    img = Image.fromarray(array, 'RGB')

    d = ImageDraw.Draw(img)


    for sensor in ray_shader.sensors:
        for pt in sensor.output:

            x, y = pt[:2]
            id_detection = int(pt[2])
            d.line((sensor.center[0], sensor.center[1], x, y), id_to_pixel(id_detection))
  
            # Verify that what we hit exist!
            if id_detection != 0:
                assert id_detection in env.ids.keys()

    ImageShow.show(img, 'test')
    #
   
if __name__ == '__main__':

    visualize_ray_shader()

    # visualize_ray_invisible_elems()

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
    
