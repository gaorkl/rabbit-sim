from abc import ABC, abstractmethod
import math
import random
import numpy as np
from array import array


class UniqueRaySensor:

    def __init__(self, view, n_rays, range, fov, spatial_res):

        self.view = view
        self.range = range
        self.n_rays = n_rays

        self.ctx = self.view.ctx
        
        self.output_pts_coord = self.ctx.buffer(data = array('f', self.gen_data(n_rays)))
        
        self.ray_shader = self.ctx.compute_shader(source=
            """
            # version 430
            
            layout(local_size_x=256, local_size_y=1) in;
            
            struct HitPoint
            {
                vec4 pos;
                vec4 color;
            };

            uniform sampler2D texture_view; 

            uniform vec2 center;
            uniform float angle;
            uniform float range;
            uniform int n_rays;
            uniform float fov;
            uniform float spatial_res;

            float n_points = int(range/spatial_res);

            layout(std430, binding=0) buffer hit_points
            {
                HitPoint hpts[];
            } Out;

            float pi = 3.14;

            void main() {


                int i_ray = int(gl_LocalInvocationID);

                vec2 end_pos = vec2(
                        center.x + range*cos(angle -fov/2 + i_ray*fov/n_rays),
                        center.y + range*sin(angle -fov/2 + i_ray*fov/n_rays));

                ivec2 sample_point = ivec2(0,0);

                // Ray cast
                for(float i=0; i<n_points; i++)
                {
                    float ratio = i/n_points;
                    sample_point = ivec2(mix(center, end_pos, ratio));
                    vec4 color_pt = texelFetch(texture_view, sample_point, 0);

                    if (color_pt != vec4(0,0,0,0)) break;

                }

                // HitPoint hpt = Out.hpts[i_ray];
               
                // Get Pixel value
                // ivec2 pos = ivec2(hpt.pos.xy);
                // vec4 color_pt = texelFetch(texture_view, pos, 0);
                
                vec4 color_pt = vec4(255, 255*float(i_ray)/n_rays, 255*float(i_ray)/n_rays, 0);

                // update_pos
                // pos.x +=1 ;
                // pos.y += 1;

                HitPoint out_pt;
                out_pt.pos = vec4(sample_point, 0, 0);
                out_pt.color = color_pt;

                Out.hpts[i_ray] = out_pt;
                
            }
            """
        )

        self.ray_shader["range"] = range
        self.ray_shader["n_rays"] = n_rays
        self.ray_shader["fov"] = fov
        self.ray_shader["spatial_res"] = spatial_res
        self.center = 0, 0

    def gen_data(self, n_rays):

        for i in range(n_rays):

            # position
            # 
            yield 0.
            yield 0.
            yield 0.
            yield 0.

            # color
            yield 0.
            yield 0.
            yield 0.
            yield 0.



    def update_sensor(self):
        
        self.output_pts_coord.bind_to_storage_buffer(binding=0)
        self.view.texture.use()

        self.center = random.uniform(0, self.view.width), random.uniform(0, self.view.height)
        self.ray_shader["center"] = self.center
        self.ray_shader["angle"] = random.uniform(0, 2*math.pi)
        self.ray_shader.run()

        # arr = np.frombuffer(self.output_pts_coord.read(), dtype=np.dtype('f'))
        # print(arr.reshape(self.n_rays, -1))


class RaySensor:

    def __init__(self, anchor, n_rays, range, fov, spatial_resolution):

        self.range = range
        self.n_rays = n_rays
        self.fov = fov
        self.spatial_resolution = spatial_resolution
        self.n_points = int(self.range / self.spatial_resolution)

        self.anchor = anchor

        self.value = 0
        self.hitpoints = 0

        self.invisible_ids = []

    @property
    def center(self):
        return self.anchor.body.position

    @property
    def angle(self):
        return self.anchor.body.angle

    def update_value(self, hitpoints):
        self.hitpoints = hitpoints


class DistanceSensor(RaySensor):

    def update_value(self, hitpoints):

        super().update_value(hitpoints)
        self.value = hitpoints[:, 9]


