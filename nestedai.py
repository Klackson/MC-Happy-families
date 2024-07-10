import game, montecarlo, numpy as np, time, copy, simpleai

params={"nb_total_simulations":50,
        "nb_worlds":2
        }

params["nb_nested_simulations"] = params["nb_total_simulations"] // params["nb_worlds"]

def choose_move(original_hands, player_number, original_families_scored, original_card_tracker, verbose = True):
    starttime = time.time()

    static_hands = copy.deepcopy(original_hands)
    static_families_scored = original_families_scored.copy()

    moves = simpleai.enumerate_moves(static_hands, player_number)

    search_data = np.empty((params["nb_worlds"], len(moves)))

    for i in range(params["nb_worlds"]):
        assumed_hands, assumed_pile = montecarlo.assume_game_state(player_number, static_hands, static_families_scored, original_card_tracker, verbose=False)

        for j, move in enumerate(moves):
            card_tracker = original_card_tracker.copy()
            lucky, hands, pile = game.ask(copy.deepcopy(assumed_hands), assumed_pile.copy(), player_number, chosen = move, verbose=False)

            if lucky: # Has to be before lucky reset check and family score check which modifies card tracker
                card_tracker[move[1], move[2]] = player_number

            hands, families_scored = game.is_family_scored(hands, static_families_scored.copy(), card_tracker)

            if len(hands[player_number]) == 0: lucky = False

            if lucky :
                search_data[i,j] = best_move_value(hands, player_number, families_scored, card_tracker)
                continue

            search_data[i,j] = best_move_value(hands, 1-player_number, families_scored, card_tracker, True) # Only retrieves score for the player for now

    if verbose :
        print("Evaluated",len(moves),"moves in", time.time() - starttime, "seconds")

    mean_scores = np.mean(search_data, axis=0)

    return moves[np.argmax(mean_scores)]


def best_move_value(original_hands, player_number, original_families_scored, card_tracker, return_opponent = False):
    static_hands = copy.deepcopy(original_hands)
    static_families_scored = original_families_scored.copy()

    moves = simpleai.enumerate_moves(static_hands, player_number)

    search_data = np.empty((params["nb_nested_simulations"], len(moves)))

    for i in range(params["nb_nested_simulations"]):
        assumed_hands, assumed_pile = montecarlo.assume_game_state(player_number, static_hands, static_families_scored, card_tracker, verbose=False)

        for j, move in enumerate(moves):
            lucky, hands, pile = game.ask(copy.deepcopy(assumed_hands), assumed_pile.copy(), player_number, chosen = move, verbose=False)
            hands, families_scored = game.is_family_scored(hands, static_families_scored.copy())

            if len(hands[player_number]) == 0: lucky = False

            starttime= time.time()
            if return_opponent:
                search_data[i,j] = montecarlo.play_simulation(player_number, hands, pile, families_scored, lucky, verbose=False)[1-player_number]

            else :
                search_data[i,j] = montecarlo.play_simulation(player_number, hands, pile, families_scored, lucky, verbose=False)[player_number]
            #print("Simulation",i*len(moves)+j,"runtime :",time.time()-starttime,"seconds")

    mean_scores = np.mean(search_data, axis=0)

    if return_opponent:
        return np.min(mean_scores)
    
    return np.max(mean_scores)