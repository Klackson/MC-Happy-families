import numpy as np
import game
import montecarlo
import copy
import time

params = {"nb_simulations": 100,
          "nb_nested_simulations" : 50}

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

    for i in range(params["nb_simulations"]):
        assumed_hands, assumed_pile = montecarlo.assume_game_state(player_number, static_hands, static_families_scored, card_tracker, verbose=False)

        for j, move in enumerate(moves):
            lucky, hands, pile = game.ask(copy.deepcopy(assumed_hands), assumed_pile.copy(), player_number, chosen = move, verbose=False)
            hands, families_scored = game.is_family_scored(hands, static_families_scored.copy())

            if len(hands[player_number]) == 0: lucky = False

            search_data[i,j] = montecarlo.play_simulation(player_number, hands, pile, families_scored, lucky, verbose=False)[player_number] # Only retrieves score for the player for now

    mean_scores = np.mean(search_data, axis=0)

    if verbose : print("Runtime :", time.time() - starttime)

    return moves[np.argmax(mean_scores)] # Simplified UCB

def play_turn(hands, pile, player, families_scored, card_tracker, verbose = False):
    lucky=True
    while lucky:
        chosen_move = choose_move(hands, player, families_scored, card_tracker, verbose = verbose)
        lucky, hands, pile = game.ask(hands, pile, player, chosen = chosen_move, verbose = verbose)

        hands, families_scored = game.is_family_scored(hands, families_scored, card_tracker, verbose)

        if len(hands[player]) == 0:
            break #Player has no cards, he can't play

        if lucky : 
            card_tracker[chosen_move[1], chosen_move[2]] = player
            if verbose : print("Player", player, "got lucky and can play again\n")