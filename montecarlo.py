import numpy as np
import game
from copy import deepcopy

params = {"selection_method" : "greedy"} # Can be "uniform", "weighted" or "greedy

VERBOSE = False

def assume_game_state(player_number, hands, families_scored, card_tracker, verbose=VERBOSE):
    deck = build_remaining_deck(hands, families_scored, player_number, card_tracker, verbose)

    hands, pile = deal_other_hands(player_number, deck, hands, card_tracker)

    return hands, pile

def build_remaining_deck(hands, families_scored, player_number, card_tracker, verbose = VERBOSE):
    deck = []

    for family in range(game.params["nb_families"]):
        if families_scored[family,0] != -1: continue # Family already scored
        for person in range(game.params["nb_people_per_family"]):
            card = [family, person]
            if card in hands[player_number] or card_tracker[family, person] != -1: continue # Card already in hand or position known
            deck.append(card)

    np.random.shuffle(deck)
    if verbose : print("Deck size :", len(deck))
    return deck

def deal_other_hands(player_number, deck, hands, card_tracker):
    newhands = [[] for _ in range(len(hands))]

    # First add known cards to hands
    nbfam, nbppl = card_tracker.shape
    for family in range(nbfam):
        for person in range(nbppl):
            owner = card_tracker[family, person]
            if owner > -1:
                newhands[owner].append([family, person])


    for i, hand in enumerate(hands):
        if i == player_number:
            newhands[player_number] = hands[player_number].copy()
            continue
        
        for _ in range(len(hand) - len(newhands[i])): #Known hand size minus nb of known cards affected to hand
            card = deck.pop()
            newhands[i].append(card)
    
    return newhands, deck # Deck is the pile since dealt cards have been popped from it


def choose_random(hands, player_number):
    other_players = [i for i in range(len(hands)) if i != player_number]
    asked_player = np.random.choice(other_players)

    families_in_hand = [card[0] for card in hands[player_number]]
    if params["selection_method"]=="weighted": asked_family = np.random.choice(families_in_hand)
    elif params["selection_method"]=="uniform": asked_family = np.random.choice(np.unique(families_in_hand))
    elif params["selection_method"]=="greedy": 
        unique, counts = np.unique(families_in_hand, return_counts=True)
        if not len(counts):
            print("counts :",counts)
            print("hand :",hands[player_number])
            print("families in hand",families_in_hand)
        index = np.argmax(counts)
        asked_family = unique[index]
    else :
        raise ValueError("Invalid selection method")
    
    # card_range = np.arange(game.params["nb_people_per_family"])
    # owned_family_cards = [card[1] for card in hands[player_number] if card[0] == asked_family]
    unowned_family_cards = [i for i in range(game.params["nb_people_per_family"]) if [asked_family, i] not in hands[player_number]] # can be made faster
    #unowned_family_cards = np.setdiff1d(card_range, owned_family_cards) 
    # We could also take a completely random card (possibly owned). Try to see speed/accuracy tradeoff

    if not len(unowned_family_cards): 
        raise ValueError("Empty card list, should not happen")
        print("families in hand :", families_in_hand)
        print("chosen family :", asked_family)
        print("player hand :", hands[player_number])
        print("Hand after score check :", game.is_family_scored(hands, np.full((game.params["nb_families"], game.params["nb_players"]), -1), card_tracker=None, verbose=False)[0][player_number])
        raise ValueError("Empty card list, should not happen")
    
    asked_card = np.random.choice(unowned_family_cards)

    return asked_player, asked_family, asked_card


def score_family(hands, family, score_guy, families_scored, hand_counts, verbose = False):
    if verbose : print("Player", score_guy, "scored a family! Family number", family)
    families_scored[family,0] = score_guy
    # families_scored[family,1] = np.sum(families_scored[:,0] != -1)
    hands[score_guy] = [card for card in hands[score_guy] if card[0] != family]
    hand_counts[score_guy, family] = 0


def ask_chosen(hands, pile, player_number, choice, hand_counts, families_scored, verbose=VERBOSE):
    asked_player, asked_family, asked_card = choice

    if verbose : print("Player", player_number, "asks player", asked_player, "for family", asked_family, "and card", asked_card)

    asked_hand = hands[asked_player]
    if [asked_family, asked_card] in asked_hand:
        if verbose : print("Player", asked_player, "gives", asked_family, asked_card, "to player", player_number)
        
        hands[asked_player].remove([asked_family, asked_card])
        hand_counts[asked_player, asked_family] -= 1

        if hand_counts[player_number, asked_family] +1 == game.params["nb_people_per_family"]:
            score_family(hands, asked_family, player_number, families_scored, hand_counts, verbose)
        else :
            hands[player_number].append([asked_family, asked_card])
            hand_counts[player_number, asked_family] += 1

        return True, hands, pile
    
    elif len(pile):
        if verbose : print("Player", asked_player, "says 'Go Fish!'")
        card = pile.pop()
        
        if hand_counts[player_number, card[0]] + 1 == game.params["nb_people_per_family"]:
            score_family(hands, asked_family, player_number, families_scored, hand_counts, verbose)
        else :
            hand_counts[player_number, card[0]] += 1
            hands[player_number].append(card)

        return (card[0] == asked_family and card[1] == asked_card), hands, pile

    return False, hands, pile


def ask_random(hands, pile, player_number, hand_counts, families_scored, verbose=VERBOSE):
    choice = choose_random(hands, player_number)

    return ask_chosen(hands, pile, player_number, choice, hand_counts, families_scored, verbose)

def play_simulation_turn(hands, pile, player_number, families_scored, hand_counts, verbose=VERBOSE):
    if len(hands[player_number]) == 0:
            return hands, pile #Player has no cards, he can't play
    
    lucky = True
    while lucky:
        if verbose : print("Your hand :", hands[player_number],"\n")

        lucky, hands, pile = ask_random(hands, pile, player_number, hand_counts, families_scored)

        if len(hands[player_number]) == 0:
            return hands, pile #Player has no cards, he can't play

        if lucky and verbose : print("Player", player_number, "got lucky and can play again")

    return hands, pile


def count_hands(hands):
    hands_count = np.zeros((game.params["nb_players"], game.params["nb_families"]))

    for player, hand in enumerate(hands):
        for card in hand:
            hands_count[player, card[0]] += 1

    return hands_count

def play_simulation(player_number, hands, pile, families_scored, lucky, verbose=VERBOSE):
    maxturns = 10e3
    turn=0

    starting_player = player_number + (not lucky)

    hand_counts = count_hands(hands)

    while not game.is_game_over(hands) and turn < maxturns:
        playing_player = (starting_player + turn) % game.params["nb_players"]
        hands, pile = play_simulation_turn(hands, pile, playing_player, families_scored, hand_counts , verbose=verbose)
        turn+=1

    if turn == maxturns and verbose : print("Game over because too long")

    scores = game.compute_scores(families_scored)

    if verbose : print("Simulation over, scores :", scores)

    return scores