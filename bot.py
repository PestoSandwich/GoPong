import abc
from settings import *

# ----------------------------------------------------------
# Variables the default reward algorithm uses

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


# Abstract class Bot is extended by your AI
class Bot(abc.ABC):
    def __init__(self):
        pass

    # By default, bots do not store data and can be passed without copying. If your bot doesnt, update get_clone
    @abc.abstractmethod
    def get_clone(self):
        return self

    # This is the main method of your ai. both the active_player and opponent are pointers to the actual object.
    # Use data stored in them to determine the best move
    @abc.abstractmethod
    def get_best_move(self, active_player, opponent):
        best_reward = None
        best_action = None
        return best_action, best_reward

    # Simpler method requesting your bot to evaluate the current position. You can use the player.getRating() method
    # for this the player.get_rating() method will make calls to your bot for evaluation. namely: rate_cell() and
    # get_combined_rating()
    @abc.abstractmethod
    def evaluate_position(self, active_player, opponent):
        best_reward = None
        return best_reward

    # evaluate position after the requested move has been made. You likely do not need to incorporate this method as the
    # current implementation will work in most circumstances. But you have the option ^^
    def evaluate_move(self, active_player, opponent, vrc):
        active_player_clone = active_player.getClone()
        opponent_clone = opponent.getClone()
        # vrc stores moves: [[1, row_a, column_a],[1, row_b, column_b]] in case of two inactive pieces
        active_player_clone.execute_vrc(opponent_clone, vrc)
        return self.evaluate_position(opponent_clone, active_player_clone)

    # the rating of a player is depending on his hitpoints and the pieces on the board. Here you can modify their
    # relationship
    def get_combined_rating(self, board_rating, current_hitpoints):
        return board_rating + current_hitpoints * HITPOINTS

    # The __board_rating of the player which is given to 'get_combined_rating() is updated every time a cell is
    # modified. the rate-cell is called twice. To subtract the old value of the players board rating and then add the
    # new rating

    # r == 0 is the row in the back and last to be hit by attacks. c == 0 is the leftmost column.
    #
    # WARNING: do not modify the grid variable, it is not a copy.
    def rate_cell(self, r, c, grid):
        rating = 0
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

        # If the piece is placed along the edges subtract value.
        if r == BOARD_ROWS - 1:
            rating += FRONTBACK_SIDE_PLACEMENT_PENALTY
        if c == 0 or c == BOARD_COLUMNS - 1:
            rating += SIDE_PLACEMENT_PENALTY

        return rating
