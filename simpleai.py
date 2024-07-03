import numpy as np
import game
import montecarlo

def enumerate_moves(hands, player_number):
    moves = []
    for i in range(len(hands)):
        if i == player_number: continue
        hand = hands[i]
        
        for family in np.unique([card[0] for card in hand]):
            for person in range(game.params["nb_people_per_family"]):
                if [family, person] not in hand:
                    moves.append((i, family, person))
    return moves

def montecarlosearch(hands, player_number, families_scored, verbose = True):
    moves = enumerate_moves(hands, player_number) # Enumerate all possible moves

    #TODO
    #Guess a lot of possible states
    hands, pile = montecarlo.assume_game_state(player_number, hands, families_scored, verbose)
    
    #For each state, play a move and run a simulation

    #Get aggregate scores for all moves

    # Choose the best move

def choose_move(hands, player_number):
    pass