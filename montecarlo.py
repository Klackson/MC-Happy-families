import numpy as np
import game

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

