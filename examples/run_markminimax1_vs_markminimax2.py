from pygame_play import *

G = CommandLineInput()
G.lock = Lock()


def run():
    game = Game(MARK_MINIMAX_1, MARK_MINIMAX_2)
    game.start()

t = Thread(target=run, args=())
t.start()

G.ask_input()