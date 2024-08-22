 
#%%
from .helper_functions import *

def agent_minimax(obs, config):
    """Selects move using minimax algorithm

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
    N_STEPS = 3

    # Get list of valid moves
    valid_moves = [c for c in range(config.columns) if obs.board[c] == 0]
    # Convert the board to a 2D grid
    grid = np.asarray(obs.board).reshape(config.rows, config.columns)
    # Use the heuristic to assign a score to each possible board in the next step
    scores = dict(zip(valid_moves, [score_move(grid, col, obs.mark, config, N_STEPS) for col in valid_moves]))
    # Get a list of columns (moves) that maximize the heuristic
    max_cols = [key for key in scores.keys() if scores[key] == max(scores.values())]
    # Select at random from the maximizing columns
    return random.choice(max_cols)
# %%
