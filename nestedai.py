import game, montecarlo, numpy as np, time, copy, simpleai

params={"nb_total_simulations":20,
        "nb_worlds":2
        }

params["nb_nested_simulations"] = params["nb_total_simulations"] // params["nb_worlds"]

def choose_move(instance , player_number, verbose = False):
    starttime = time.time()

    moves = simpleai.enumerate_moves(instance, player_number)

    search_data = np.empty((params["nb_worlds"], len(moves)))

    for i in range(params["nb_worlds"]):
        assumed_hands, assumed_pile = instance.assume_game_state(player_number)

        for j, move in enumerate(moves):
            re_instance = copy.deepcopy(instance)
            re_instance.hands = copy.deepcopy(assumed_hands)
            re_instance.pile = assumed_pile.copy()
            re_instance.verbose = False
            re_instance.is_family_scored()
            lucky = re_instance.ask(player_number, chosen = move)

            re_instance.is_family_scored()

            if len(re_instance.hands[player_number]) == 0: lucky = False

            if re_instance.is_game_over():
                search_data[i,j] = re_instance.compute_scores()[player_number]
                continue

            if lucky :
                search_data[i,j] = best_move_value(re_instance, player_number)
                continue

            search_data[i,j] = best_move_value(re_instance, 1-player_number, True) # Only retrieves score for the player for now

    if verbose :
        print("Evaluated",len(moves),"moves in", time.time() - starttime, "seconds")

    mean_scores = np.mean(search_data, axis=0)

    return moves[np.argmax(mean_scores)]


def best_move_value(instance , player_number, return_opponent = False):
    moves = simpleai.enumerate_moves(instance, player_number)

    search_data = np.empty((params["nb_nested_simulations"], len(moves)))

    for i in range(params["nb_nested_simulations"]):
        assumed_hands, assumed_pile = instance.assume_game_state(player_number)
        
        for j, move in enumerate(moves):
            simulation = montecarlo.simulation(copy.deepcopy(assumed_hands), copy.deepcopy(assumed_pile), instance.families_scored.copy())
            lucky = simulation.ask_chosen(player_number, move)

            if return_opponent:
                search_data[i,j] = simulation.playout(player_number, lucky)[1-player_number]
            else:
                search_data[i,j] = simulation.playout(player_number, lucky)[player_number] 

    mean_scores = np.mean(search_data, axis=0)

    if return_opponent:
        return np.min(mean_scores)

    return np.max(mean_scores) # Simplified UCB