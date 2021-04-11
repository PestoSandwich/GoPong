from bot import Bot
import abc
from settings import *
import transpositions as tp
from minimax import MiniMax
from iterativedeepening import IterativeDeepening

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
SEARCHDEPTH = 2


class MarkMiniMaxBot(Bot, abc.ABC):
    def __init__(self):
        super().__init__()
        self.search_depth = SEARCHDEPTH
        self.transpositions = tp.Transpositions()

    def _rate_and_play(self, protagonist, antagonist):
        minimax = MiniMax(self, SEARCHDEPTH, self.transpositions)
        reward, action_list = minimax.minimax(protagonist, antagonist, 0, NEGATIVE_INFINITY, NEGATIVE_INFINITY)
        return reward, action_list

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


class MarkIDBot(MarkMiniMaxBot, abc.ABC):
    def __init__(self):
        super().__init__()
        self.max_time = 10

