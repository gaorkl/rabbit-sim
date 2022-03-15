from elements import Rabbit, WereRabbit, id_to_pixel
import math
import numpy as np
import time
from PIL import Image, ImageShow, ImageDraw


from sensors.ray import DistanceSensor, RGBSensor, RaySensor, RayCompute
from env import RabbitWorld, TopDownView


def analyze_speed_ray_shader(n_rays, range_rays, n_sensors, sensor_type, sensor_scale):
    
    env = RabbitWorld((2000, 2000), n_sensors, 10, 200, 0)

    ray_shader = RayCompute(env, center=(0,0), size = (int(2000*sensor_scale), int(2000*sensor_scale)), zoom = sensor_scale)    

    rabbits = [elem for elem in env.elems if isinstance(elem, Rabbit)]
    for rab in rabbits:

        sensor = (sensor_type(rab, n_rays=n_rays, range=range_rays, fov=3*math.pi/2, spatial_resolution=2))
        ray_shader.add_sensor(sensor)

    t1 = time.time()

    for i in range(10000):
        # env.step()
        ray_shader.update_sensor()
        # arr = np.frombuffer(ray_shader.output_rays_buffer.read(), dtype=np.dtype('f'))
     
    print(n_rays, range_rays, n_sensors, sensor_scale, 10000/(time.time() - t1))

    ray_shader.ctx.gc()
    del ray_shader


def visualize_ray_shader(mode):

    env = RabbitWorld((1000, 1000), 30, 5, 30, 0)

    ray_shader = RayCompute(env, center=(0,0), size=(1000, 1000), zoom=0.5)

    view_id = ray_shader.id_view
    view_color = ray_shader.color_view

    rabbits = [elem for elem in env.elems if isinstance(elem, Rabbit)]
   
    if mode == 'color':
        sensor = RGBSensor
    elif mode == 'dist':
        sensor = DistanceSensor
    elif mode == 'id':
        sensor = DistanceSensor
    
    sensor_1 = sensor( rabbits[0], n_rays=100, range=200, fov=2*math.pi, spatial_resolution=1)
    ray_shader.add_sensor(sensor_1)
    
    sensor_2 = sensor( rabbits[1], n_rays=100, range=200, fov=2*math.pi, spatial_resolution=1)
    ray_shader.add_sensor(sensor_2)
    
    sensor_3 = sensor( rabbits[2], n_rays=100, range=200, fov=2*math.pi, spatial_resolution=1)
    ray_shader.add_sensor(sensor_3)
     
    sensor_4 = sensor( rabbits[3], n_rays=100, range=200, fov=2*math.pi, spatial_resolution=1)
    ray_shader.add_sensor(sensor_4)

    t1 = time.time()

    for i in range(100):
        env.step()

    ray_shader.update_sensor()
    array = np.frombuffer(view_color.fbo.read(), dtype=np.dtype('B')).reshape(view_color.width, view_color.height, 3)
    img = Image.fromarray(array, 'RGB')

    d = ImageDraw.Draw(img)


    for sensor in ray_shader.sensors:
        
        for ind_pt, pt in enumerate(sensor.hitpoints):

            view_x, view_y = pt[:2]
            x, y = pt[2:4]
            rel_x, rel_y = pt[4:6]
            center_x, center_y = pt[6:8]
            id_detection = int(pt[8])
            dist = 1-pt[9]/sensor.range

            # Verify that what we hit exist!
            if id_detection != 0:
                assert id_detection in env.ids.keys()
                
                if mode == 'id':
                    color = id_to_pixel(id_detection)

                elif mode == 'dist':
                    color = (int(dist*255), int(dist*255), int(dist*255))

                elif mode == 'color':
                    color = tuple(sensor.value[ind_pt].astype(np.uint8))

                d.line((center_x, center_y, view_x, view_y), color)
            

    ImageShow.show(img, 'test')

   
if __name__ == '__main__':

    visualize_ray_shader(mode='id')

    # visualize_ray_invisible_elems()

    # for n_rays in [100, 200]:
    #     for range_rays in [500, 1000]:
    #         for n_sensors in [20 , 50, 100]:
    #             for sensor_scale in [0.1, 0.5, 1]:

    #                 analyze_speed_ray_shader(n_rays, range_rays, n_sensors, RGBSensor, sensor_scale)


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
    
