from gui import *

G = CommandLineInput()
G.lock = Lock()


def run():
    game = Game(MARK_MINIMAX_2, USER)
    game.start()

t = Thread(target=run, args=())
t.start()

G.ask_input()