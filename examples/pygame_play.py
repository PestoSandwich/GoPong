import pygame
import datetime
from pygame import freetype
from game import GymGame
import numpy as np
import helperfunctions as hf
from threading import Thread, Lock
from settings import *

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHT_GREY = (152, 152, 152)
DARK_GREY = (91, 91, 91)
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 900
BOX_WIDTH = 80
BOX_HEIGHT = 70
BOX_MARGIN = 10
DEFENDER_BOARD_OFFSET = 450
CONFIRM_X_OFFSET = 500
CONFIRM_Y_OFFSET = 120
CONFIRM_WIDTH = 180
CONFIRM_HEIGHT = 80
CONFIRM_COLOR = (230, 214, 190)
RESET_X_OFFSET = 700
RESET_Y_OFFSET = 120
RESET_WIDTH = 180
RESET_HEIGHT = 80
RESET_COLOR = (190, 214, 230)

control = ''

dead_img = pygame.transform.scale(pygame.image.load('../dist/assets/dead.png'), (BOX_WIDTH, BOX_HEIGHT))
red_img = pygame.transform.scale(pygame.image.load('../dist/assets/blue_live.png'), (BOX_WIDTH, BOX_HEIGHT))
blue_img = pygame.transform.scale(pygame.image.load('../dist/assets/red_live.png'), (BOX_WIDTH, BOX_HEIGHT))


def mouseposition_to_rowcolumn(x, y):
    row = np.ceil((y - BOX_MARGIN) / (BOX_MARGIN + BOX_HEIGHT)) - 1
    column = np.ceil((x - BOX_MARGIN) / (BOX_MARGIN + BOX_WIDTH)) - 1
    return row, column


class CommandLineInput:
    def __init__(self):
        self.new_input = False
        self.done = False
        self.input = ''

    def get_input(self):
        self.new_input = False
        return self.input

    def ask_input(self):
        while not self.done:
            self.input = input("Put your input here:")
            self.new_input = True


