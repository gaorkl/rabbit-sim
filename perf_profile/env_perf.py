import os, sys
sys.path.append('..')


from env import RabbitWorld
import time
from topdown import TopDownView


def analyze_speed_env_update(size_envir, n_rabbits, n_carrots):
    
    env = RabbitWorld(size_envir, n_rabbits=n_rabbits, n_carrots=n_carrots, n_wrabbits=0, seed=0)

    t1 = time.time()

    for _ in range(10000):
        env.step()
     
    print('envir_fps:', size_envir, n_rabbits, n_carrots, 10000/(time.time() - t1))



def analyze_speed_view_update(size_envir, n_rabbits, n_carrots):
    
    env = RabbitWorld(size_envir, n_rabbits=n_rabbits, n_carrots=n_carrots, n_wrabbits=0, seed=0)
    view = TopDownView(env, (0,0), size_envir, zoom=1)

    t1 = time.time()

    for _ in range(10000):
        env.step()
        view.buf_update()
     
    print('enviri_and_view_fps:', size_envir, n_rabbits, n_carrots, 10000/(time.time() - t1))




if __name__ == '__main__':
   
    print(" Depends on environment size_envir ")

    # for env_size in [500, 1000, 2000, 5000, 10000]:
        # analyze_speed_env_update((env_size, env_size), 100, 100)
        # analyze_speed_view_update((env_size, env_size), 100, 100)

    # Depends on environment size_envir

    print(" Depends on number moving elems ")
    
    for n_rabbits in [0, 100, 500, 1000]:
        # analyze_speed_env_update((2000, 2000), n_rabbits, 100)
        analyze_speed_view_update((2000, 2000), n_rabbits, 100)



        # for n_rabbits in [0, 10, 50, 100, 500]:
        #     for n_carrots in [0, 100, 500, 1000]:
