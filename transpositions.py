import json
from settings import *

json_file = os.path.join(ROOT_DIR, 'transpositions.json')  # requires `import os`
min_storable_searchdepth = 1
disable_transpositions = False


def hash_gamestate(observation):
    first = ''.join(map(str, observation[0]))
    second = ''.join(map(str, observation[1]))
    first += second
    return first


def load_transpositions():
    file = open(json_file, 'r')
    json_string = file.read()
    file.close()
    transpositions = json.loads(json_string)
    return transpositions


class Transpositions:
    def __init__(self):
        self.trans_dict = load_transpositions()

    def store_to_file(self):
        print("store to file")
        json_string = json.dumps(self.trans_dict)
        file = open(json_file, 'w')
        file.write(json_string)
        file.close()

    def compare_transposition(self, game_hash, reward, action_list, search_depth):
        if disable_transpositions is True:
            return None
        if game_hash in self.trans_dict:
            if self.trans_dict[game_hash][2] >= search_depth:
                return self.trans_dict[game_hash][:2]  # return reward and action_list

        self.trans_dict[game_hash] = [reward, action_list, search_depth]
        return None

    def get_transposition(self, game_hash, search_depth):
        if disable_transpositions is True:
            return None
        if game_hash in self.trans_dict:
            if self.trans_dict[game_hash][2] > search_depth:
                return self.trans_dict[game_hash][:2]  # return reward and action_list

        return None

    def store_transposition(self, game_hash, reward, action_list, search_depth):
        if search_depth >= min_storable_searchdepth:
            self.trans_dict[game_hash] = [reward, action_list, search_depth]


empty_transpositions = dict()
json_string = json.dumps(empty_transpositions)
file = open(json_file, 'w')
file.write(json_string)
file.close()