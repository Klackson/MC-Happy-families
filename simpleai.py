import numpy as np
import montecarlo
import copy
import time

params = {"nb_simulations": 100,
          "nb_nested_simulations" : 50}

def enumerate_moves(instance, player_number):
    moves = []

    hand = instance.hands[player_number]

    families_in_hand = np.unique([card[0] for card in hand])

    for family in families_in_hand:

        for person in range(instance.nb_people_per_family):
            if [family, person] not in hand:
                    for enemy_player in range(len(instance.hands)):
                        if enemy_player == player_number: continue
                        moves.append((enemy_player, family, person))

    return moves


def choose_move(instance , player_number, verbose = True):
    starttime = time.time()

    moves = enumerate_moves(instance, player_number)

    search_data = np.empty((params["nb_simulations"], len(moves)))

    for i in range(params["nb_simulations"]):
        assumed_hands, assumed_pile = instance.assume_game_state(player_number)
        
        for j, move in enumerate(moves):
            simulation = montecarlo.simulation(copy.deepcopy(assumed_hands), copy.deepcopy(assumed_pile), instance.families_scored.copy())
            lucky = simulation.ask_chosen(player_number, move)

            search_data[i,j] = simulation.playout(player_number, lucky)[player_number] # Only retrieves score for the player for now

    mean_scores = np.mean(search_data, axis=0)

    if verbose : print("Runtime :", time.time() - starttime)

    return moves[np.argmax(mean_scores)] # Simplified UCB