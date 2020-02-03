from gym.envs.registration import register

register(
            id='Grid-World-Car-v0',
            entry_point='grid_world_car.envs:GridWorld',
        )