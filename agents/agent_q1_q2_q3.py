#%%
from .helper_functions import *

# %%

def agent_q1(obs, config):
    """Selects a winning move if exists, otherwise selects  random

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
    

    valid_moves = [col for col in range(config.columns) if obs.board[col] == 0]

    winning_moves = [col for col in valid_moves if check_winning_move(obs, config, col, piece=obs.mark)]

    
    if not winning_moves:
        return random.choice(valid_moves)
    
    else:
        return random.choice(winning_moves)
        
    
    

def agent_q2(obs, config):
    """Selects a winning move if available, 
    otherwise selects the winning move of the opponent,
    otherwise selects random

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
    valid_moves = [col for col in range(config.columns) if obs.board[col] == 0]
    
    winning_moves = [col for col in valid_moves if check_winning_move(obs, config, col, piece=obs.mark)]
    
    opponet_mark = 1 if obs.mark == 2 else 2
    
    winning_moves_opp = [col for col in valid_moves if check_winning_move(obs, config, col, piece=opponet_mark)]
    
    
    if winning_moves:
        return random.choice(winning_moves)
    
    elif winning_moves_opp:
        return random.choice(winning_moves_opp)
        
    else:
        return random.choice(valid_moves) 
    


def agent_q3(obs, config):
    """Selects a winning move if available, 
    otherwise selects the winning move of the opponent,
    otherwise selects random

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

    valid_moves = [col for col in range(config.columns) if obs.board[col] == 0]
    
    winning_moves = [col for col in valid_moves if check_winning_move(obs, config, col, piece=obs.mark)]
    
    opponet_mark = 1 if obs.mark == 2 else 2
    
    winning_moves_opp = [col for col in valid_moves if check_winning_move(obs, config, col, piece=opponet_mark)]
    
    no_play_moves=[]
    
    class tempclass:
        def __init__(self, board):
            self.board = board

    
    for move in valid_moves:
        grid = np.asarray(obs.board).reshape(config.rows, config.columns)
        next_grid = drop_piece(grid, move, obs.mark, config)
        next_board=next_grid.flatten()
        next_obs=tempclass(next_board)
        if check_winning_move(next_obs, config, move, piece=opponet_mark):
            no_play_moves.append(move)
            
        
    
    not_lossing_moves=[move for move in valid_moves if move not in no_play_moves]
    
    
    if winning_moves:
        return random.choice(winning_moves)
    
    elif winning_moves_opp:
        return random.choice(winning_moves_opp)
    
    elif not_lossing_moves:
        return random.choice(not_lossing_moves)
    else:
        return random.choice(valid_moves)
# %%





