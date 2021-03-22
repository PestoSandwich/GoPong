from abc import ABC

import gym
from savegame import SaveGame
from gym import spaces
from player import Player
import numpy as np
from settings import *
import helperfunctions as hf
from bots.mark_minimax.markminimax import MarkMiniMax

doprint = False


# ---------------------------------------------------------------------------------------------------------------------------
# Gym class which operates the game

def get_observation(pro, ant):
    p1_observation = [j for sub in pro.get_board() for j in sub]
    p1_observation.extend(hf.decimal_to_array(pro.hp + 3))
    p2_observation = [j for sub in ant.get_board() for j in sub]
    p2_observation.extend(hf.decimal_to_array(ant.hp + 3))
    return [p1_observation, p2_observation]


class GymGame(gym.Env, ABC):
    def __init__(self, p1_type, p2_type):
        self.p1_bot = None
        self.p2_bot = None
        self.p1_type = p1_type
        self.p2_type = p2_type

        if self.p1_type == MARK_MINIMAX_1:
            self.p1_bot = MarkMiniMax()
            self.p1_bot.search_depth = 1
        elif self.p1_type == MARK_MINIMAX_2:
            self.p1_bot = MarkMiniMax()
            self.p1_bot.search_depth = 2
        else:
            self.p1_bot = MarkMiniMax()

        if self.p2_type == MARK_MINIMAX_1:
            self.p2_bot = MarkMiniMax()
            self.p2_bot.search_depth = 1
        elif self.p2_type == MARK_MINIMAX_2:
            self.p2_bot = MarkMiniMax()
            self.p2_bot.search_depth = 2
        else:
            self.p2_bot = MarkMiniMax()

        # if env_config is None:
        #     env_config = {}
        self.save_game = True
        self.turn = 0
        self.board_rows = BOARD_ROWS
        self.board_columns = BOARD_COLUMNS
        self.board_positions = int(self.board_columns * self.board_rows)
        self.observation_shape = (2, self.board_rows * self.board_columns + 3)
        self.observation_space = spaces.Box(low=0, high=2, shape=self.observation_shape, dtype=np.int64)
        self.action_input_shape = self.board_positions + self.board_positions * self.board_positions
        self.action_space = gym.spaces.Discrete(self.action_input_shape)

        self.p1 = Player(100, self.p1_bot)
        self.p1.initialize()
        self.p2 = Player(200, self.p2_bot)
        self.p2.initialize()
        self.stored_game = None

    def get_saved_game(self):
        return self.stored_game

    def set_board(self, p1_boardstate, p2_boardstate):
        self.p1.setCustomBoard(p1_boardstate)
        self.p2.setCustomBoard(p2_boardstate)

    def reset(self):
        # reset the environment to initial state
        self.p1.reset(PLAYER_1_BOARD, PLAYER_1_HP)
        self.p2.reset(PLAYER_2_BOARD, PLAYER_2_HP)
        self.stored_game = SaveGame(self.p1, self.p2)
        return get_observation(self.p1, self.p2)

    def step(self, action):
        if self.turn % 2 == 0:
            self.p1.execute_action(self.p2, action)
            reward = self.p2.get_rating() - self.p1.get_rating()
            observation = get_observation(self.p2, self.p1)
            done = self.p1.hp < 1 or self.p2.hp < 1
        else:
            self.p2.execute_action(self.p1, action)
            reward = self.p1.get_rating() - self.p2.get_rating()
            observation = get_observation(self.p1, self.p2)
            done = self.p1.hp < 1 or self.p2.hp < 1

        if self.save_game:
            self.stored_game.store(self.p1, self.p2)

        self.turn += 1
        return observation, reward, done, None