class RGBSensor(RaySensor):

    def update_value(self, hitpoints):

        super().update_value(hitpoints)

        colors = []

        ids = hitpoints[:, 4]
        rel_pos = hitpoints[2:4]

        for htp in hitpoints:

            pos = htp[2:4]
            elem_id = int(htp[8])
           
            if elem_id == 0:
                color = (0,0,0)

            else:
                elem = self.anchor.env.ids[elem_id]
                color = elem.get_pixel_from_point(pos)

            colors.append(color)

        self.value = np.array(colors)


class RayShader:

    def __init__(self, view):

        self.sensors = []
        self.view = view
        
        self.ctx = self.view.ctx

        self.view_params_buffer = self.ctx.buffer(data = array('f', 
                                                               [view.center[0],
                                                                view.center[1],
                                                                view.width,
                                                                view.height,
                                                                view.zoom
                                                                ]))
        self.source = """
            # version 440
            
            layout(local_size_x=MAX_N_RAYS) in;
            
            struct HitPoint
            {
                // Position of hitpoint on view
                float view_pos_x;
                float view_pos_y;
                
                // Position of hitpoint in env
                float env_pos_x;
                float env_pos_y;

                // Position of hitpoint relative to sensor
                float rel_pos_x;
                float rel_pos_y;

                // Position of sensor on view
                float sensor_x_on_view;
                float sensor_y_on_view;

                float id;
                float dist;
            };

            struct SensorParam
            {
                float range;
                float fov;
                float n_rays;
                float n_points;
            };

            struct Coordinate
            {
                float pos_x;
                float pos_y;
                float angle;
            };

            uniform sampler2D id_texture; 
            
            layout(std430, binding = 2) buffer sparams
            {
                SensorParam sensor_params[N_SENSORS];
            } Params;

            layout(std430, binding = 0) buffer coordinates
            { 
                Coordinate coords[N_SENSORS];
            } In;

            layout(std430, binding = 1) buffer hit_points
            {
                HitPoint hpts[];
            } Out;

            layout(std430, binding=3) buffer invisible_ids
            {
                int inv_ids[N_SENSORS][MAX_N_INVISIBLE];
            }InvIDs;

            layout(std430, binding=4) buffer view_params
            {
                float center_view_x;
                float center_view_y;
                float w;
                float h;
                float zoom;

            }ViewParams;

            float pi = 3.14;

            void main() {

                int i_ray = int(gl_LocalInvocationIndex);
                int i_sensor = int(gl_WorkGroupID);

                // SENSOR PARAMETERS
                SensorParam s_param = Params.sensor_params[i_sensor];
                float range = s_param.range;
                float fov = s_param.fov;
                float n_rays = s_param.n_rays;
                float n_points = s_param.n_points;

                // VIEW PARAMETERS
                float center_view_x = ViewParams.center_view_x; 
                float center_view_y = ViewParams.center_view_y; 
                float zoom = ViewParams.zoom;
                float view_w = ViewParams.w;
                float view_h = ViewParams.h;

                // SENSOR POSITION
                Coordinate in_coord = In.coords[i_sensor];
                float sensor_pos_x = in_coord.pos_x;
                float sensor_pos_y = in_coord.pos_y;
                
                float sensor_x_on_view = (sensor_pos_x - center_view_x)*zoom + view_w/2;
                float sensor_y_on_view = (sensor_pos_y - center_view_y)*zoom + view_h/2;

                float angle = in_coord.angle;

                // INVISIBLE POINTS
                int inv_pts[MAX_N_INVISIBLE] = InvIDs.inv_ids[i_sensor];

                // CENTER AND END OF RAY
                vec2 center = vec2(sensor_x_on_view, sensor_y_on_view);
                vec2 end_pos = vec2(
                        sensor_x_on_view + range*cos(angle -fov/2 + i_ray*fov/n_rays)*zoom,
                        sensor_y_on_view + range*sin(angle -fov/2 + i_ray*fov/n_rays)*zoom);

                // OUTPUTS
                ivec2 sample_point = ivec2(0,0);
                vec4 color_out = vec4(0,0,0,0);
                int id_out = 0;

                // Ray cast
                for(float i=0; i<n_points; i++)
                {
                    float ratio = i/n_points;
                    sample_point = ivec2(mix(center, end_pos, ratio));
                    color_out = texelFetch(id_texture, sample_point, 0);

                    id_out = int(256*256*color_out.z*255 + 256*color_out.y*255 + color_out.x*255);
                    
                    if (id_out != 0)
                    {
                        bool invisible = false;

                        for(int ind_inv=0; ind_inv<MAX_N_INVISIBLE; ind_inv++)
                        {
                            if (inv_pts[ind_inv] == id_out)
                            {
                                invisible = true;
                                id_out = 0;
                                break;
                            }

                        }

                        if (!invisible) break;
    
                    }

                }
                
                float dx = sample_point.x - sensor_x_on_view;
                float dy = sample_point.y - sensor_y_on_view;
                float dist = sqrt( (dx*dx) + (dy*dy) )/zoom;

                // CONVERT IN THE FRAME OF THE ENVIRONMENT

                HitPoint out_pt;
                
                out_pt.view_pos_x = sample_point.x;
                out_pt.view_pos_y = sample_point.y;

                out_pt.env_pos_x = (sample_point.x - view_w/2)/zoom + center_view_x ;
                out_pt.env_pos_y = (sample_point.y - view_h/2)/zoom + center_view_y ;
                
                //float rel_pos_x = (sample_point.x - center_x)*cos(angle) - (sample_point.y - center_y)*sin(angle);
                //out_pt.env_rel_pos_x = rel_pos_x/zoom;

                //float rel_pos_y = (sample_point.y - center_y)*cos(angle) + (sample_point.x - center_x)*sin(angle);
                //out_pt.env_rel_pos_y = rel_pos_y/zoom;

                out_pt.sensor_x_on_view = sensor_x_on_view ;
                out_pt.sensor_y_on_view = sensor_y_on_view ;

                out_pt.id = float(id_out);               
                out_pt.dist = dist/zoom;

                Out.hpts[i_ray + i_sensor*MAX_N_RAYS] = out_pt;
                
            }
            """

    @property
    def n_sensors(self):
        return len(self.sensors)

    @property
    def max_n_rays(self):
        return max( sensor.n_rays for sensor in self.sensors )

    @property
    def max_invisible(self):
        return 1 + max( len(sensor.invisible_ids) for sensor in self.sensors )

    def generate_parameter_buffer(self):

        for sensor in self.sensors:
            yield sensor.range
            yield sensor.fov
            yield sensor.n_rays
            yield sensor.n_points

    def generate_position_buffer(self):

        for sensor in self.sensors:
            yield sensor.center[0]
            yield sensor.center[1]
            yield sensor.angle

    def generate_output_buffer(self):

        for _ in range(self.n_sensors):
            for _ in range(self.max_n_rays):

                    # View Position
                    yield 0.
                    yield 0.

                    # Abs Env Position
                    yield 0.
                    yield 0.

                    # Rel Position
                    yield 0.
                    yield 0.

                    # Sensor center on view
                    yield 0.
                    yield 0.

                    # ID
                    yield 0.

                    # Distance
                    yield 0.

    def generate_invisible_buffer(self):

        for sensor in self.sensors:

            count = 1
            yield sensor.anchor.id
            
            for inv in sensor.invisible_ids:
                yield inv
                count += 1

            while count < self.max_invisible-1:
                yield 0
                count += 1



    def add_sensor(self, sensor):
        self.sensors.append(sensor)
        
        self.position_buffer = self.ctx.buffer(data = array('f', self.generate_position_buffer()))
        self.param_buffer = self.ctx.buffer(data = array('f', self.generate_parameter_buffer()))
        self.output_rays_buffer = self.ctx.buffer(data = array('f', self.generate_output_buffer()))
        self.inv_buffer = self.ctx.buffer(data = array('I', self.generate_invisible_buffer()))
        new_source = self.source
        new_source = new_source.replace('N_SENSORS', str(len(self.sensors)))
        new_source = new_source.replace('MAX_N_RAYS', str(self.max_n_rays))
        new_source = new_source.replace('MAX_N_INVISIBLE', str(self.max_invisible))
        self.ray_shader = self.ctx.compute_shader(source = new_source)

        self.output_rays_buffer.bind_to_storage_buffer(binding=1)
        self.param_buffer.bind_to_storage_buffer(binding=2)
        self.inv_buffer.bind_to_storage_buffer(binding=3)
        self.view_params_buffer.bind_to_storage_buffer(binding=4)


    def update_sensor(self):
        
        if self.sensors:
            self.position_buffer = self.ctx.buffer(data = array('f', self.generate_position_buffer()))
            self.position_buffer.bind_to_storage_buffer(binding=0)
            self.view.texture.use()

            self.ray_shader.run(group_x = self.n_sensors)

            hitpoints = np.frombuffer(self.output_rays_buffer.read(),
                                      dtype=np.float32).reshape( self.n_sensors, self.max_n_rays, 10)

            for index, sensor in enumerate(self.sensors):
                sensor.update_value(hitpoints[index, :sensor.n_rays, :])


