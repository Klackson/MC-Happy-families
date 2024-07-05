import numpy as np
import simpleai

params = {"nb_families" : 7, 
          "nb_people_per_family" : 6,
          "starting_hand_size" : 6,
          "nb_players" : 2}

VERBOSE = False

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


def is_family_scored(hands, families_scored):
    #new_families_scored = families_scored.copy()

    for player, hand in enumerate(hands):
        counts = np.zeros(params["nb_families"])
        for card in hand:
            counts[card[0]] += 1
            if counts[card[0]] == params["nb_people_per_family"]:
                hands, families_scored = score_family(hands, card[0], player, families_scored)

    return hands, families_scored

def ask_human(hands, player_number):
    is_player_valid = False
    while not is_player_valid:
        asked_player = int(input("What player do you want to ask?"))

        if asked_player > params["nb_players"] or asked_player < 0:
            print("This player doesn't exist")
            continue

        if asked_player == player_number:
            print("You cannot ask yourself for a card")
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


def ask(hands, pile, player_number, chosen=None, verbose = VERBOSE):
    if not chosen : # Human player
        asked_player, asked_family, asked_card = ask_human(hands, player_number)

    else :
        # Ensure on the AI side that the choice is feasible
        asked_player, asked_family, asked_card = chosen

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
        return [-1,-1], hands, pile

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

        hands, families_scored = is_family_scored(hands, families_scored)

        if len(hands[player_number]) == 0:
            return hands, pile #Player has no cards, he can't play

        if lucky : print("Player", player_number, "got lucky and can play again")

    print("Turn over")
    return hands, pile

def score_family(hands, family, score_guy, families_scored):
    if VERBOSE : print("Player", score_guy, "scored a family! Family number", family)
    families_scored[family,0] = score_guy
    families_scored[family,1] = np.sum(families_scored[:,0] != -1)

    hand = hands[score_guy].copy()
    for card in hand:
        if card[0] == family:
            hands[score_guy].remove(card)
    
    return hands, families_scored

def is_game_over(hands):
    for hand in hands:
        if len(hand) > 0:
            return False
    return True

def play_game(nb_players, verbose=VERBOSE):
    deck = generate_deck()
    hands, pile = deal_hands(deck, nb_players)
    families_scored = np.full((params["nb_families"],2), -1)
    # Row = family, Column 0 = player who scored, Column 1 = order it was scored in
    
    turn = 0
    max_turns = 10e6
    while turn < max_turns:
        player = turn % nb_players
        hands, pile = play_turn(hands, pile, player, families_scored)
        turn += 1
        
        if is_game_over(hands) :

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

            scores = compute_scores(families_scored)

            return scores
            
    if verbose : print('Game over because too long')
    return -1

def compute_scores(families_scored):
    scores = [np.sum(families_scored[:,0] == i) for i in range(params["nb_players"])] # can be made faster
    return scores

def main():
    play_game(params["nb_players"])