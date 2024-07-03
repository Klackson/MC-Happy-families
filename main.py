import montecarlo
import numpy as np
import game

def main():
    blc(2, True, randomshit=True)


def blc(nb_players, verbose=True, randomshit=True):
    deck = game.generate_deck()
    hands, pile = game.deal_hands(deck, nb_players)
    families_scored = np.full((game.params["nb_families"],2), -1)
    # Row = family, Column 0 = player who scored, Column 1 = order it was scored in
    
    turn = 0
    max_turns = 10e6
    while turn < max_turns:
        player = turn % nb_players
        hands, pile = game.play_turn(hands, pile, player, families_scored)
        turn += 1

        if randomshit :
            montecarlo.play_simulation(player, hands, families_scored, True)

            return
        
        if game.is_game_over(hands) :

            """
            # Find the highest score
            max_score = np.max(families_scored[:,0])
            
            # Find all players with the highest score
            tied_players = np.where(families_scored[:,0] == max_score)[0]
            
            if len(tied_players) > 1:
                # Tiebreak by taking the first to complete a family among tied players
                # Find the player among tied players who completed a family first
                earliest_completion = np.argmin(families_scored[tied_players,1])
                winner = tied_players[earliest_completion]
            else:
                # No tie, winner is the one with the highest score
                winner = tied_players[0]
            
            if verbose : print("Player", winner, "wins!")
            """

            score = game.compute_scores(families_scored)

            return print("actual score :",score)
            
    if verbose : print('Game over because too long')
    return game.compute_scores(families_scored)

main()