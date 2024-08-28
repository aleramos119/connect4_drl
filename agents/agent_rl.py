 
#%%
import sys
from pathlib import Path # if you haven't already done so
file = Path(__file__).resolve()
parent, root = file.parent, file.parents[2]
sys.path.append(str(parent))
sys.path.append(str(root))




#%%

from helper_functions import *

#%%
from connect4_drl.config import *

#%%

#%%

# from stable_baselines3 import PPO 
# from stable_baselines3.common.torch_layers import BaseFeaturesExtractor






# import gym
# from kaggle_environments import make, evaluate
# from gym import spaces

# class ConnectFourGym(gym.Env):
#     def __init__(self, agent2="random"):
#         ks_env = make("connectx", debug=True)
#         self.env = ks_env.train([None, agent2])
#         self.rows = ks_env.configuration.rows
#         self.columns = ks_env.configuration.columns
#         # Learn about spaces here: http://gym.openai.com/docs/#spaces
#         self.action_space = spaces.Discrete(self.columns)
#         self.observation_space = spaces.Box(low=0, high=2, 
#                                             shape=(1,self.rows,self.columns), dtype=int)
#         # Tuple corresponding to the min and max possible rewards
#         self.reward_range = (-10, 1)
#         # StableBaselines throws error if these are not defined
#         self.spec = None
#         self.metadata = None
#     def reset(self):
#         self.obs = self.env.reset()
#         return np.array(self.obs['board']).reshape(1,self.rows,self.columns)
#     def change_reward(self, old_reward, done):
#         if old_reward == 1: # The agent won the game
#             return 1
#         elif done: # The opponent won the game
#             return -1
#         else: # Reward 1/42
#             return 1/(self.rows*self.columns)
#     def step(self, action):
#         # Check if agent's move is valid
#         is_valid = (self.obs['board'][int(action)] == 0)
#         if is_valid: # Play the move
#             self.obs, old_reward, done, _ = self.env.step(int(action))
#             reward = self.change_reward(old_reward, done)
#         else: # End the game and penalize agent
#             reward, done, _ = -10, True, {}
#         return np.array(self.obs['board']).reshape(1,self.rows,self.columns), reward, done, _


# #%%

# env = ConnectFourGym(agent2="random")


def agent_rl(obs, config):
    """Use a reinforcement learning agent to select the moves

    Parameters
    ----------
    obs : object 
        The observation object containing the game board information. 
    config : dict 
        A dictionary containing the configuration parameters of the game.

    
    Returns
    -------
    int
        Column selected by the agent
    """


    try:
        model = PPO.load(MODELS_DIR / "ppo")
    except Exception as e:
        print(f"Failed to load model: {e}")



     # Use the best model to select a column

    try:
        input_data = np.array(obs['board']).reshape(1, 6, 7)
        print(f"Input shape: {input_data.shape}, Input type: {input_data.dtype}")
        col, _ = model.predict(input_data)

    except Exception as e:
        print(f"Failed to load model: {e}")

    
    print(col)
    print(col)
    print(col)
    # Check if selected column is valid
    is_valid = (obs['board'][int(col)] == 0)
    # If not valid, select random move. 
    if is_valid:
        return int(col)
    else:
        return random.choice([col for col in range(config.columns) if obs.board[int(col)] == 0])
# %%
# %%

import sys


# %%
sys.path
# %%



from config import BASE_DIR
# %%