# class RayShader:

#     def __init__(self, view):

#         self.sensors = []
#         self.view = view
        
#         self.ctx = self.view.ctx

#         self.source = """
#             # version 440
            
#             layout(local_size_x=MAX_N_RAYS) in;
            
#             struct HitPoint
#             {
#                 vec3 pos;
#                 vec4 color;
#             };

#             struct SensorParam
#             {
#                 float range;
#                 float fov;
#                 float n_rays;
#                 float n_points;
#             };

#             struct Coordinate
#             {
#                 float pos_x;
#                 float pos_y;
#                 float angle;
#             };

#             uniform sampler2D texture_view; 
            
#             layout(std430, binding = 2) buffer sparams
#             {
#                 SensorParam sensor_params[N_SENSORS];
#             } Params;

#             layout(std430, binding = 0) buffer coordinates
#             { 
#                 Coordinate coords[N_SENSORS];
#             } In;

#             layout(std430, binding = 1) buffer hit_points
#             {
#                 HitPoint hpts[];
#             } Out;

#             layout(std430, binding=3) buffer invisible_elems
#             {
#                 uint number_inv_elems_per_sensor[N_SENSORS];
#                 uint start_inv_elems[N_SENSORS];
#                 uvec4 invisible_elems[];
#             } Invis;

