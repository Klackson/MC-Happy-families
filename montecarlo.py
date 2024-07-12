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
            if owner >= 0:
                newhands[owner].append([family, person])


    for i, hand in enumerate(hands):
        if i == player_number:
            newhands[player_number] = hands[player_number].copy()
            continue
        
        nb_added_cards = len(newhands[i])
        for _ in range(len(hand) - nb_added_cards): #Known hand size minus nb of known cards affected to hand
            card = deck.pop()
            newhands[i].append(card)
    
    return newhands, deck # Deck is the pile since dealt cards have been popped from it


def choose_random(hands, hand_counts, player_number):
    other_players = [i for i in range(hand_counts.shape[0]) if i != player_number]
    asked_player = np.random.choice(other_players)

    families_in_hand = [i for i in range(game.params["nb_families"]) if hand_counts[player_number, i]]
    if params["selection_method"]=="weighted": asked_family = np.random.choice(families_in_hand)
    elif params["selection_method"]=="uniform": asked_family = np.random.choice(np.unique(families_in_hand))
    elif params["selection_method"]=="greedy": asked_family = np.argmax(hand_counts[player_number])
    else :
        raise ValueError("Invalid selection method")
    
    unowned_family_cards = [i for i in range(game.params["nb_people_per_family"]) if not hands[player_number, asked_family, i]]

    if not len(unowned_family_cards): 
        print("families in hand :", families_in_hand)
        print("chosen family :", asked_family)
        print("player hand :", hands[player_number])
        print("Hand after score check :", game.is_family_scored(hands, np.full((game.params["nb_families"], game.params["nb_players"]), -1), card_tracker=None, verbose=False)[0][player_number])
        raise ValueError("Empty card list, should not happen")
    
    asked_card = np.random.choice(unowned_family_cards)

    if asked_player == player_number or not np.sum(hands[player_number, asked_family]) or hands[player_number, asked_family, asked_card]:
        raise ValueError("Unvalid choice")

    return asked_player, asked_family, asked_card


def score_family(hands, family, score_guy, families_scored, hand_counts, verbose = False):
    if verbose : print("Player", score_guy, "scored a family! Family number", family)
    families_scored[family,0] = score_guy
    # families_scored[family,1] = np.sum(families_scored[:,0] != -1)
    hands[score_guy, family] = np.zeros(game.params["nb_people_per_family"])
    hand_counts[score_guy, family] = 0


def ask_chosen(hands, pile, player_number, choice, hand_counts, families_scored, verbose=VERBOSE):
    asked_player, asked_family, asked_card = choice

    if verbose : print("Player", player_number, "asks player", asked_player, "for family", asked_family, "and card", asked_card)

    if hands[asked_player, asked_family, asked_card] :
        if verbose : print("Player", asked_player, "gives", asked_family, asked_card, "to player", player_number)
        
        hands[asked_player, asked_family, asked_card] = 0
        hand_counts[asked_player, asked_family] -= 1

        if hand_counts[player_number, asked_family] +1 == game.params["nb_people_per_family"]:
            score_family(hands, asked_family, player_number, families_scored, hand_counts, verbose)
        else :
            hands[player_number, asked_family, asked_card] = 1
            hand_counts[player_number, asked_family] += 1

        return True, hands, pile
    
    elif len(pile):
        if verbose : print("Player", asked_player, "says 'Go Fish!'")
        card = pile.pop()
        
        if hand_counts[player_number, card[0]] + 1 == game.params["nb_people_per_family"]:
            score_family(hands, card[0], player_number, families_scored, hand_counts, verbose)
        else :
            hand_counts[player_number, card[0]] += 1
            hands[player_number, card[0], card[1]] = 1

        return (card[0] == asked_family and card[1] == asked_card), hands, pile

    return False, hands, pile


def ask_random(hands, pile, player_number, hand_counts, families_scored, verbose=VERBOSE):
    choice = choose_random(hands, hand_counts, player_number)

    return ask_chosen(hands, pile, player_number, choice, hand_counts, families_scored, verbose)

def play_simulation_turn(hands, pile, player_number, families_scored, hand_counts, verbose=VERBOSE):
    if np.sum(hands[player_number]) == 0:
            return hands, pile #Player has no cards, he can't play
    
    lucky = True
    while lucky:
        if verbose : print("Your hand :", hands[player_number],"\n")

        lucky, hands, pile = ask_random(hands, pile, player_number, hand_counts, families_scored)

        if not np.sum(hands[player_number]):
            return hands, pile #Player has no cards, he can't play

        if lucky and verbose : print("Player", player_number, "got lucky and can play again")

    return hands, pile


def count_hands(hands):
    hand_counts = np.zeros((game.params["nb_players"], game.params["nb_families"]))

    for player, hand in enumerate(hands):
        for card in hand:
            hand_counts[player, card[0]] += 1

    return hand_counts

def build_binary_hands(hands):
    binary_hands = np.zeros((game.params["nb_players"], game.params["nb_families"], game.params["nb_people_per_family"]))

    for player, hand in enumerate(hands):
        for card in hand:
            binary_hands[player, card[0], card[1]] = 1

    return binary_hands

def is_game_over(hands):
    non_empty_hands = 0
    for player in range(hands.shape[0]):
        if np.sum(hands[player]) > 0:
            non_empty_hands += 1

    return non_empty_hands <= 1

def play_simulation(player_number, og_hands, pile, og_families_scored, lucky, verbose=VERBOSE):
    maxturns = 10e4
    turn=0

    used_fam_scores = og_families_scored.copy()

    starting_player = player_number + (not lucky)

    hand_counts = count_hands(og_hands)
    og_hand_counts = hand_counts.copy()

    hands = build_binary_hands(og_hands)

    while not is_game_over(hands) and turn < maxturns:
        playing_player = (starting_player + turn) % game.params["nb_players"]
        hands, pile = play_simulation_turn(hands, pile, playing_player, used_fam_scores, hand_counts, verbose=verbose)
        turn+=1

    if turn == maxturns:
        print("og hands :",og_hands)
        print("OG hand counts :",og_hand_counts)
        print("OG families scores :", og_families_scored)
        print("--------------------")
        print("hand_counts :",hand_counts)
        print("pile :",pile)
        print("faimilies scored :", used_fam_scores)
        raise ValueError("Simulation over because too long")

    scores = game.compute_scores(used_fam_scores)

    if verbose : print("Simulation over, scores :", scores)

    return scores