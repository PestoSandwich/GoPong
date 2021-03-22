import numpy as np
from datetime import datetime
import helperfunctions as hf
from settings import *

class MinMax:
    def __init__(self, player_1, player_2, max_depth):
        self.max_depth = max_depth
        self.current_depth = 0
        self.player_1 = player_1
        self.player_2 = player_2
        self.alpha = -2000
        self.beta = -2000
        self.best_reward = -1001
        self.best_action_list = []
        self.type = None

    def start_minmax(self):
        begin_time = datetime.now()
        highest_reward, action_list = self.minmax(0, -2000,
                                                  -2000)

        print("-------------------------------------------------------------------")
        print((datetime.now() - begin_time))

        if len(action_list) > 0:
            return highest_reward, action_list[-1], action_list
        else:
            return highest_reward, 0, action_list

    def minmax(self, current_depth, alpha, beta):
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

            checked_action_reward, checked_action_list = self.evaluateMove(vrc)
            checked_action_list.append(checked_action)

            if self.updateVariables(checked_action_reward, checked_action_list):
                return self.best_reward, self.best_action_list

        if self.current_depth <= self.max_depth:
            for checked_action in range(self.player_1.action_shape):
                self.progressbar()

                valid, vrc = self.PruneAndConvert(checked_action)

                if valid:
                    checked_action_reward, checked_action_list = self.evaluateMove(vrc)
                    checked_action_list.append(checked_action)

                    if self.updateVariables(checked_action_reward, checked_action_list):
                        return self.best_reward, self.best_action_list

        return self.best_reward, self.best_action_list

    def progressbar(self):
        if self.current_depth == 0:
            pass
            # if checked_action % np.floor(self.action_shape / 5) == 0:
            #     print("Calculating for player_id: ", self.player_id, "progress:",
            #           np.floor((checked_action / self.action_shape) * 100), "%")

    def PruneAndConvert(self, checked_action):
        if checked_action in self.player_1.prune_set:
            return False, None

        vrc = hf.action_to_vrc(checked_action)

        if self.player_2.num_active < 2 and vrc[0][0] == 1:
            return False, None

        # Check if the action is valid
        for element in vrc:
            if not (self.player_1.isvalid(element[0], element[1], element[2])):
                return False, None

            if element[0] == 1:
                need_defender = False
                for attack in self.player_2.threatened_attacks:
                    if attack[0][1] == element[2]:
                        need_defender = True
                if not need_defender:
                    return False, None

        return True, vrc

    def evaluateMove(self, vrc):
        p1_clone = self.player_1.get_copy()
        p2_clone = self.player_2.get_copy()
        p1_clone.execute_vrc(p2_clone, vrc)

        if p2_clone.hp <= 0:
            return VICTORY + self.player_1.get_rating() - self.player_2.get_rating(), []

        if (len(
                p2_clone.threatened_attacks) > 0 or self.current_depth < self.max_depth) and self.current_depth < self.max_depth + 1:
            new_minmax = MinMax(p2_clone, p1_clone, self.max_depth)
            checked_action_reward, checked_action_list = new_minmax.minmax(self.current_depth + 1, self.alpha,
                                                                           self.beta)
            checked_action_reward *= -1
        else:
            checked_action_reward = p1_clone.get_rating() - p2_clone.get_rating()
            checked_action_list = []
        # Determine new board reward

        if self.current_depth == 0:
            addition = (np.random.randint(0, 1000) / 100000.0)
            checked_action_reward += addition
        return checked_action_reward, checked_action_list

    def updateVariables(self, checked_action_reward, checked_action_list):
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