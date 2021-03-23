from bot import Bot
import abc
from settings import *
import numpy as np
import helperfunctions as hf

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


class MarkMiniMax(Bot, abc.ABC):
    def __init__(self):
        super().__init__()
        self.search_depth = SEARCHDEPTH

    def evaluate_move(self, active_player, opponent, vrc):
        minimax = MiniMax(self.search_depth)
        minimax.initialize()
        checked_action_reward, checked_action_list = minimax.evaluate_move(active_player, opponent, vrc)
        return checked_action_reward, checked_action_list

    def get_best_move(self, active_player, opponent):
        minimax = MiniMax(self.search_depth)
        minimax.initialize()
        checked_action_reward, checked_action_list = minimax.minimax(active_player, opponent, 0, -2000, -2000)

        if len(checked_action_list) > 0:
            return checked_action_list[-1], checked_action_reward, checked_action_list
        else:
            return 0, checked_action_reward, checked_action_list

    def evaluate_position(self, active_player, opponent):
        minimax = MiniMax(self.search_depth)
        minimax.initialize()
        checked_action_reward, checked_action_list = minimax.minimax(active_player, opponent, 0, -2000, -2000)
        return checked_action_reward, checked_action_list

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


# TODO minimax at search depth 1 will not end the game. 3500 moves and counting with both players at 1 hp.
class MiniMax:
    def __init__(self, max_depth):
        self.max_depth = max_depth
        self.current_depth = 0
        self.player_1 = None
        self.player_2 = None
        self.alpha = -2000
        self.beta = -2000
        self.best_reward = -1001
        self.best_action_list = []
        self.type = None
        self.prune_set = set()

    def initialize(self):
        self.populate_prunelist()

    def get_clone(self):
        minimax = MiniMax(self.max_depth)
        minimax.prune_set = self.prune_set
        return minimax

    def minimax(self, player_1, player_2, current_depth, alpha, beta):
        self.player_1 = player_1
        self.player_2 = player_2
        self.alpha = alpha
        self.beta = beta
        self.current_depth = current_depth

        if self.current_depth % 2 == 0:
            self.type = 'max'
        else:
            self.type = 'min'

        for attack in self.player_1.threatened_attacks:
            vrc = [[2, attack[0][0], attack[0][1]]]
            checked_action = hf.vrc_to_action(vrc)

            checked_action_reward, checked_action_list = self.evaluate_move(player_1, player_2, vrc)
            checked_action_list.append(checked_action)

            if self.__update_variables(checked_action_reward, checked_action_list):
                return self.best_reward, self.best_action_list

        if self.current_depth <= self.max_depth:
            for checked_action in range(self.player_1.action_shape):
                self.__progressbar()

                valid, vrc = self.__prune_and_convert(checked_action)

                if valid:
                    checked_action_reward, checked_action_list = self.evaluate_move(player_1, player_2, vrc)
                    checked_action_list.append(checked_action)

                    if self.__update_variables(checked_action_reward, checked_action_list):
                        return self.best_reward, self.best_action_list

        return self.best_reward, self.best_action_list

    def populate_prunelist(self):
        pruneset = set()
        safeset = set()
        for action in range(BOARD_ROWS * BOARD_COLUMNS + (BOARD_ROWS * BOARD_COLUMNS) * (BOARD_ROWS * BOARD_COLUMNS)):
            vrc = hf.action_to_vrc(action)
            if len(vrc) > 1:
                if (vrc[0][2] == vrc[1][2]) and (abs(vrc[0][1] - vrc[1][1]) <= 1):
                    pruneset.add(action)
                else:
                    order_pair = [vrc[1], vrc[0]]
                    order_pair_action = hf.vrc_to_action(order_pair)
                    if order_pair_action not in safeset:
                        safeset.add(action)
                        pruneset.add(order_pair_action)

        self.prune_set = pruneset

    def __progressbar(self):
        if self.current_depth == 0:
            pass
            # if checked_action % np.floor(self.action_shape / 5) == 0:
            #     print("Calculating for player_id: ", self.player_id, "progress:",
            #           np.floor((checked_action / self.action_shape) * 100), "%")

    def __prune_and_convert(self, checked_action):
        if checked_action in self.prune_set:
            return False, None

        vrc = hf.action_to_vrc(checked_action)

        if self.player_2.num_active < 2 and vrc[0][0] == 1:
            return False, None

        # Check if the action is valid
        for element in vrc:
            if not (self.player_1.is_cell_valid(element[0], element[1], element[2])):
                return False, None

            if element[0] == 1:
                need_defender = False
                for attack in self.player_2.threatened_attacks:
                    if attack[0][1] == element[2]:
                        need_defender = True
                if not need_defender:
                    return False, None

        return True, vrc

    def evaluate_move(self, player_1, player_2, vrc):
        p1_clone = player_1.get_copy()
        p2_clone = player_2.get_copy()
        p1_clone.execute_vrc(p2_clone, vrc)

        if p2_clone.hp <= 0:
            return VICTORY + self.player_1.get_rating(self.player_2), []

        if (len(p2_clone.threatened_attacks) > 0 or self.current_depth < self.max_depth) and \
                self.current_depth < self.max_depth + 1:
            new_minimax = MiniMax(self.max_depth)
            new_minimax.prune_set = self.prune_set
            checked_action_reward, checked_action_list = new_minimax.minimax(p1_clone, p2_clone, self.current_depth + 1,
                                                                             self.alpha, self.beta)
            checked_action_reward *= -1
        else:
            checked_action_reward = p1_clone.get_rating(p2_clone)
            checked_action_list = []
        # Determine new board reward

        if self.current_depth == 0:
            addition = (np.random.randint(0, 1000) / 100000.0)
            checked_action_reward += addition
        return checked_action_reward, checked_action_list

    def __update_variables(self, checked_action_reward, checked_action_list):
        if type == 'max':
            # Update best action
            if checked_action_reward > self.best_reward:
                self.best_reward = checked_action_reward
                self.best_action_list = checked_action_list

            # Alpha beta pruning
            if self.best_reward < self.beta:
                return True

            if self.best_reward > self.alpha:
                self.alpha = self.best_reward
        else:
            # Update best action
            if checked_action_reward > self.best_reward:
                self.best_reward = checked_action_reward
                self.best_action_list = checked_action_list

            # Alpha beta pruning
            if self.best_reward < self.alpha:
                return True

            if self.best_reward > self.beta:
                self.beta = self.best_reward

        return False
