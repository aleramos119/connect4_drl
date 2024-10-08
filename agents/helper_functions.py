#%%
import numpy as np
import random

from kaggle_environments import make, evaluate, agent
from stable_baselines3 import PPO 
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor




def get_win_percentages(agent1, agent2, n_rounds=100):
    """Gets the winning percentages of two agents playing together

    Parameters
    ----------
    agent1 : object 
        Agent number 1
    agent2 : object 
        Agent number 2
    n_rounds : int, optional
        Number of rounds, by default 100
    """
    # Use default Connect Four setup
    config = {'rows': 6, 'columns': 7, 'inarow': 4}
    # Agent 1 goes first (roughly) half the time          
    outcomes = evaluate("connectx", [agent1, agent2], config, [], n_rounds//2)
    # Agent 2 goes first (roughly) half the time      
    outcomes += [[b,a] for [a,b] in evaluate("connectx", [agent2, agent1], config, [], n_rounds-n_rounds//2)]
    print("Agent 1 Win Percentage:", np.round(outcomes.count([1,-1])/len(outcomes), 2))
    print("Agent 2 Win Percentage:", np.round(outcomes.count([-1,1])/len(outcomes), 2))
    print("Number of draws:", np.round(outcomes.count([0,0])/len(outcomes), 2))
    print("Number of Invalid Plays by Agent 1:", outcomes.count([None, 0]))
    print("Number of Invalid Plays by Agent 2:", outcomes.count([0, None]))





def drop_piece(grid, col, piece, config):
    '''Gets board at next step if agent drops piece in selected column

    Parameters: 
    ----------- 
    grid : numpy array 
        The current game grid. 
        
    col : int 
        The column where the piece will be dropped. 
        
    piece : int 
        The value of the piece to be dropped. 
        
    config : dict 
        A dictionary containing the configuration parameters of the game. 
        
    Returns: 
    -------- 
    next_grid : numpy array 
        The updated game grid after dropping the piece in the specified column. 
    '''  
    next_grid = grid.copy()
    for row in range(config.rows-1, -1, -1):
        if next_grid[row][col] == 0:
            break
    next_grid[row][col] = piece
    return next_grid





def check_winning_move(obs, config, col, piece):
    '''Returns True if dropping piece in column results in game win 


    Parameters: 
    ----------- 
    obs : object 
        The observation object containing the game board information. 
    
    config : dict 
        A dictionary containing the configuration parameters of the game. 
    
    col : int 
        The column where the piece is to be placed. 
    
    piece : int 
        The value of the piece to be checked for winning move. 
    
    Returns: 
    -------- 
    bool 
        True if the move results in a winning move, False otherwise. 
    '''
    # Convert the board to a 2D grid
    grid = np.asarray(obs.board).reshape(config.rows, config.columns)
    next_grid = drop_piece(grid, col, piece, config)
    # horizontal
    for row in range(config.rows):
        for col in range(config.columns-(config.inarow-1)):
            window = list(next_grid[row,col:col+config.inarow])
            if window.count(piece) == config.inarow:
                return True
    # vertical
    for row in range(config.rows-(config.inarow-1)):
        for col in range(config.columns):
            window = list(next_grid[row:row+config.inarow,col])
            if window.count(piece) == config.inarow:
                return True
    # positive diagonal
    for row in range(config.rows-(config.inarow-1)):
        for col in range(config.columns-(config.inarow-1)):
            window = list(next_grid[range(row, row+config.inarow), range(col, col+config.inarow)])
            if window.count(piece) == config.inarow:
                return True
    # negative diagonal
    for row in range(config.inarow-1, config.rows):
        for col in range(config.columns-(config.inarow-1)):
            window = list(next_grid[range(row, row-config.inarow, -1), range(col, col+config.inarow)])
            if window.count(piece) == config.inarow:
                return True
    return False



###########################################################
### Helper functions of heuristic agnets
###########################################################
#%%
def score_move(grid, col, mark, config):
    ''' Calculates score if agent drops piece in selected column

    Parameters: 
    ----------- 
    grid : numpy array 
        The current game grid. 
    
    col : int 
        The column where the piece will be dropped. 
    
    mark : int 
        The value of the piece to be dropped. 
    
    config : dict 
        A dictionary containing the configuration parameters of the game. 
    
    Returns: 
    -------- 
    score : int 
        The score of the move based on the heuristic evaluation. 
    '''
    next_grid = drop_piece(grid, col, mark, config)
    score = get_heuristic(next_grid, mark, config)
    return score

#
def drop_piece(grid, col, mark, config):
    ''' Helper function for score_move: gets board at next step if agent drops piece in selected column
    Parameters: 
    ----------- 
    grid : numpy array 
        The current game grid. 
    
    col : int 
        The column where the piece will be dropped. 
    
    mark : int 
        The value of the piece to be dropped. 
    
    config : dict 
        A dictionary containing the configuration parameters of the game. 
    
    Returns: 
    -------- 
    next_grid : numpy array 
        The updated game grid after dropping the piece in the specified column. 
    '''
    next_grid = grid.copy()
    for row in range(config.rows-1, -1, -1):
        if next_grid[row][col] == 0:
            break
    next_grid[row][col] = mark
    return next_grid


def get_heuristic(grid, mark, config):
    ''' Helper function for score_move: calculates value of heuristic for grid
    Parameters: 
    ----------- 
    grid : numpy array 
        The current game grid. 
    
    mark : int 
        The value of the piece to be evaluated. 
    
    config : dict 
        A dictionary containing the configuration parameters of the game. 
    
    Returns: 
    -------- 
    score : int 
        The heuristic score calculated based on the game grid and piece value. 
    '''
    num_threes = count_windows(grid, 3, mark, config)
    num_fours = count_windows(grid, 4, mark, config)
    num_threes_opp = count_windows(grid, 3, mark%2+1, config)
    score = num_threes - 1e2*num_threes_opp + 1e6*num_fours
    return score

# 
def check_window(window, num_discs, piece, config):
    ''' Helper function for get_heuristic: checks if window satisfies heuristic conditions
    Parameters: 
    ----------- 
    window : list 
        The window of pieces to be checked. 
    
    num_discs : int 
        The number of discs to be checked for. 
    
    piece : int 
        The value of the piece to be checked. 
    
    config : dict 
        A dictionary containing the configuration parameters of the game. 
    
    Returns: 
    -------- 
    bool 
        True if the window contains the specified number of pieces and empty slots as per the configuration, False otherwise. 
    '''
    return (window.count(piece) == num_discs and window.count(0) == config.inarow-num_discs)
    
# 
def count_windows(grid, num_discs, piece, config):
    ''' Helper function for get_heuristic: counts number of windows satisfying specified heuristic conditions
    Parameters: 
    ----------- 
    grid : numpy array 
        The current game grid. 
    
    num_discs : int 
        The number of discs to be checked for in a window. 
    
    piece : int 
        The value of the piece to be checked. 
    
    config : dict 
        A dictionary containing the configuration parameters of the game. 
    
    Returns: 
    -------- 
    num_windows : int 
        The number of windows satisfying the specified heuristic conditions in the game grid. 
    '''

    num_windows = 0
    # horizontal
    for row in range(config.rows):
        for col in range(config.columns-(config.inarow-1)):
            window = list(grid[row, col:col+config.inarow])
            if check_window(window, num_discs, piece, config):
                num_windows += 1
    # vertical
    for row in range(config.rows-(config.inarow-1)):
        for col in range(config.columns):
            window = list(grid[row:row+config.inarow, col])
            if check_window(window, num_discs, piece, config):
                num_windows += 1
    # positive diagonal
    for row in range(config.rows-(config.inarow-1)):
        for col in range(config.columns-(config.inarow-1)):
            window = list(grid[range(row, row+config.inarow), range(col, col+config.inarow)])
            if check_window(window, num_discs, piece, config):
                num_windows += 1
    # negative diagonal
    for row in range(config.inarow-1, config.rows):
        for col in range(config.columns-(config.inarow-1)):
            window = list(grid[range(row, row-config.inarow, -1), range(col, col+config.inarow)])
            if check_window(window, num_discs, piece, config):
                num_windows += 1
    return num_windows








# %%


###########################################################
### Helper functions of minimax agnets
###########################################################

def get_heuristic_minimax(grid, mark, config):
    ''' Helper function for score_move: calculates value of heuristic for grid
    Parameters: 
    ----------- 
    grid : numpy array 
        The current game grid. 
    
    mark : int 
        The value of the piece to be evaluated. 
    
    config : dict 
        A dictionary containing the configuration parameters of the game. 
    
    Returns: 
    -------- 
    score : int 
        The heuristic score calculated based on the game grid and piece value. 
    '''
    num_threes = count_windows(grid, 3, mark, config)
    num_fours = count_windows(grid, 4, mark, config)
    num_threes_opp = count_windows(grid, 3, mark%2+1, config)
    num_fours_opp = count_windows(grid, 4, mark%2+1, config)
    score = num_threes - 1e2*num_threes_opp - 1e4*num_fours_opp + 1e6*num_fours
    return score


def score_move(grid, col, mark, config, nsteps):
    ''' Uses minimax to calculate value of dropping piece in selected column

    Parameters: 
    ----------- 
    grid : numpy array 
        The current game grid. 
    
    col : int 
        The column where the piece will be dropped. 
    
    mark : int 
        The value of the piece to be dropped. 
    
    config : dict 
        A dictionary containing the configuration parameters of the game. 
    
    nsteps : int 
        The number of steps to look ahead in the minimax algorithm. 
    
    Returns: 
    -------- 
    score : int 
        The score of the move calculated using the minimax algorithm. 
    '''
    next_grid = drop_piece(grid, col, mark, config)
    score = minimax(next_grid, nsteps-1, False, mark, config)
    return score

# Helper function for minimax: checks if agent or opponent has four in a row in the window
def is_terminal_window(window, config):
    ''' Helper function for minimax: checks if agent or opponent has four in a row in the window

    Parameters: 
    ----------- 
    window : list 
        The window of pieces to be checked. 
    
    config : dict 
        A dictionary containing the configuration parameters of the game. 
    
    Returns: 
    -------- 
    bool 
        True if the window contains a winning sequence for either player 1 or player 2, False otherwise. 
    '''
    return window.count(1) == config.inarow or window.count(2) == config.inarow



# Helper function for minimax: checks if game has ended
def is_terminal_node(grid, config):
    ''' Helper function for minimax: checks if game has ended

    Parameters: 
    ----------- 
    grid : numpy array 
        The current game grid. 
    
    config : dict 
        A dictionary containing the configuration parameters of the game. 
    
    Returns: 
    -------- 
    bool 
        True if the current node is a terminal node (win or draw), False otherwise. 
    '''
    # Check for draw 
    if list(grid[0, :]).count(0) == 0:
        return True
    # Check for win: horizontal, vertical, or diagonal
    # horizontal 
    for row in range(config.rows):
        for col in range(config.columns-(config.inarow-1)):
            window = list(grid[row, col:col+config.inarow])
            if is_terminal_window(window, config):
                return True
    # vertical
    for row in range(config.rows-(config.inarow-1)):
        for col in range(config.columns):
            window = list(grid[row:row+config.inarow, col])
            if is_terminal_window(window, config):
                return True
    # positive diagonal
    for row in range(config.rows-(config.inarow-1)):
        for col in range(config.columns-(config.inarow-1)):
            window = list(grid[range(row, row+config.inarow), range(col, col+config.inarow)])
            if is_terminal_window(window, config):
                return True
    # negative diagonal
    for row in range(config.inarow-1, config.rows):
        for col in range(config.columns-(config.inarow-1)):
            window = list(grid[range(row, row-config.inarow, -1), range(col, col+config.inarow)])
            if is_terminal_window(window, config):
                return True
    return False

# Minimax implementation
def minimax(node, depth, maximizingPlayer, mark, config):
    ''' Minimax implementation
    
    Parameters: 
    ----------- 
    node : numpy array 
        The current node representing the game state. 
    
    depth : int 
        The depth to which the minimax algorithm should search. 
    
    maximizingPlayer : bool 
        True if the current player is maximizing, False if minimizing. 
    
    mark : int 
        The value of the piece to be evaluated. 
    
    config : dict 
        A dictionary containing the configuration parameters of the game. 
    
    Returns: 
    -------- 
    int 
        The optimal value of the current node calculated using the minimax algorithm. 
    '''
    is_terminal = is_terminal_node(node, config)
    valid_moves = [c for c in range(config.columns) if node[0][c] == 0]
    if depth == 0 or is_terminal:
        return get_heuristic(node, mark, config)
    if maximizingPlayer:
        value = -np.Inf
        for col in valid_moves:
            child = drop_piece(node, col, mark, config)
            value = max(value, minimax(child, depth-1, False, mark, config))
        return value
    else:
        value = np.Inf
        for col in valid_moves:
            child = drop_piece(node, col, mark%2+1, config)
            value = min(value, minimax(child, depth-1, True, mark, config))
        return value