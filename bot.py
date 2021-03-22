import abc
from settings import *

BASE_ACTIVE = 1
BASE_INACTIVE = 0.25
BASE_EMPTY = 0
INACTIVE_HIDING_PENALTY = -0.25
ACTIVE_HIDING_PENALTY = -0.1
EVEN_ROWS = 0.05
SIDE_PLACEMENT_PENALTY = -0.03
FRONTBACK_SIDE_PLACEMENT_PENALTY = -0.02
HITPOINTS = 3.5
VICTORY = 1000

class Bot(abc.ABC):
    def __init__(self):
        pass

    @abc.abstractmethod
    def get_clone(self):
        return self

    @abc.abstractmethod
    def get_best_move(self, active_player, opponent):
        best_reward = None
        best_action = None
        return best_action, best_reward

    @abc.abstractmethod
    def evaluate_position(self, active_player, opponent):
        best_reward = None
        return best_reward

    def evaluate_move(self, active_player, opponent, vrc):
        active_player_clone = active_player.getClone()
        opponent_clone = opponent.getClone()
        active_player_clone.execute_vrc(opponent_clone, vrc)
        return self.evaluate_position(opponent_clone, active_player_clone)

    def get_combined_rating(self, board_rating, current_hitpoints):
        return board_rating + current_hitpoints*HITPOINTS

    # DO NOT MODIFY THE GIVEN GRID, FOR PERFORMANCE REASONS THE GRID IS NOT A COPY
    def rate_cell(self, r, c, grid):
        rating = 0
        # What is the value of the cell
        if r == 0 or r == BOARD_ROWS - 1:
            rating += FRONTBACK_SIDE_PLACEMENT_PENALTY
        if c == 0 or c == BOARD_COLUMNS - 1:
            rating += SIDE_PLACEMENT_PENALTY
        if grid[r][c] == 1:
            rating += BASE_INACTIVE
            if r % 2 == 0:
                rating += EVEN_ROWS
            # Is the cell placed poorly?
            if r + 1 < BOARD_ROWS:
                if grid[r + 1][c] != 0:
                    rating += INACTIVE_HIDING_PENALTY
        elif grid[r][c] == 2:
            rating += BASE_ACTIVE
            if r % 2 == 0:
                rating += EVEN_ROWS
            # Is the cell placed poorly?
            if r + 1 < BOARD_ROWS:
                if grid[r + 1][c] != 0:
                    rating += INACTIVE_HIDING_PENALTY
        return rating
