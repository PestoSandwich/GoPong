import numpy as np
import helperfunctions as hf
from settings import *
import transpositions as tp


class MiniMax:
    def __init__(self, bot, max_depth, transpositions):
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
        self.transpositions = transpositions
        self.bot = bot

    def initialize(self):
        self.populate_prunelist()

    def get_clone(self):
        minimax = MiniMax(self.bot, self.max_depth, self.transpositions)
        minimax.prune_set = self.prune_set
        minimax.transpositions = self.transpositions
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

        game_hash = tp.hash_gamestate(hf.get_observation(p1_clone, p2_clone))
        existing_transposition = self.transpositions.get_transposition(game_hash, self.max_depth - self.current_depth)
        if existing_transposition is not None:
            reward, action_list = existing_transposition
            return reward, action_list

        if (len(p2_clone.threatened_attacks) > 0 or self.current_depth < self.max_depth) and \
                self.current_depth < self.max_depth + 1:
            new_minimax = self.get_clone()
            checked_action_reward, checked_action_list = new_minimax.minimax(p2_clone, p1_clone, self.current_depth + 1,
                                                                             self.alpha, self.beta)
            checked_action_reward *= -1

            self.transpositions.store_transposition(game_hash, checked_action_reward, checked_action_list,
                                                    self.max_depth - self.current_depth)
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
