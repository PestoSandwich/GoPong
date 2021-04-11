import abc
from settings import *
import settings as st
from threading import Thread
import threading as th

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
        self.done = False
        self.player_id = None
        self.active_player = None
        self.opponent = None

    # initialize steps which require heavy calculations and should not be redone when the bot is copied
    # todo initialize is not implemented for bots
    def initialize(self):
        pass

    def update(self, reward, action, done):
        st.INTERFACE.set_evaluation(self.player_id, reward, action)
        st.INTERFACE.set_done(self.player_id, done)

    # reset the bot values
    def reset(self):
        self.action_list = []
        self.evaluation = NEGATIVE_INFINITY
        self.done = False

    # By default, bots do not store data and can be passed without copying. If your bot doesnt, update get_clone
    def get_clone(self):
        return self

    def start(self, protagonist, antagonist):
        best_reward, action_branch = self._rate_and_play(protagonist, antagonist)
        st.INTERFACE.set_evaluation(self.player_id, best_reward, action_branch)
        st.INTERFACE.set_done(self.player_id, True)

    @abc.abstractmethod
    def _rate_and_play(self, protagonist, antagonist):
        return None, None

    # the rating of a player is depending on his hitpoints and the pieces on the board. Here you can modify their
    # relationship
    def rate_game_position(self, active_board_rating, active_hp, opponent_board_rating, opponent_hp):
        return (active_hp * HITPOINTS + active_board_rating) - (opponent_hp * HITPOINTS +
                                                                opponent_board_rating)

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
