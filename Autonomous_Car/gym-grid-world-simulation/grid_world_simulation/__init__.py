from gym.envs.registration import register

register(
            id='Grid-World-Simulation-v0',
            entry_point='grid_world_simulation.envs:GridWorld',
        )