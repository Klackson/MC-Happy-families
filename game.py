import numpy as np
import simpleai

params = {"nb_families" : 4, 
          "nb_people_per_family" : 3,
          "starting_hand_size" : 6,
          "nb_players" : 2}

VERBOSE = True

player_types = ["Human", "Human"]

def generate_deck(verbose=VERBOSE):
    deck = []

    for family in range(params["nb_families"]):
        for person in range(params["nb_people_per_family"]):
            deck.append([family, person])

    np.random.shuffle(deck)
    if verbose : print("Deck size :", len(deck))
    return deck

def deal_hands(deck, nb_players):
    # Calculate the total number of cards to be dealt
    total_cards_to_deal = params["starting_hand_size"] * nb_players
    
    # Ensure the deck has enough cards to deal
    if len(deck) < total_cards_to_deal:
        raise ValueError("Not enough cards in the deck to deal to all players")
    
    # Slice the deck to get only the required number of cards
    deck_to_deal = deck[:total_cards_to_deal]
    pile = deck[total_cards_to_deal:]
    
    # Distribute the sliced deck evenly among the players
    hands = [deck_to_deal[i::nb_players] for i in range(nb_players)]
    return hands, pile


def is_family_scored(hands):
    player = 0
    for hand in hands:
        counts = np.zeros(params["nb_families"])
        for card in hand:
            counts[card[0]] += 1
            if counts[card[0]] == params["nb_people_per_family"]:
                return player, card[0]
        player += 1
    return -1, -1

def ask_human(hands, player_number):
    is_player_valid = False
    while not is_player_valid:
        asked_player = int(input("What player do you want to ask?"))

        if asked_player > params["nb_players"] or asked_player < 0:
            print("This player doesn't exist")
            continue

        is_player_valid = len(hands[asked_player])
        if not is_player_valid:
            print("You cannot ask for a card from a player with no cards in hand")

    family_counts = np.zeros(params["nb_families"])
    for card in hands[player_number]:
        family_counts[card[0]] += 1

    is_family_valid = False
    while not is_family_valid:
        asked_family = int(input("What family do you want to ask for?"))
        
        if asked_family >= params["nb_families"] or asked_family < 0:
            print("This family doesn't exist")
            continue

        is_family_valid = family_counts[asked_family]

        if not is_family_valid:
            print("You cannot ask a family you do not have in hand")

    is_card_valid = False
    while not is_card_valid:
        asked_card = int(input("What card do you want to ask for?"))
        if asked_card < 0 or asked_card >= params["nb_people_per_family"]:
            print("This card number doesn't exist")
        else:
            is_card_valid = True

    return asked_player, asked_family, asked_card

def ask_AI(hands, player_number, verbose = VERBOSE):
    if player_types[player_number] == "simple_AI":
        return simpleai.choose_move(hands, player_number)

def ask(hands, pile, player_number, player_type="Human", AI_choice=None, verbose = VERBOSE):
    if player_types[player_number] == "Human":
        asked_player, asked_family, asked_card = ask_human(hands, player_number)
        

    else :
        # Ensure on the AI side that the choice is feasible
        asked_player, asked_family, asked_card = ask_AI(hands, player_number)

    #else : raise ValueError("Invalid player type")

    if verbose : print("Player", player_number, "asks player", asked_player, "for card", asked_card, "in family", asked_family)

    for card in hands[asked_player]:
        if card[0] == asked_family and card[1] == asked_card:
            hands[player_number].append(card)
            hands[asked_player].remove(card)
            if verbose : print("Player", player_number, "got the card he asked for")
            return True, hands, pile
    
    # Otherwise the player draws a card
    card, hands, pile = draw(hands, pile, player_number)
    if card[0] == asked_family and card[1] == asked_card: # Lucky draw
        if verbose : print("Player", player_number, "drew the card he asked for")
        return True, hands, pile
    
    return False, hands, pile

def draw(hands, pile, player_number, verbose = VERBOSE):
    if not len(pile): #If the pile is empty, the player can't draw
        if verbose : print("Player", player_number, "can't draw a card, the pile is empty")
        return hands, pile

    card = pile.pop(0)
    hands[player_number].append(card)
    if verbose : print("Player", player_number, "drew a card")
    return card, hands, pile


def play_turn(hands, pile, player_number, families_scored, verbose=VERBOSE):
    if verbose : print("Player", player_number, "playing")

    lucky = True
    while lucky:
        print("Your hand :", hands[player_number],"\n")
        lucky, hands, pile = ask(hands, pile, player_number)

        score_guy, family_scored = is_family_scored(hands)
        if score_guy>=0 : 
            score_family(hands, family_scored, score_guy, families_scored)

        if len(hands[player_number]) == 0:
            return hands, pile #Player has no cards, he can't play

        if lucky and verbose : print("Player", player_number, "got lucky and can play again")

    return hands, pile

def score_family(hands, family, score_guy, families_scored):
    print("Player", score_guy, "scored a family! Family number", family)
    families_scored[score_guy] += 1
    hand = hands[score_guy].copy()
    for card in hand:
        if card[0] == family:
            hands[score_guy].remove(card)

def is_game_over(hands):
    for hand in hands:
        if len(hand) > 0:
            return False
    return True

def play_game(nb_players, verbose=VERBOSE):
    deck = generate_deck()
    hands, pile = deal_hands(deck, nb_players)
    families_scored = [0] * nb_players
    
    turn = 0
    max_turns = 10e6
    while turn < max_turns:
        player = turn % nb_players
        hands, pile = play_turn(hands, pile, player, families_scored)
        turn += 1
        
        if is_game_over(hands) :
            winner = np.argmax(families_scored)
            if verbose : print("Player", winner, "wins!")
            return winner
            
    if verbose : print('Game over because too long')
    return -1

def main():
    play_game(params["nb_players"])

main()