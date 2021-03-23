
# class which is used to store the gamestate after each move and the corresponding turn. the get_players method can
# then be used to playback the game.
class SaveGame:
    def __init__(self, p1, p2):
        self.turns = 0
        self.p1_statelist = [p1.get_copy()]
        self.p2_statelist = [p2.get_copy()]

    def store(self, p1, p2):
        self.turns += 1
        self.p1_statelist.append(p1.get_copy())
        self.p2_statelist.append(p2.get_copy())

    def get_players(self, turn):
        return self.p1_statelist[turn], self.p2_statelist[turn]