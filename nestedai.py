import game, montecarlo, numpy as np, time, copy, simpleai

def choose_move(original_hands, player_number, original_families_scored, original_card_tracker, verbose = True):
    starttime = time.time()

    static_hands = copy.deepcopy(original_hands)
    static_families_scored = original_families_scored.copy()

    moves = simpleai.enumerate_moves(static_hands, player_number)

    assumed_hands, assumed_pile = montecarlo.assume_game_state(player_number, static_hands, static_families_scored, original_card_tracker, verbose=False)

    search_data = np.empty(len(moves))

    for j, move in enumerate(moves):
        card_tracker = original_card_tracker.copy()
        lucky, hands, pile = montecarlo.ask_chosen(copy.deepcopy(assumed_hands), assumed_pile.copy(), player_number, move, verbose=False)

        if lucky: # Has to be before lucky reset check and family score check which modifies card tracker
            card_tracker[move[1], move[2]] = player_number

        hands, families_scored = game.is_family_scored(hands, static_families_scored.copy(), card_tracker)

        if len(hands[player_number]) == 0: lucky = False

        while lucky :
            random_choice = montecarlo.choose_random(hands, player_number)
            lucky, hands, pile = montecarlo.ask_chosen(hands, pile, player_number, random_choice, verbose=False)

            if lucky :
                card_tracker[random_choice[1], random_choice[2]] = player_number

            hands, families_scored = game.is_family_scored(hands, families_scored, card_tracker)

        search_data[j] = simpleai.best_move_value(hands, 1-player_number, families_scored, card_tracker) # Only retrieves score for the player for now

    if verbose :
        print("Evaluated",len(moves),"moves in", time.time() - starttime, "seconds")

    return moves[np.argmin(search_data)] # Simplified UCB