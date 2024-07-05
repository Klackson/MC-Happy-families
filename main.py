import montecarlo
import numpy as np
import game
import simpleai

def full_auto_game(nb_players):
    deck = game.generate_deck()
    hands, pile = game.deal_hands(deck, nb_players)
    families_scored = np.full((game.params["nb_families"],2), -1)
    # Row = family, Column 0 = player who scored, Column 1 = order it was scored in
    
    turn = 0
    max_turns = 10e6
    while turn < max_turns:
        player = turn % nb_players

        lucky = True
        print("Player", player, "playing")
        while lucky:
            print("Your hand :", hands[player])

            chosen_move = simpleai.choose_move(hands, player, families_scored, False)
            lucky, hands, pile = game.ask(hands, pile, player, chosen = chosen_move, verbose=True)

            hands, families_scored = game.is_family_scored(hands, families_scored)

            if len(hands[player]) == 0:
                break #Player has no cards, he can't play

            if lucky : print("Player", player, "got lucky and can play again\n")

        print("Turn over\n")

        turn += 1

        if game.is_game_over(hands) :
            score = game.compute_scores(families_scored)
            print("Score :",score)
            return score
    
    print('Game over because too long')
    return game.compute_scores(families_scored)



def main():
    full_auto_game(2)


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
            move = simpleai.choose_move(hands, 1-player, families_scored, False)
            print("Suggested move :", move)
        
        if game.is_game_over(hands) :
            score = game.compute_scores(families_scored)

            return print("actual score :",score)
            
    if verbose : print('Game over because too long')
    return game.compute_scores(families_scored)

main()