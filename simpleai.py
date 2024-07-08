import numpy as np
import game
import montecarlo
import copy
import time

params = {"nb_simulations": 100}

def enumerate_moves(hands, player_number):
    moves = []

    hand = hands[player_number]

    families_in_hand = np.unique([card[0] for card in hand])

    for family in families_in_hand:

        for person in range(game.params["nb_people_per_family"]):
            if [family, person] not in hand:
                    for enemy_player in range(len(hands)):
                        if enemy_player == player_number: continue
                        moves.append((enemy_player, family, person))

    return moves


def choose_move(original_hands, player_number, original_families_scored, card_tracker, verbose = True):
    starttime = time.time()

    static_hands = copy.deepcopy(original_hands)
    static_families_scored = original_families_scored.copy()

    moves = enumerate_moves(static_hands, player_number)

    search_data = np.empty((params["nb_simulations"], len(moves)))
    opponent_data = np.empty((params["nb_simulations"], len(moves)))

    for i in range(params["nb_simulations"]):
        assumed_hands, assumed_pile = montecarlo.assume_game_state(player_number, static_hands, static_families_scored, card_tracker, verbose=False)

        for j, move in enumerate(moves):
            lucky, hands, pile = montecarlo.ask_chosen(copy.deepcopy(assumed_hands), assumed_pile.copy(), player_number, move, verbose=False)
            hands, families_scored = game.is_family_scored(hands, static_families_scored.copy())

            if len(hands[player_number]) == 0: lucky = False

            search_data[i,j] = montecarlo.play_simulation(player_number, hands, pile, families_scored, lucky, verbose=False)[player_number] # Only retrieves score for the player for now
            opponent_data[i,j] = montecarlo.play_simulation(player_number, hands, pile, families_scored, lucky, verbose=False)[1 - player_number]


    mean_scores = np.mean(search_data, axis=0)

    if verbose : 
        print("Mean scores :", mean_scores)
        print("Opponent scores :", np.mean(opponent_data, axis=0))

    print("Runtime :", time.time() - starttime)

    return moves[np.argmax(mean_scores)] # Simplified UCB