import numpy as np
import simpleai, nestedai

params = {"nb_families" : 7, 
          "nb_people_per_family" : 6,
          "starting_hand_size" : 6,
          "nb_players" : 2}

VERBOSE = False

class game:
    def __init__(self, player_list, nb_families = params["nb_families"], nb_people_per_family = params["nb_people_per_family"], starting_hand_size = params["starting_hand_size"], verbose=False):
        self.nb_families = nb_families
        self.player_list = player_list
        self.nb_players = len(player_list)
        self.nb_people_per_family = nb_people_per_family
        self.starting_hand_size = starting_hand_size
        self.verbose = verbose

        self.hands, self.pile = self.deal_hands(self.generate_deck())
        self.families_scored = np.full((self.nb_families,2), -1)
        self.card_tracker = np.full((nb_families, nb_people_per_family), -1)

    def generate_deck(self):
        deck = []

        for family in range(self.nb_families):
            for person in range(self.nb_people_per_family):
                deck.append([family, person])

        np.random.shuffle(deck)
        if self.verbose : print("Deck size :", len(deck))
        return deck

    def deal_hands(self, deck):
        # Calculate the total number of cards to be dealt
        total_cards_to_deal = self.starting_hand_size * self.nb_players
        
        # Ensure the deck has enough cards to deal
        if len(deck) < total_cards_to_deal:
            raise ValueError("Not enough cards in the deck to deal to all players")
        
        # Slice the deck to get only the required number of cards
        deck_to_deal = deck[:total_cards_to_deal]
        pile = deck[total_cards_to_deal:]
        
        # Distribute the sliced deck evenly among the players
        hands = [deck_to_deal[i::self.nb_players] for i in range(self.nb_players)]
        return hands, pile
    
    def present_hand(self, player_number):
        print("Your hand :")
        persons_per_family = [[] for _ in range(self.nb_families)]

        for card in self.hands[player_number]:
            persons_per_family[card[0]].append(card[1])

        for family in range(self.nb_families):
            print("Family", family, ":", np.sort(persons_per_family[family]))


    def ask_human(self, player_number):
        self.present_hand(player_number)

        is_player_valid = False
        while not is_player_valid:
            asked_player = int(input("What player do you want to ask? "))

            if asked_player > self.nb_players or asked_player < 0:
                print("This player doesn't exist")
                continue

            if asked_player == player_number:
                print("You cannot ask yourself for a card")
                continue

            is_player_valid = len(self.hands[asked_player])
            if not is_player_valid:
                print("You cannot ask for a card from a player with no cards in hand")

        family_counts = np.zeros(self.nb_families)
        for card in self.hands[player_number]:
            family_counts[card[0]] += 1

        is_family_valid = False
        while not is_family_valid:
            asked_family = int(input("What family do you want to ask for? "))
            
            if asked_family >= self.nb_families or asked_family < 0:
                print("This family doesn't exist")
                continue

            is_family_valid = family_counts[asked_family]

            if not is_family_valid:
                print("You cannot ask a family you do not have in hand")

        is_card_valid = False
        while not is_card_valid:
            asked_card = int(input("What card do you want to ask for? "))
            if asked_card < 0 or asked_card >= self.nb_people_per_family:
                print("This card number doesn't exist")
            else:
                is_card_valid = True

        return asked_player, asked_family, asked_card

    
    def ask(self, player_number, chosen=None):
        if not chosen : # Human player
            asked_player, asked_family, asked_card = self.ask_human(player_number)

        else :
            # Ensure on the AI side that the choice is feasible
            asked_player, asked_family, asked_card = chosen

        if self.verbose : print("Player", player_number, "asks player", asked_player, "for card", asked_card, "in family", asked_family)

        for card in self.hands[asked_player]:
            if card[0] == asked_family and card[1] == asked_card:
                self.hands[player_number].append(card)
                self.hands[asked_player].remove(card)
                if self.verbose : print("Player", player_number, "got the card he asked for")
                self.card_tracker[card[0], card[1]] = player_number
                return True
        
        # Otherwise the player draws a card
        card = self.draw(player_number)
        if card[0] == asked_family and card[1] == asked_card: # Lucky draw
            if self.verbose : print("Player", player_number, "drew the card he asked for")
            self.card_tracker[card[0], card[1]] = player_number
            return True
        
        return False

    def draw(self, player_number):
        if not len(self.pile): #If the pile is empty, the player can't draw
            if self.verbose : print("Player", player_number, "can't draw a card, the pile is empty")
            return [-1,-1]

        card = self.pile.pop(0)
        self.hands[player_number].append(card)
        if self.verbose : print("Player", player_number, "drew a card")
        return card
    
    def play_turn(self, player_number):
        if self.verbose : print("Player", player_number, "playing")

        lucky = True
        while lucky:
            if self.player_list[player_number].capitalize() == "Human":
                lucky = self.ask(player_number)
            
            elif self.player_list[player_number].capitalize() == "Simpleai":
                choice = simpleai.choose_move(self, player_number, verbose = self.verbose)
                lucky = self.ask(player_number, choice)

            elif self.player_list[player_number].capitalize() == "Nestedai":
                choice = nestedai.choose_move(self, player_number, verbose = self.verbose)
                lucky = self.ask(player_number, choice)

            else:
                raise ValueError("Invalid player type")

            self.is_family_scored()

            if len(self.hands[player_number]) == 0:
                return #Player has no cards, he can't play

            if lucky and self.verbose : print("Player", player_number, "got lucky and can play again\n")

        if self.verbose : print("Turn over\n")


    def is_family_scored(self):
        for player, hand in enumerate(self.hands):
            counts = np.zeros(self.nb_families)
            for card in hand:
                counts[card[0]] += 1
                if counts[card[0]] == self.nb_people_per_family:
                    self.score_family(card[0], player)


    def score_family(self, family, score_guy):
        if self.verbose : print("Player", score_guy, "scored a family! Family number", family)
        self.families_scored[family,0] = score_guy
        self.families_scored[family,1] = np.sum(self.families_scored[:,0] != -1)

        self.hands[score_guy] = [card for card in self.hands[score_guy] if card[0] != family]

        self.card_tracker[family, :] = np.full(self.nb_people_per_family, -1)

        if self.verbose : print("Score :", self.compute_scores())
        

    def is_game_over(self):
        non_empty_hands = 0

        for hand in self.hands:
            if len(hand):
                non_empty_hands +=1

        return non_empty_hands <=1
    

    def compute_scores(self):
        scores = [np.sum(self.families_scored[:,0] == i) for i in range(self.nb_players)] # can be made faster
        return scores
    
    
    def assume_game_state(self, player_number):
        deck = self.build_remaining_deck(player_number)

        hands, pile = self.deal_other_hands(player_number, deck)

        return hands, pile


    def build_remaining_deck(self, player_number):
        deck = []

        for family in range(self.nb_families):
            if self.families_scored[family,0] != -1: continue # Family already scored
            for person in range(self.nb_people_per_family):
                card = [family, person]
                if card in self.hands[player_number] or self.card_tracker[family, person] != -1: continue # Card already in hand or position known
                deck.append(card)

        np.random.shuffle(deck)
        return deck


    def deal_other_hands(self, player_number, deck):
        newhands = [[] for _ in range(len(self.hands))]

        # First add known cards to hands
        for family in range(self.nb_families):
            for person in range(self.nb_people_per_family):
                owner = self.card_tracker[family, person]
                if owner >= 0:
                    newhands[owner].append([family, person])

        for i, hand in enumerate(self.hands):
            if i == player_number:
                newhands[player_number] = hand.copy()
                continue
            
            nb_added_cards = len(newhands[i])
            for _ in range(len(hand) - nb_added_cards): #Known hand size minus nb of known cards affected to hand
                card = deck.pop()
                newhands[i].append(card)
        
        return newhands, deck # Deck is the pile since dealt cards have been popped from it

    def play_game(self):
        turn = 0
        max_turns = 10e6
        while turn < max_turns:
            player = turn % self.nb_players
            self.play_turn(player)
            turn += 1
            
            if self.is_game_over() :
                scores = self.compute_scores()
                if self.verbose : print("Game over! Scores :", scores)

                return scores
                
        if self.verbose : print('Game over because too long')
        return -1