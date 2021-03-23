from settings import *
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

    # Take unnecessary calculations away from def_init. Player.initialize() is called by the host Gym. Newly created
    # players outside of the GymGame should use old_player.get_copy() instead of creating a new player.
    def initialize(self):
        self.__grid = [[0 for x in range(BOARD_COLUMNS)] for y in range(BOARD_ROWS)]
        self.action_shape = (BOARD_COLUMNS * BOARD_ROWS) * (
                BOARD_COLUMNS * BOARD_ROWS) + BOARD_COLUMNS * BOARD_ROWS

    # new player objects should be made as copy's of existing player objects.
    def get_copy(self):
        clone = Player(self.player_id + 1, self.bot.get_clone())
        clone.action_shape = self.action_shape
        clone.set_board_as_copy(self.__grid)
        clone.num_active = self.num_active
        clone.hp = self.hp
        clone.__board_rating = self.__board_rating
        clone.threatened_attacks = [[*attack] for attack in self.threatened_attacks]
        return clone

    # get_rating calls the bot method which determines the rating from the pre_calculated rating of both boards and
    # the \ player's hp TODO different bots will result in different board_ratings. Can't compare these to each other
    def get_rating(self, opponent):
        return self.bot.rate_game_position(self.__board_rating, self.hp, opponent.__board_rating, opponent.hp)

    # make call to the bot's rate_cell method
    def __rate_cell(self, r, c):
        return self.bot.rate_cell(r, c, self.__grid)

    # reset all non-constant values to their initial position (grid and hp
    def reset(self, initial_grid, initial_hp):
        self.set_custom_board(initial_grid)
        self.hp = initial_hp

    # Copy a board and calculate the board rating. This is used at the start of the game by the gym method and should
    # not be used by bots as it is quite slow
    def set_custom_board(self, grid):
        self.__grid = [[0 for x in range(BOARD_COLUMNS)] for y in range(BOARD_ROWS)]
        self.num_active = 0
        self.threatened_attacks = []
        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLUMNS):
                if grid[r][c] > 0:
                    self.__place_piece(grid[r][c], r, c)

    # getter for the players board which makes a copy to avoid accidentally changing the original values
    def get_board(self):
        return [[*row] for row in self.__grid]

    # sets board as copy of a board.
    def set_board_as_copy(self, grid):
        self.__grid = [[*row] for row in grid]

    # place piece method which must be called to update values of cells. place_piece keeps self.__board_rating up
    # to date.
    def __place_piece(self, value, row, column):
        old_cell_value = self.__grid[row][column]
        # rate selected cell
        prev_rating = self.__rate_cell(row, column)
        if row > 0:
            # rate cells whose rating depends on selected cell
            prev_rating += self.__rate_cell(row - 1, column)

        # modify selected cell
        self.__grid[row][column] = value

        # check an active piece is placed or removed
        if value == 2 and old_cell_value != 2:
            # update the total number of active pieces
            self.num_active += 1
        # if an active piece is placed, complete formations and attack should be checked after place_piece is called.
        elif value != 2 and old_cell_value == 2:
            # update the total number of active pieces
            self.num_active -= 1
            # if an active piece is removed, remove all near_complete formations which the active piece was a part of
            remove_list = []
            for attack in self.threatened_attacks:
                for vector in attack[1]:
                    if vector[0] == row and vector[1] == column:
                        remove_list.append(attack)
            self.threatened_attacks = [item for item in self.threatened_attacks if item not in remove_list]

        # rate selected cell after modification
        new_rating = self.__rate_cell(row, column)
        if row > 0:
            # rate cells whose rating depends on selected cell after modification
            new_rating += self.__rate_cell(row - 1, column)

        # update board rating with the new rating of the modified cells
        self.__board_rating += (new_rating - prev_rating)

    # damage_piece is called when an attack hits a piece.
    def __hit(self, target, column):
        # Subtract 2 from the value of the damages piece (always resulting in 0)
        self.__place_piece(max(0, self.__grid[target][column] - 2), target, column)
        if target - 1 >= 0:
            # If there is a cell located after the target, subtract 1 from the value of that cell
            self.__place_piece(max(0, self.__grid[target - 1][column] - 1), target, column)

    def __deactivate(self, row, column):
        self.__place_piece(1, row, column)

    # send 'amount' of bullets over a single column. Checking cells from high row numbers to low row numbers.
    # if a bullet encounters a non 0 cell, it will __hit() the cell and the bullet is defended.
    # if a bullet passes the last row without being defended, the players hp is reduced by 1
    def attack(self, column, amount):
        for x in range(amount):
            defended = False
            target = BOARD_ROWS
            for i in range(BOARD_ROWS):
                target -= 1
                if self.__grid[target][column] > 0:
                    self.__hit(target, column)
                    defended = True
            if not defended:
                self.hp -= 1

    # first check if the cell is both within the boundaries of the board
    # then check if the cell has the required values
    def is_cell_value(self, value, row, column):
        if self.cell_exists(row, column):
            if self.__grid[row][column] == value:
                return True
        return False

    def is_cell_valid(self, value, row, column):
        if self.cell_exists(row, column):
            if self.__grid[row][column] < value:
                return True
        return False

    def cell_exists(self, row, column):
        return 0 <= row < BOARD_ROWS and 0 <= column < BOARD_COLUMNS

    # code which both checks if a complete formation is formed, and adds near complete formations to the
    # threatened_attacks set
    def check_formation(self, row, column):
        found_formation = False
        complete_formation = None
        found_attacks = []
        if self.num_active > 1:
            for formation in FORMATIONS:
                missing_pieces = []
                number_missing = 0
                for vector in formation:
                    if not self.is_cell_value(2, row + vector[0], column + vector[1]):
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

    # all calls to modify a player's board outside of the player class should be made through the execute methods.
    # actions [ 0 - board-positions] -> active pieces
    # actions [ board_positions - board_positions*board_positions ] -> sets of two inactive pieces
    def execute_action(self, p2, action):
        self.execute_vrc(p2, hf.action_to_vrc(action))

    # vrc = [[value_a, row_a, column_a],[value_b, row_b column_c],[etc..]]
    def execute_vrc(self, p2, vrc):
        for element in vrc:
            value, row, column = element[0], element[1], element[2]
            self.__place_piece(value, row, column)

            # Check if the just placed active piece created valid formations and if so, attack
            if value == 2:
                formation = self.check_formation(row, column)
                if formation is not None:
                    p2.attack(column, len(formation))
                    for vector in formation:
                        self.__deactivate(row + vector[0], vector[1] + column)
