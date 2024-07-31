import montecarlo
import numpy as np
import game
import nestedai
import simpleai
from time import time
from copy import deepcopy

from pathlib import Path
import msvcrt
import os


def time_tests():
    deck = game.generate_deck()
    hands, pile = game.deal_hands(deck, 2)
    families_scored = np.full((game.params["nb_families"],2), -1)

    starttime = time()
    for _ in range(25):
        _ = deepcopy(hands)
    print("Time for 25 deep copies :", time() - starttime)


def write_to_file(filename, text):
    with open(filename, "a") as f:
        # Lock the file
        msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)
        try:
            f.write((text+"\n"))
        finally:
            # Unlock the file
            msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
    

def record_matches(nb_matches, filename, players):
    for i in range(nb_matches):
        partie = game.game(players, game.params["nb_families"], game.params["nb_people_per_family"], game.params["starting_hand_size"], verbose=False)
        score = partie.play_game()

        write_to_file(filename, f"{score[0]},{score[1]}")
        print(f"Match {i+1} recorded")

def one_hundred_games(players):
    script_dir = os.path.dirname(__file__)
    file_path = os.path.join(script_dir, f"{players[0]}_vs_{players[1]}.txt")

    record_matches(100, file_path, players)


def one_v_one(players):
    partie = game.game(players, game.params["nb_families"], game.params["nb_people_per_family"], game.params["starting_hand_size"], verbose=True)

    partie.play_game()

def main():
    players = ["pimc", "pimc"]
    one_hundred_games(players)

main()