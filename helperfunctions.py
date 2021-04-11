import numpy as np
from settings import *


# vrc = [[value_a, row_a, column_a],[value_b, row_b column_c],[etc..]]
def action_to_vrc(action):
    vrc = []
    if action < BOARD_COLUMNS * BOARD_ROWS:
        # Place an active piece
        row = int(np.floor(action / BOARD_COLUMNS))
        column = int(action % BOARD_COLUMNS)
        vrc.append([2, row, column])

    else:
        # Subtract the action space of the active piece, Extract the values of the first and second inactive piece
        action = action - BOARD_COLUMNS * BOARD_ROWS
        first = int(np.floor(action / (BOARD_COLUMNS * BOARD_ROWS)))
        second = action % (BOARD_COLUMNS * BOARD_ROWS)
        firstrow = int(np.floor(first / BOARD_COLUMNS))
        firstcol = int(first % BOARD_COLUMNS)
        secondrow = int(np.floor(second / BOARD_COLUMNS))
        secondcol = int(second % BOARD_COLUMNS)
        vrc.append([1, firstrow, firstcol])
        vrc.append([1, secondrow, secondcol])
    return vrc


# vrc = [[value_a, row_a, column_a],[value_b, row_b column_c],[etc..]]
def vrc_to_action(vrc):
    if len(vrc) == 2:
        first = vrc[0][1] * BOARD_COLUMNS + vrc[0][2]
        second = vrc[1][1] * BOARD_COLUMNS + vrc[1][2]
        action = (first * (BOARD_COLUMNS * BOARD_ROWS) + second) + BOARD_COLUMNS * BOARD_ROWS
    else:
        action = vrc[0][1] * BOARD_COLUMNS + vrc[0][2]
    return action


def array_to_action(self, row, col):
    return col + ((self.board_columns * row))


def action_to_array(self, action):
    row = int(np.floor(action / self.board_columns))
    column = int(action % self.board_columns)
    return row, column


# this is used to convert the players hp into a list which can be extended onto the board representation for the
# observation
def decimal_to_array(n):
    # 3 is added so that we only store positive integers
    n = n + 3
    if n == 0:
        nums = [0]
    else:
        nums = []
        while n:
            n, r = divmod(n, 3)
            nums.append(r)

    # add zero's until the list is of length 3
    for i in range(3 - len(nums)):
        nums.append(0)

    return nums

def get_observation(pro, ant):
    # flatten the boardstate of player 1 in a single list
    p1_observation = [j for sub in pro.get_board() for j in sub]
    p2_observation = [j for sub in ant.get_board() for j in sub]
    # add the hitpoints of the player to the end to the list represented in ternary. '+3' is added to avoid negative hp
    p1_observation.extend(decimal_to_array(pro.hp + 3))
    p2_observation.extend(decimal_to_array(ant.hp + 3))
    return [p1_observation, p2_observation]