#             float pi = 3.14;

#             void main() {

                
#                 int i_ray = int(gl_LocalInvocationIndex);
#                 int i_sensor = int(gl_WorkGroupID);

#                 Coordinate in_coord = In.coords[i_sensor];

#                 float center_x = in_coord.pos_x;
#                 float center_y = in_coord.pos_y;
#                 float angle = in_coord.angle;
                   
#                 SensorParam s_param = Params.sensor_params[i_sensor];

#                 uint n_invisible_elems = Invis.number_inv_elems_per_sensor[i_sensor];
#                 uint start_inv_elem = Invis.start_inv_elems[i_sensor];

#                 float range = s_param.range;
#                 float fov = s_param.fov;
#                 float n_rays = s_param.n_rays;
#                 float n_points = s_param.n_points;

#                 vec2 center = vec2(center_x, center_y);
#                 vec2 end_pos = vec2(
#                         center_x + range*cos(angle -fov/2 + i_ray*fov/n_rays),
#                         center_y + range*sin(angle -fov/2 + i_ray*fov/n_rays));

#                 ivec2 sample_point = ivec2(0,0);
               
#                 vec4 color_out = vec4(0,0,0, 0);
                
#                 // Ray cast
#                 for(float i=0; i<n_points; i++)
#                 {
#                     float ratio = i/n_points;
#                     sample_point = ivec2(mix(center, end_pos, ratio));
#                     vec4 color_pt = texelFetch(texture_view, sample_point, 0);

#                     if (color_pt != vec4(0,0,0,0))
#                     {
#                         bool invisible = false;

#                         for(uint inv_id=0; i<n_invisible_elems; i++)
#                         {
#                             uint ind_inv_elem = start_inv_elem + inv_id;
#                             if (uvec4(color_pt*255) == Invis.invisible_elems[ind_inv_elem])
#                             {
#                                 invisible = true;
#                                 break;
#                             }

