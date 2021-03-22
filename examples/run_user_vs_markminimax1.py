from pygame_play import *

G = CommandLineInput()
G.lock = Lock()


def run():
    game = Game(USER, MARK_MINIMAX_1)
    game.start()

t = Thread(target=run, args=())
t.start()

G.ask_input()