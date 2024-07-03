import numpy as np
import game

params = {"selection_method" : "greedy"}

def assume_game_state(player_number, hands, families_scored):
    deck = build_remaining_deck(hands, families_scored, player_number)

    hands, pile = deal_other_hands(player_number, deck, hands)

    return hands, pile

def build_remaining_deck(hands, families_scored, player_number, verbose = game.VERBOSE):
    deck = []

    for family in range(game.params["nb_families"]):
        if families_scored[family,0] != -1: continue # Family already scored
        for person in range(game.params["nb_people_per_family"]):
            card = [family, person]
            if card in hands[player_number]: continue # Card already in hand
            deck.append(card)

    np.random.shuffle(deck)
    if verbose : print("Deck size :", len(deck))
    return deck

def deal_other_hands(player_number, deck, hands):
    newhands = hands.copy()

    for i in range(len(hands)):
        if i == player_number: continue
        hand = hands[i]
        for j in range(len(hand)):
            card = deck.pop()
            newhands[i] = card
    
    return newhands, deck # Deck is the pile since dealt cards have been popped from it


def ask_random(hands, player_number):
    other_players = [i for i in range(len(hands)) if i != player_number]
    asked_player = np.random.choice(other_players)

    families_in_hand = [card[0] for card in hands[player_number]]
    if params["selection_method"]=="weighted": asked_family = np.random.choice(families_in_hand)
    elif params["selection_method"]=="uniform": asked_family = np.random.choice(np.unique(families_in_hand))
    elif params["selection_method"]=="greedy": 
        unique, counts = np.unique(families_in_hand, return_counts=True)
        index = np.argmax(counts)
        asked_family = unique[index]
    
    unowned_family_cards = [i for i in range(len(game.params["nb_people_per_family"])) if [asked_family, i] not in hands[player_number]]
    asked_card = np.random.choice(unowned_family_cards)

    return asked_player, asked_family, asked_card