import numpy as np
import game
from copy import deepcopy

params = {"selection_method" : "greedy"} # Can be "uniform", "weighted" or "greedy"

VERBOSE = False

class simulation:
    def __init__(self, hands, pile, families_scored, verbose = False):
        self.nb_players = len(hands)
        self.nb_families = families_scored.shape[0]
        self.hands = self.build_binary_hands(hands)
        self.pile = pile
        self.verbose = verbose
        self.families_scored = families_scored
        self.hand_counts = self.count_hands(hands)

        self.og_hands = deepcopy(self.hands)
        self.og_families_scored = families_scored.copy()

        for family, scorer in enumerate(families_scored[:,0]):
            if scorer == -1:
                continue
            for player, hand in enumerate(self.hands):
                if hand[family].any():
                    print("hands :",hands)
                    print("families scored :", families_scored)
                    raise ValueError(f"Problem: scored family {family} in player {player}'s hand")
                
        famcounts = np.zeros(self.nb_families)
        for hand in hands:
            for card in hand:
                famcounts[card[0]] += 1
        for card in pile:
            famcounts[card[0]] += 1
        for family, count in enumerate(famcounts):
            if count< game.params["nb_people_per_family"] and families_scored[family,0] == -1:
                print("pile :",pile)
                print("hands :",hands)
                raise ValueError(f"Not enough cards in family {family}")

    def count_hands(self, hands):
        hand_counts = np.zeros((self.nb_players, self.nb_families))

        for player, hand in enumerate(hands):
            for card in hand:
                hand_counts[player, card[0]] += 1

        return hand_counts

    def build_binary_hands(self, hands):
        binary_hands = np.zeros((self.nb_players, self.nb_families, game.params["nb_people_per_family"]))

        for player, hand in enumerate(hands):
            for card in hand:
                binary_hands[player, card[0], card[1]] = 1

        return binary_hands
    
    def playout(self, player_number, lucky):
        maxturns = 10e4
        turn=0

        starting_player = player_number + (not lucky)

        for player, hc in enumerate(self.hand_counts):
            for family, count in enumerate(hc):
                if count==6:
                    self.score_family(family, player)

        while not self.is_game_over() and turn < maxturns:
            playing_player = (starting_player + turn) % self.nb_players 
            self.play_simulation_turn(playing_player)
            turn+=1

            if turn > maxturns - 10: self.verbose = True

        if turn == maxturns:
            print("hands :",self.hands)
            print("hand counts :", self.hand_counts)
            print("pile :", self.pile)
            print("families scored :", self.families_scored)
            print("-----------------")
            print("OG hands :", self.og_hands)
            print("OG families scored :", self.og_families_scored)
            raise ValueError("Simulation over because too long")

        scores = self.compute_scores()
        if self.verbose : print("Simulation over, scores :", scores)
        return scores
    

    def play_simulation_turn(self, player_number):
        if not np.sum(self.hands[player_number]):
                return #Player has no cards, he can't play
        
        lucky = True
        while lucky:
            if self.verbose : 
                print("player", player_number,"playing")
                #print("Your hand :", self.hands[player_number],"\n")
            lucky = self.ask_random(player_number)

            if not np.sum(self.hands[player_number]):
                if self.verbose : print("empty hand :/")
                return #Player has no cards, he can't play

            if lucky and self.verbose : print("Player", player_number, "got lucky and can play again")

    def is_game_over(self):
        non_empty_hands = 0
        for hand in self.hands:
            if np.sum(hand) > 0:
                non_empty_hands += 1

        return non_empty_hands <= 1
    

    def compute_scores(self):
        scores = [np.sum(self.families_scored[:,0] == i) for i in range(self.nb_players)] # can be made faster
        return scores


    def choose_random(self, player_number):
        other_players = [i for i in range(self.nb_players) if i != player_number]
        asked_player = np.random.choice(other_players)

        families_in_hand = [i for i in range(game.params["nb_families"]) if self.hand_counts[player_number, i]]
        if params["selection_method"]=="weighted": 
            asked_family = np.random.choice(families_in_hand)
        elif params["selection_method"]=="uniform": 
            asked_family = np.random.choice(np.unique(families_in_hand))
        elif params["selection_method"]=="greedy": 
            asked_family = np.argmax(self.hand_counts[player_number])
        else :
            raise ValueError("Invalid selection method")
        
        unowned_family_cards = [i for i in range(game.params["nb_people_per_family"]) if not self.hands[player_number, asked_family, i]]

        if not len(unowned_family_cards): 
            print("families in hand :", families_in_hand)
            print("chosen family :", asked_family)
            print("player hand :", self.hands[player_number])
            raise ValueError("Empty card list, should not happen")
        
        asked_card = np.random.choice(unowned_family_cards)

        return asked_player, asked_family, asked_card
    
    def ask_random(self, player_number):
        choice = self.choose_random(player_number)

        return self.ask_chosen(player_number, choice)


    def score_family(self, family, score_guy):
        if self.verbose : print("Player", score_guy, "scored a family! Family number", family)
        self.families_scored[family,0] = score_guy
        # families_scored[family,1] = np.sum(families_scored[:,0] != -1)
        self.hands[score_guy, family] = np.zeros(game.params["nb_people_per_family"])
        self.hand_counts[score_guy, family] = 0


    def ask_chosen(self, player_number, choice):
        asked_player, asked_family, asked_card = choice

        if self.verbose : print("Player", player_number, "asks player", asked_player, "for family", asked_family, "and card", asked_card)

        if self.hands[asked_player, asked_family, asked_card] :
            if self.verbose : print("Player", asked_player, "gives", asked_family, asked_card, "to player", player_number)
            
            self.hands[asked_player, asked_family, asked_card] = 0
            self.hand_counts[asked_player, asked_family] -= 1

            if self.hand_counts[player_number, asked_family] +1 == game.params["nb_people_per_family"]:
                self.score_family(asked_family, player_number)
            else :
                self.hands[player_number, asked_family, asked_card] = 1
                self.hand_counts[player_number, asked_family] += 1

            return True
        
        elif len(self.pile):
            if self.verbose : print("Player", asked_player, "says 'Go Fish!'")
            card = self.pile.pop()
            
            if self.hand_counts[player_number, card[0]] + 1 == game.params["nb_people_per_family"]:
                self.score_family(card[0], player_number)
            else :
                self.hand_counts[player_number, card[0]] += 1
                self.hands[player_number, card[0], card[1]] = 1

            return (card[0] == asked_family and card[1] == asked_card)

        return False
    
    def pimc(self, player_number):
        for player in range(self.nb_players):
            if player == player_number : continue
            for family in range(self.nb_families):
                for card in range(game.params["nb_people_per_family"]):
                    if self.hands[player, family, card]:
                        self.ask_chosen(player_number, (player, family, card))
        
        return self.compute_scores()