from minimax import MiniMax
import datetime as dt
import helperfunctions as hf
from settings import *


class IterativeDeepening(MiniMax):
    def __init__(self, max_depth, transpositions, max_seconds):
        super().__init__(max_depth, transpositions)
        self.start_time = dt.datetime.now()
        self.max_seconds = max_seconds
        self.done = False

    def IterativeDeepening(self, player_1, player_2):
        self.best_reward = -2000
        self.best_action_list = []
        iteration_depth = 0
        self.start_time = dt.datetime.now()
        while True:
            self.max_depth = iteration_depth
            self.best_reward, self.best_action_list = self.minimax(player_1, player_2, 0, self.alpha, self.beta)

            if dt.datetime.now() - self.start_time > dt.timedelta(seconds=self.max_seconds):
                return self.best_reward, self.best_action_list
            iteration_depth += 1

    def minimax(self, player_1, player_2, current_depth, alpha, beta):
        self.player_1 = player_1
        self.player_2 = player_2
        self.alpha = alpha
        self.beta = beta
        self.current_depth = current_depth
        self.done = dt.datetime.now() - self.start_time < dt.timedelta(seconds=self.max_seconds)

        if self.current_depth % 2 == 0:
            self.type = 'max'
        else:
            self.type = 'min'

        for attack in self.player_1.threatened_attacks:
            if self.done:
                break
            vrc = [[2, attack[0][0], attack[0][1]]]
            checked_action = hf.vrc_to_action(vrc)

            checked_action_reward, checked_action_list = self.evaluate_move(player_1, player_2, vrc)
            checked_action_list.append(checked_action)

            if self.__update_variables(checked_action_reward, checked_action_list):
                return self.best_reward, self.best_action_list

        if self.current_depth <= self.max_depth:
            for checked_action in range(self.player_1.action_shape):
                if self.done:
                    break

                valid, vrc = self.__prune_and_convert(checked_action)

                if valid:
                    checked_action_reward, checked_action_list = self.evaluate_move(player_1, player_2, vrc)
                    checked_action_list.append(checked_action)

                    if self.__update_variables(checked_action_reward, checked_action_list):
                        return self.best_reward, self.best_action_list

        return self.best_reward, self.best_action_list

    def get_clone(self):
        minimax = IterativeDeepening(self.max_depth, self.transpositions, self.max_seconds)
        minimax.prune_set = self.prune_set
        minimax.transpositions = self.transpositions
        minimax.start_time = self.start_time
        return minimax

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
