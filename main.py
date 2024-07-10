import montecarlo
import numpy as np
import game
import nestedai
import simpleai
from time import time
from copy import deepcopy



def full_auto_game():
    deck = game.generate_deck()
    hands, pile = game.deal_hands(deck, game.params["nb_players"])
    families_scored = np.full((game.params["nb_families"], game.params["nb_players"]), -1)
    # Row = family, Column 0 = player who scored, Column 1 = order it was scored in

    card_tracker = np.full((game.params["nb_families"], game.params["nb_people_per_family"]), -1)
    
    turn = 0
    max_turns = 10e6
    while turn < max_turns:
        player = turn % game.params["nb_players"]

        lucky = True
        print("Player", player, "playing")
        while lucky:
            print("Your hand :", hands[player])

            chosen_move = nestedai.choose_move(hands, player, families_scored, card_tracker, True)
            lucky, hands, pile = game.ask(hands, pile, player, chosen = chosen_move, verbose=True)

            hands, families_scored = game.is_family_scored(hands, families_scored, card_tracker, True)

            if len(hands[player]) == 0:
                break #Player has no cards, he can't play

            if lucky : 
                print("Player", player, "got lucky and can play again\n")
                card_tracker[chosen_move[1], chosen_move[2]] = player

        print("Turn over\n")

        turn += 1

        if game.is_game_over(hands) :
            score = game.compute_scores(families_scored)
            print("Score :",score)
            print("Game lasted", turn+1, "turns")
            return score
    
    print('Game over because too long')
    return game.compute_scores(families_scored)


def play_vs_ai():
    deck = game.generate_deck()
    hands, pile = game.deal_hands(deck, 2)
    families_scored = np.full((game.params["nb_families"], game.params["nb_players"]), -1)
    # Row = family, Column 0 = player who scored, Column 1 = order it was scored in

    card_tracker = np.full((game.params["nb_families"], game.params["nb_people_per_family"]), -1)
    
    turn = 0
    max_turns = 10e6
    while turn < max_turns:
        player = turn % game.params["nb_players"]
        
        print("\nPlayer", player, "playing")
        lucky = True

        if player == 0:
            while lucky:
                chosen_move = game.ask_human(hands, player)
                lucky, hands, pile = game.ask(hands, pile, player, chosen = chosen_move, verbose=True)

                hands, families_scored = game.is_family_scored(hands, families_scored, card_tracker, True)

                if len(hands[player]) == 0:
                    break #Player has no cards, he can't play

                if lucky : 
                    card_tracker[chosen_move[1], chosen_move[2]] = player
                    print("Player", player, "got lucky and can play again\n")
            
            print("Hand after draw :")
            game.present_hand(hands, player)

        else:
            while lucky:
                chosen_move = nestedai.choose_move(hands, player, families_scored, card_tracker, verbose = True)
                lucky, hands, pile = game.ask(hands, pile, player, chosen = chosen_move, verbose=True)

                hands, families_scored = game.is_family_scored(hands, families_scored, card_tracker, True)

                if len(hands[player]) == 0:
                    break #Player has no cards, he can't play

                if lucky : 
                    card_tracker[chosen_move[1], chosen_move[2]] = player
                    print("Player", player, "got lucky and can play again\n")

        turn += 1
        print("Turn over")

        if game.is_game_over(hands) :
            score = game.compute_scores(families_scored)
            print("Game over !\nScore :",score)
            return score
    
    print('Game over because too long')
    return game.compute_scores(families_scored)

def time_tests():
    deck = game.generate_deck()
    hands, pile = game.deal_hands(deck, 2)
    families_scored = np.full((game.params["nb_families"],2), -1)

    starttime = time()
    for _ in range(25):
        _ = deepcopy(hands)
    print("Time for 25 deep copies :", time() - starttime)


def main():
    full_auto_game()


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
            move = simpleai.choose_move(hands, 1-player, families_scored, True)
            print("Suggested move :", move)
        
        if game.is_game_over(hands) :
            score = game.compute_scores(families_scored)

            return print("actual score :",score)
            
    if verbose : print('Game over because too long')
    return game.compute_scores(families_scored)

main()