class Game:
    def __init__(self, p1_type, p2_type):
        self.player_1_time = None
        self.player_2_time = None
        self.datetime = 0
        self.confirm = False
        self.reset = False
        self.selected = 0
        self.stage = 'play'  # Play/ Review
        self.done = False
        self.player_1 = None
        self.player_2 = None

        self.p1_type = p1_type
        self.p2_type = p2_type

        self.env = GymGame(p1_type, p2_type)

        self.max_x_pos = BOARD_COLUMNS * (BOX_MARGIN + BOX_WIDTH)
        self.max_y_pos = BOARD_ROWS * (BOX_MARGIN + BOX_HEIGHT)
        self.stored_moves = []
        self.user_selection = [[0 for c in range(BOARD_ROWS)] for r in range(BOARD_COLUMNS)]

        pygame.init()
        self.clock = pygame.time.Clock()
        self.display = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('GoPong test')

        freetype.init()
        self.GAME_FONT = pygame.freetype.SysFont('Times new roman', 30)

    def __make_selection(self, r, c):
        if self.user_selection[r][c] < 2:
            if self.env.turn % 2 == 0:
                if self.player_1.is_cell_value(1, BOARD_ROWS - 1 - r, c):
                    if self.selected == 0:
                        self.user_selection[r][c] = 2
                        self.selected = 2
                else:
                    self.user_selection[r][c] += 1
                    self.selected += 1
            else:
                if self.player_2.is_cell_value(1, r, c):
                    if self.selected == 0:
                        self.user_selection[r][c] = 2
                        self.selected = 2
                else:
                    self.user_selection[r][c] += 1
                    self.selected += 1

        self.confirm = (self.selected == 2)
        self.reset = (self.selected > 0)

    def __reset_selection(self):
        self.user_selection = [[0 for c in range(BOARD_ROWS)] for r in range(BOARD_COLUMNS)]
        self.selected = 0
        self.confirm = False
        self.reset = False

    def __confirm_selection(self):
        vrc = []
        # If the first player is playing: Take the flipped board into account
        if self.env.turn % 2 == 0:
            for r in range(BOARD_ROWS):
                for c in range(BOARD_COLUMNS):
                    value = self.user_selection[r][c]
                    if value != 0:
                        vrc.append([value, (BOARD_ROWS - r - 1), c])
        else:
            for r in range(BOARD_ROWS):
                for c in range(BOARD_COLUMNS):
                    value = self.user_selection[r][c]
                    if value != 0:
                        vrc.append([value, r, c])

        action = hf.vrc_to_action(vrc)
        observation, reward, self.done, info = self.env.step(action)
        self.__reset_selection()

    def gameplay(self):
        self.player_1 = self.env.p1
        self.player_2 = self.env.p2
        self.env.reset()
        self.render()
        while not self.done:

            p1_board = self.player_1.get_board()[::-1]
            p2_board = self.player_2.get_board()

            for row in p2_board:
                print(row)
            print('\n')
            for row in p1_board:
                print(row)
            print("-----------------------------------------------------------------------------------------")

            if G.new_input:
                user_input = G.get_input()
                if user_input == 'stop':
                    self.done = True

            self.datetime = datetime.datetime.now()
            if self.env.turn % 2 == 0:
                if self.p1_type == USER:
                    self.user_input()
                else:
                    action, reward, action_branch = self.env.p1_bot.get_best_move(self.player_1, self.player_2)
                    observation, current_reward, self.done, info = self.env.step(action)
                    print('[', self.env.turn,
                          "]\n", self.player_1.player_id, "(", self.player_1.hp, ") Played:", action, "evaluation:",
                          str(round(reward, 2)), "threatening", len(self.player_1.threatened_attacks), "attacks.", action_branch)
                if self.player_1_time is None:
                    self.player_1_time = (datetime.datetime.now() - self.datetime)
                else:
                    self.player_1_time += (datetime.datetime.now() - self.datetime)
            else:
                if self.p2_type == USER:
                    self.user_input()
                else:
                    action, reward, action_branch = self.env.p2_bot.get_best_move(self.player_2, self.player_1)
                    observation, current_reward, self.done, info = self.env.step(action)
                    print('[', self.env.turn,
                          "]\n", self.player_2.player_id, "(", self.player_2.hp, ") Played:", action, "evaluation:",
                          str(round(reward, 2)), "threatening", len(self.player_2.threatened_attacks), "attacks.", action_branch)
                if self.player_2_time is None:
                    self.player_2_time = (datetime.datetime.now() - self.datetime)
                else:
                    self.player_2_time += (datetime.datetime.now() - self.datetime)

            self.render()
            pygame.display.update()
            self.clock.tick(60)

        print("Game finished in:", self.env.turn, "Turns")
        self.stage = 'review'

    def review(self):
        max_turns = self.env.get_saved_game().turns
        viewed_turn = self.env.turn
        while not self.done:
            self.player_1, self.player_2 = self.env.get_saved_game().get_players(viewed_turn)
            self.render()

            if G.new_input:
                user_input = G.get_input()
                if user_input == 'left':
                    if viewed_turn > 0:
                        viewed_turn -= 1
                elif user_input == 'right':
                    if viewed_turn < max_turns:
                        viewed_turn += 1
                elif user_input == 'reset':
                    viewed_turn = 0
                elif user_input == 'pruned':
                    p1 = self.player_1.get_copy()
                    for action in p1.prune_set:
                        vrc = hf.action_to_vrc(action)
                        for element in vrc:
                            p1.__place_piece(element[1], element[2], element[0])
                else:
                    args = user_input.split()
                    if args[0] == 'test':
                        if args[1] == '1':
                            bot = self.env.p1_bot
                            if len(args) == 5:
                                vrc = [[int(args[2]), int(args[3]) - 1, int(args[4]) - 1]]
                                reward, action_branch = bot.evaluate_move(self.player_1, self.player_2, vrc)
                                print("estimated reward:", reward, action_branch)
                            elif len(args) == 8:
                                vrc = [[int(args[2]), int(args[3]) - 1, int(args[4]) - 1],
                                       [int(args[5]), int(args[6]) - 1, int(args[7]) - 1]]
                                reward, action_branch = bot.evaluate_move(self.player_1, self.player_2, vrc)
                                print("estimated reward:", reward, action_branch)
                            else:
                                print("Wrong number of total arguments, expected 4 or 7")

                        elif args[1] == '2':
                            bot = self.env.p2_bot
                            if len(args) == 5:
                                vrc = [[int(args[2]), int(args[3]) - 1, int(args[4]) - 1]]
                                reward, action_branch = bot.evaluate_move(self.player_2, self.player_1, vrc)
                                print("estimated reward:", reward, action_branch)
                            elif len(args) == 8:
                                vrc = [[int(args[2]), int(args[3]) - 1, int(args[4]) - 1],
                                       [int(args[5]), int(args[6]) - 1, int(args[7]) - 1]]
                                reward, action_branch = bot.evaluate_move(self.player_2, self.player_1, vrc)
                                print("estimated reward:", reward, action_branch)
                            else:
                                print("Wrong number of total arguments, expected 4 or 7")
                        else:
                            print("Selected wrong player, options are 1 and 2")
                    else:
                        print("Input incorrect, received:", user_input)

            ev = pygame.event.get()
            for event in ev:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        if viewed_turn > 0:
                            viewed_turn -= 1
                    if event.key == pygame.K_RIGHT:
                        if viewed_turn < max_turns:
                            viewed_turn += 1
                    if event.key == pygame.K_ESCAPE:
                        self.done = True

            self.render()
            pygame.display.update()
            self.clock.tick(60)

    def start(self):
        self.done = False
        if self.stage == 'play':
            self.gameplay()
            self.done = False
            self.stage = 'review'

        if self.stage == 'review':
            self.review()

        self.env.close()
        pygame.quit()

    def user_input(self):
        responded = False
        while not responded:
            ev = pygame.event.get()
            for event in ev:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_position = pygame.mouse.get_pos()

                    if self.confirm:
                        if CONFIRM_X_OFFSET <= mouse_position[0] <= CONFIRM_X_OFFSET + CONFIRM_WIDTH \
                                and CONFIRM_Y_OFFSET <= mouse_position[1] <= CONFIRM_Y_OFFSET + CONFIRM_HEIGHT:
                            self.__confirm_selection()
                            responded = True

                    if self.reset:
                        if RESET_X_OFFSET <= mouse_position[0] <= RESET_X_OFFSET + RESET_WIDTH and RESET_Y_OFFSET <= \
                                mouse_position[1] <= RESET_Y_OFFSET + RESET_HEIGHT:
                            self.__reset_selection()

                    valid, row, column = self.handlemouseclick(mouse_position)
                    if valid:
                        self.__make_selection(int(row), int(column))

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        responded = True
                        self.done = True

            self.render()
            pygame.display.update()
            self.clock.tick(60)

    def handlemouseclick(self, pos):
        if pos[0] < self.max_x_pos and pos[1] < self.max_y_pos and self.env.turn % 2 == 1:
            row, column = mouseposition_to_rowcolumn(pos[0], pos[1])
            return True, row, column
        elif pos[0] < self.max_x_pos and DEFENDER_BOARD_OFFSET < pos[1] < self.max_y_pos + DEFENDER_BOARD_OFFSET and \
                self.env.turn % 2 == 0:
            row, column = mouseposition_to_rowcolumn(pos[0], pos[1] - DEFENDER_BOARD_OFFSET)
            return True, row, column
        else:
            return False, None, None

    def render(self):
        p1_board = self.player_1.get_board()[::-1]
        p2_board = self.player_2.get_board()

        mouse_location = pygame.mouse.get_pos()

        if self.env.turn % 2 == 0:
            row, column = mouseposition_to_rowcolumn(mouse_location[0], mouse_location[1] - DEFENDER_BOARD_OFFSET)
            if self.p1_type == USER:
                for r in range(BOARD_ROWS):
                    for c in range(BOARD_COLUMNS):
                        if self.user_selection[r][c] != 0:
                            p1_board[r][c] = self.user_selection[r][c]
                        if row == r and c == column and self.selected < 2:
                            p1_board[r][c] = min(2, p1_board[r][c] + 1)
        else:
            row, column = mouseposition_to_rowcolumn(mouse_location[0], mouse_location[1])
            if self.p2_type == USER:
                for r in range(BOARD_ROWS):
                    for c in range(BOARD_COLUMNS):
                        if self.user_selection[r][c] != 0:
                            p2_board[r][c] = self.user_selection[r][c]
                        if row == r and c == column and self.selected < 2:
                            p2_board[r][c] = min(2, p2_board[r][c] + 1)

        self.display.fill(BLACK)

        self.draw_grid(p2_board, 0, 0, LIGHT_GREY, 1)
        self.draw_grid(p1_board, DEFENDER_BOARD_OFFSET, 0, DARK_GREY, 2)

        self.GAME_FONT.render_to(self.display, (BOX_MARGIN + BOARD_COLUMNS * (BOX_MARGIN + BOX_WIDTH), BOX_MARGIN),
                                 "hitpoints: " + str(self.player_2.hp), WHITE)
        self.GAME_FONT.render_to(self.display, (BOX_MARGIN + BOARD_COLUMNS * (BOX_MARGIN + BOX_WIDTH), BOX_MARGIN + 40),
                                 "time spend: " + str(self.player_2_time), WHITE)
        self.GAME_FONT.render_to(self.display,
                                 (BOX_MARGIN + BOARD_COLUMNS * (BOX_MARGIN + BOX_WIDTH), DEFENDER_BOARD_OFFSET + BOX_MARGIN),
                                 "hitpoints: " + str(self.player_1.hp), WHITE)
        self.GAME_FONT.render_to(self.display,
                                 (BOX_MARGIN + BOARD_COLUMNS * (BOX_MARGIN + BOX_WIDTH), DEFENDER_BOARD_OFFSET + BOX_MARGIN + 40),
                                 "time spend: " + str(self.player_1_time), WHITE)

        if self.reset:
            reset = pygame.Rect(RESET_X_OFFSET, RESET_Y_OFFSET, RESET_WIDTH, RESET_HEIGHT)
            pygame.draw.rect(self.display, RESET_COLOR, reset, 0)
            self.GAME_FONT.render_to(self.display,
                                     (RESET_X_OFFSET, RESET_Y_OFFSET),
                                     "Reset", BLACK)

        if self.confirm:
            confirm = pygame.Rect(CONFIRM_X_OFFSET, CONFIRM_Y_OFFSET, CONFIRM_WIDTH, CONFIRM_HEIGHT)
            pygame.draw.rect(self.display, CONFIRM_COLOR, confirm, 0)
            self.GAME_FONT.render_to(self.display,
                                     (CONFIRM_X_OFFSET, CONFIRM_Y_OFFSET),
                                     "Confirm", BLACK)

    def draw_grid(self, board, init_y, init_x, color, player):
        for column in range(BOARD_COLUMNS):
            for row in range(BOARD_ROWS):
                x_coordinate = init_x + BOX_MARGIN + column * (BOX_MARGIN + BOX_WIDTH)
                y_coordinate = init_y + BOX_MARGIN + row * (BOX_MARGIN + BOX_HEIGHT)
                rect = pygame.Rect(x_coordinate, y_coordinate,
                                        BOX_WIDTH, BOX_HEIGHT)
                pygame.draw.rect(self.display, color, rect, 0)
                if board[row][column] == 2:
                    if player == 1:
                        self.display.blit(red_img, (x_coordinate, y_coordinate))
                    else:
                        self.display.blit(blue_img, (x_coordinate, y_coordinate))
                elif board[row][column] == 1:
                    self.display.blit(dead_img, (x_coordinate, y_coordinate))


G = CommandLineInput()
G.lock = Lock()


def run():
    game = Game(USER, USER)
    game.start()


t = Thread(target=run, args=())
t.start()

G.ask_input()
