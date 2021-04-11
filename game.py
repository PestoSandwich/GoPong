from abc import ABC
import gym
from savegame import SaveGame
from gym import spaces
from player import Player
import numpy as np
from settings import *
import settings as st
import helperfunctions as hf
from bots.mark_minimax.markminimaxbot import MarkMiniMaxBot
from bots.mark_minimax.markminimaxbot import MarkIDBot

doprint = False


def get_bot(type):
    if type == MARK_MINIMAX_1:
        bot = MarkMiniMaxBot()
        bot.search_depth = 1
    elif type == MARK_MINIMAX_2:
        bot = MarkMiniMaxBot()
        bot.search_depth = 2
    elif type == MARK_ID_2:
        bot = MarkIDBot()
        bot.max_time = 2
    elif type == MARK_ID_10:
        bot = MarkIDBot()
        bot.max_time = 10
    elif type == MARK_ID_60:
        bot = MarkIDBot()
        bot.max_time = 60
    else:
        bot = MarkMiniMaxBot()
    return bot


# ---------------------------------------------------------------------------------------------------------------------------
# Gym class which operates the game


# represent the boardstate in a way deeplearning algoritms can work with. [2, board.positions + 4]



class GymGame(gym.Env, ABC):
    def __init__(self, p1_type, p2_type):
        self.p1_bot = get_bot(p1_type)
        self.p2_bot = get_bot(p2_type)
        self.save_game = True
        self.turn = 0

        self.p1_type = p1_type
        self.p2_type = p2_type
        self.first_player_id = 10000
        self.second_player_id = 20000

        # calculate action space and observation space from board_rows and board_columns

        self.board_rows = BOARD_ROWS
        self.board_columns = BOARD_COLUMNS
        self.board_positions = int(self.board_columns * self.board_rows)
        self.observation_shape = (2, self.board_rows * self.board_columns + 3)
        self.observation_space = spaces.Box(low=0, high=2, shape=self.observation_shape, dtype=np.int64)
        self.action_input_shape = self.board_positions + self.board_positions * self.board_positions
        self.action_space = gym.spaces.Discrete(self.action_input_shape)

        # Initialize players, for performance: new players must be created as copies of existing player objects.
        # player_id = 10000 for player 1 and 20000 for player 2. A copied players id will be 1 higher than the original.
        # player 1 makes the first move.
        self.p1 = Player(self.first_player_id, self.p1_bot)
        self.p1.initialize()
        st.INTERFACE.set_bot(self.p1.player_id, p1_type)
        self.p2 = Player(self.second_player_id, self.p2_bot)
        st.INTERFACE.set_bot(self.p2.player_id, p2_type)
        self.p2.initialize()
        st.INTERFACE.set_players(self.p1, self.p2)

        self.__stored_game = None

    def get_active_player_id(self):
        if self.turn % 2 == 0:
            return self.first_player_id
        else:
            return self.second_player_id

    # getter method for the stored_game object
    def get_saved_game(self):
        return self.__stored_game

    # Sets the board state of the players, set_custom_board will recalculate the __board_rating of the player
    def set_board(self, p1_boardstate, p2_boardstate):
        self.p1.set_custom_board(p1_boardstate)
        self.p2.set_custom_board(p2_boardstate)

    # reset the environment to initial state and returns the observation. The observation always returns the \
    # board of the player who has to make the next move first.
    def reset(self):
        self.p1.reset(PLAYER_1_BOARD, PLAYER_1_HP)
        self.p2.reset(PLAYER_2_BOARD, PLAYER_2_HP)
        self.__stored_game = SaveGame(self.p1, self.p2)
        return hf.get_observation(self.p1, self.p2)

    # step will execute the action for the currently active player. The currently active player is determined
    # with the turn counter. On even turns the first player is playing, on uneven turns the second player is playing
    def step(self, action):
        if self.turn % 2 == 0:
            # execute_action (and execute_vrc) will perform the action on the board of the player it is called at and
            # \ make calls to the other methods resolving complete formations and following attacks. The player given
            # as argument in the method is the player that receives the attacks if formations are formed.
            self.p1.execute_action(self.p2, action)

            # reward is the difference between the evaluation of both players which are in turn determined by the
            # bots they use
            # TODO: in matches between two different bots, the reward will be a combination of both ratings. plz fix
            reward = self.p1.get_rating(self.p2)

            # observation is a 2d list representation of the board state and both players hp, which neural networks can
            # use
            observation = hf.get_observation(self.p2, self.p1)

            # if any players hp is 0 or lower, the game ends.
            done = self.p1.hp < 1 or self.p2.hp < 1
        else:
            self.p2.execute_action(self.p1, action)
            reward = self.p2.get_rating(self.p1)
            observation = hf.get_observation(self.p1, self.p2)
            done = self.p1.hp < 1 or self.p2.hp < 1

        if self.save_game:
            # If save_game is turned on, store the gamestate
            self.__stored_game.store(self.p1, self.p2)

        # Increase the turn counter which is used to determine which player is making a move
        self.turn += 1
        return observation, reward, done, None
