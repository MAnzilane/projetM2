from gym.envs.registration import register

register(
            id='Grid-World-v0',
            entry_point='grid_world.envs:GridWorld',
        )