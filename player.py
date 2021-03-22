from settings import *
from formations import *
import helperfunctions as hf


class Player:
    def __init__(self, player_id, bot):
        self.bot = bot
        self.action_shape = 0
        self.num_active = 0
        self.__board_rating = 0
        self.hp = 7
        self.__grid = None
        self.player_id = player_id
        self.threatened_attacks = []

    def initialize(self):
        # Take unnecessary calculations away from def_init, Player.initialize() is called by the host Gym
        self.__grid = [[0 for x in range(BOARD_COLUMNS)] for y in range(BOARD_ROWS)]
        self.action_shape = (BOARD_COLUMNS * BOARD_ROWS) * (
                BOARD_COLUMNS * BOARD_ROWS) + BOARD_COLUMNS * BOARD_ROWS

    def get_copy(self):
        clone = Player(self.player_id + 1, self.bot)
        clone.action_shape = self.action_shape
        clone.setCopyBoard(self.__grid)
        clone.num_active = self.num_active
        clone.hp = self.hp
        clone.__board_rating = self.__board_rating
        clone.threatened_attacks = [[*attack] for attack in self.threatened_attacks]
        return clone

    def get_rating(self):
        return self.bot.get_combined_rating(self.__board_rating, self.hp)

    def isvalid(self, value, r, c):
        if self.__grid[r][c] < value:
            return True
        return False

    def __rate_cell(self, r, c):
        return self.bot.rate_cell(r, c, self.__grid)

    def reset(self, grid, hp):
        self.setCustomBoard(grid)
        self.hp = hp

    def setCustomBoard(self, grid):
        self.__grid = [[0 for x in range(BOARD_COLUMNS)] for y in range(BOARD_ROWS)]
        self.num_active = 0
        self.threatened_attacks = []
        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLUMNS):
                if grid[r][c] > 0:
                    self.placepiece(r,c,grid[r][c])

    def get_board(self):
        return [[*row] for row in self.__grid]

    def setCopyBoard(self, grid):
        self.__grid = [[*row] for row in grid]

    def placepiece(self, row, column, value):
        prev_rating = self.__rate_cell(row, column)
        if row > 0:
            prev_rating += self.__rate_cell(row - 1, column)

        self.__grid[row][column] = value
        if value == 2:
            self.num_active += 1

        new_rating = self.__rate_cell(row, column)
        if row > 0:
            new_rating += self.__rate_cell(row - 1, column)

        self.__board_rating += (new_rating - prev_rating)

    def __damage_piece(self, row, column, value):
        if self.__grid[row][column] == 2:
            self.num_active -= 1
            removelist= []
            for attack in self.threatened_attacks:
                for vector in attack[1]:
                    if vector[0] == row and vector[1] == column:
                        removelist.append(attack)
            self.threatened_attacks = [item for item in self.threatened_attacks if item not in removelist]
            if value == 2:
                self.placepiece(row, column, 0)
            else:
                self.placepiece(row, column, 1)
        else:
            self.placepiece(row, column, 0)

    def __deactivate(self, row, column):
        self.placepiece(row, column, 1)
        self.num_active -= 1
        removelist = []
        for attack in self.threatened_attacks:
            for vector in attack[1]:
                if vector[0] == row and vector[1] == column:
                    removelist.append(attack)
        self.threatened_attacks = [item for item in self.threatened_attacks if item not in removelist]

    def attack(self, column, amount):
        for x in range(amount):
            defended = False
            for i in range(BOARD_ROWS):
                target = BOARD_ROWS - 1 - i
                if self.__grid[target][column] > 0:
                    self.__damage_piece(target, column, 2)
                    if target - 1 >= 0:
                        self.__damage_piece(target - 1, column, 1)
                    defended = True
                    break
            if not defended:
                self.hp -= 1

    def check_cell(self, value, row, column):
        if 0 <= row < BOARD_ROWS and 0 <= column < BOARD_COLUMNS:
            if value == self.__grid[row][column]:
                return True
        return False

    def checkformation(self, row, column):
        found_formation = False
        complete_formation = None
        found_attacks = []
        if self.num_active > 1:
            for formation in all_formations():
                missing_pieces = []
                number_missing = 0
                for vector in formation:
                    if not self.check_cell(2, row + vector[0], column + vector[1]):
                        missing_pieces.append([row + vector[0], column + vector[1]])
                        number_missing += 1
                if number_missing == 0:
                    complete_formation = formation
                    found_formation = True
                    break
                elif number_missing == 1 and found_formation is False:
                    if 0 <= missing_pieces[0][0] < BOARD_ROWS and 0 <= missing_pieces[0][1] < BOARD_COLUMNS:
                        new_formation = []
                        for vector in formation:
                            new_formation.append([vector[0] + row, vector[1] + column])
                        found_attacks.append([missing_pieces[0], new_formation])
        if found_formation is False:
            self.threatened_attacks.extend(found_attacks)
        return complete_formation

    def execute_action(self, p2, action):
        self.execute_vrc(p2, hf.action_to_vrc(action))

    # vrc = [[value_a, row_a, column_a],[value_b, row_b column_c],[etc..]]
    def execute_vrc(self, p2, vrc):
        for element in vrc:
            value, row, column = element[0], element[1], element[2]
            self.placepiece(row, column, value)

            # Check if the just placed active piece created valid formations
            if (value == 2):
                formation = self.checkformation(row, column)
                if formation is not None:
                    p2.attack(column, len(formation))
                    for vector in formation:
                        self.__deactivate(row + vector[0], vector[1] + column)
