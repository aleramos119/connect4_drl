#%%
import agents as ag
from importlib import reload
reload(ag)

# %%

ag.get_win_percentages(agent1=ag.agent_q3, agent2=ag.agent_minimax)

# %%