#                             if (invisible) break;
#                         }

#                         if (!invisible) 
#                         {
#                             color_out = color_pt;
#                             break;
#                         }

#                     }
#                 }

#                 vec4 color_pt = vec4(255, 255*float(i_ray)/n_rays, 255*float(i_ray)/n_rays, 0);
                
#                 HitPoint out_pt;
#                 out_pt.pos = vec3(sample_point, 0);
#                 // out_pt.pos = vec4(i_sensor, i_ray, 0, 0);
#                 out_pt.color = color_out*255;

#                 Out.hpts[i_ray + i_sensor*MAX_N_RAYS] = out_pt;
                
#             }
#             """


#     @property
#     def n_sensors(self):
#         return len(self.sensors)

#     @property
#     def max_n_rays(self):
#         return max( sensor.n_rays for sensor in self.sensors )

#     def generate_parameter_buffer(self):

#         for sensor in self.sensors:
#             yield sensor.range
#             yield sensor.fov
#             yield sensor.n_rays
#             yield sensor.n_points

#     def generate_position_buffer(self):

#         for sensor in self.sensors:
#             yield sensor.center[0]
#             yield sensor.center[1]
#             yield sensor.angle

#     def generate_output_buffer(self):

#         for _ in range(self.n_sensors):
#             for _ in range(self.max_n_rays):

#                     # Position
#                     yield 0.
#                     yield 0.
#                     yield 0.
#                     yield 0.

#                     # ID
#                     yield 0.
#                     yield 0.
#                     yield 0.
#                     yield 0.

#     def generate_invisible_buffer(self):

#         index_inv = 0

#         for n_sens in range(self.n_sensors):    
#             n_inv = len(self.sensors[n_sens].invisible_ids)
#             yield n_inv

#         for n_sens in range(self.n_sensors):    
#             n_inv = len(self.sensors[n_sens].invisible_ids)
#             yield index_inv
#             index_inv += n_inv

#         for sensor in self.sensors:

#             for inv in sensor.invisible_ids:

#                 id_0 =  inv & 255
#                 id_1 = (inv >> 8) & 255
#                 id_2 = (inv >> 16) & 255


#                 yield id_0
#                 yield id_1
#                 yield id_2
#                 yield 255

#     def add_sensor(self, sensor):
#         self.sensors.append(sensor)
        
#         self.position_buffer = self.ctx.buffer(data = array('f', self.generate_position_buffer()))
#         self.param_buffer = self.ctx.buffer(data = array('f', self.generate_parameter_buffer()))
#         self.output_rays_buffer = self.ctx.buffer(data = array('f', self.generate_output_buffer()))
#         self.inv_buffer = self.ctx.buffer(data = array('I', self.generate_invisible_buffer()))
     
#         print(array('I', self.generate_invisible_buffer()))
#         print(np.frombuffer(self.inv_buffer.read(), np.uint32 ))
       
#         # for elem in self.generate_invisible_buffer(): print(elem)
#         new_source = self.source
#         new_source = new_source.replace('N_SENSORS', str(len(self.sensors)))
#         new_source = new_source.replace('MAX_N_RAYS', str(self.max_n_rays))
#         self.ray_shader = self.ctx.compute_shader(source = new_source)

#         # self.ray_shader['sensor_params'] = self.param_buffer

#     def update_sensor(self):
        
#         if self.sensors:
#             self.position_buffer = self.ctx.buffer(data = array('f', self.generate_position_buffer()))
#             self.position_buffer.bind_to_storage_buffer(binding=0)
#             self.output_rays_buffer.bind_to_storage_buffer(binding=1)
#             self.param_buffer.bind_to_storage_buffer(binding=2)
#             self.inv_buffer.bind_to_storage_buffer(binding=3)
#             self.view.texture.use()

#             self.ray_shader.run(group_x = self.n_sensors)

            
#             arr = np.frombuffer(self.output_rays_buffer.read(), dtype=np.dtype('f')).reshape( self.n_sensors, self.max_n_rays, 8)
#             for index, sensor in enumerate(self.sensors):
 
