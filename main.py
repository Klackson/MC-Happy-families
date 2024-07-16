import montecarlo
import numpy as np
import game
import nestedai
import simpleai
from time import time
from copy import deepcopy

def time_tests():
    deck = game.generate_deck()
    hands, pile = game.deal_hands(deck, 2)
    families_scored = np.full((game.params["nb_families"],2), -1)

    starttime = time()
    for _ in range(25):
        _ = deepcopy(hands)
    print("Time for 25 deep copies :", time() - starttime)


def main():
    partie = game.game(["nestedai", "simpleai"], game.params["nb_families"], game.params["nb_people_per_family"], game.params["starting_hand_size"], verbose=True)

    partie.play_game()

main()