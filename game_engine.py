import random
import os
import pandas as pd
from copy import deepcopy

class Card:
    def __init__(self, number=None, color=None, special=None):
        self.number = number
        self.color = color
        self.special = special
        self.path = self.path_finder(number, color, special)

    def __str__(self):
        if self.special and self.color:
            return f"{self.special} ({self.color})"
        elif self.special:
            return f"{self.special}"
        return f"{self.number} ({self.color})"

    def is_playable_on(self, other_card):
        if self.special in ["Wild", "Wild Draw Four"]:
            return True
        if self.color == other_card.color:
            return True
        if self.number is not None and self.number == other_card.number:
            return True
        if self.special is not None and self.special == other_card.special:
            return True
        return False
    
    @staticmethod
    def path_finder(number, color, special):
        if special == "Wild":
            return os.path.join("assets", "Wild.png")
        elif special == "Wild Draw Four":
            return os.path.join("assets", "Wild_Draw.png")
        elif special in ["Skip", "Reverse"]:
            return os.path.join("assets", f"{color}_{special}.png")
        elif special == "Draw Two":
            return os.path.join("assets", f"{color}_Draw.png")
        elif number is not None and color is not None:
            return os.path.join("assets", f"{color}_{number}.png")
        return None
    

class Player:
    def __init__(self, player_id):
        self.player_id = player_id
        self.hand = []

    def draw_card(self, card):
        self.hand.append(card)

    def play_card(self, card):
        if card in self.hand:
            self.hand.remove(card)
            return card
        return None


class Strategy:
    @staticmethod
    def choose_random_card(hand, top_card):
        playable_cards = [card for card in hand if card.is_playable_on(top_card)]
        if playable_cards:
            return random.choice(playable_cards)
        return None
    
    @staticmethod
    def choose_with_priority(hand, top_card):
        playable_cards = [card for card in hand if card.is_playable_on(top_card)]
        if not playable_cards:
            return None

        number_cards = [card for card in playable_cards if card.number is not None]
        if number_cards:
            return max(number_cards, key=lambda c: c.number)

        for special in ["Wild Draw Four", "Wild", "Draw Two", "Skip", "Reverse"]:
            for card in playable_cards:
                if card.special == special:
                    return card

        return playable_cards[0]
    
    @staticmethod
    def monte_carlo_card(game, player_id, simulations=50):
        player = game.players[player_id]
        top_card = game.discard_pile[-1]
        playable_cards = [card for card in player.hand if card.is_playable_on(top_card)]

        if not playable_cards:
            return None

        card_scores = {card: 0 for card in playable_cards}

        for card in playable_cards:
            for i in range(simulations):
                
                sim_game = deepcopy(game)
                sim_player = sim_game.players[player_id]

                sim_player.play_card(card)
                sim_game.discard_pile.append(card)

                sim_players_ids = list(sim_game.players.keys())
                turn_index = sim_players_ids.index(player_id)
                while len(sim_game.players) > 1:
                    current_id = sim_players_ids[turn_index % len(sim_players_ids)]
                    current_player = sim_game.players.get(current_id)
                    if current_player:
                        playable = [c for c in current_player.hand if c.is_playable_on(sim_game.discard_pile[-1])]
                        if playable:
                            chosen = random.choice(playable)
                            current_player.play_card(chosen)
                            sim_game.discard_pile.append(chosen)
                        else:
                            if sim_game.deck:
                                current_player.draw_card(sim_game.deck.pop())
                    turn_index += 1

                if player_id not in sim_game.players:
                    card_scores[card] += 1

        best_card = max(card_scores, key=lambda c: card_scores[c])
        return best_card
    

class Game:
    def __init__(self, num_players=1, difficulty=1, simulations=50):
        self.num_players = num_players
        self.players = {i: Player(i) for i in range(self.num_players)}
        self.players[100] = Player(100)
        self.deck = self.create_deck()
        self.discard_pile = []
        self.difficulty = difficulty
        self.play_direction = 1
        self.winner = None
        self.simulations = simulations
        self.game_history = []

    def create_deck(self):
        deck = []
        
        for i in list(range(0, 10)) + list(range(1, 10)):
            for color in ["Red", "Green", "Blue", "Yellow"]:
                deck.append(Card(number=i, color=color))

        for special in ["Skip", "Reverse", "Draw Two"]:
            for i in range(2):
                for color in ["Red", "Green", "Blue", "Yellow"]:
                    deck.append(Card(special=special, color=color))

        for i in range(4):
            deck.append(Card(special="Wild"))
            deck.append(Card(special="Wild Draw Four"))

        random.shuffle(deck)
        return deck
    
    def game_setup(self, hand_size=7):
        for i in range(hand_size):
            for player in self.players.values():
                player.draw_card(self.deck.pop())

        first_card = self.deck.pop()
        while first_card.special == "Wild Draw Four":
            self.deck.insert(0, first_card)
            random.shuffle(self.deck)
            first_card = self.deck.pop()
        self.discard_pile.append(first_card)

    def reshuffle_deck(self):
        if not self.deck:
            top_card = self.discard_pile.pop()
            self.deck = self.discard_pile
            random.shuffle(self.deck)
            self.discard_pile = [top_card]

    def next_player(self, skip=False):
        """Move turn to the next player, respecting direction and skip."""
        ids = list(self.players.keys())
        idx = ids.index(self.current_player)
        step = 2 if skip else 1
        new_idx = (idx + step * self.play_direction) % len(ids)
        self.current_player = ids[new_idx]

    def apply_special(self, card):
        """Apply effects of special cards after playing them."""
        effect = self.special_cards(card)

        if effect["Reverse"]:
            self.play_direction *= -1
        elif effect["Skip"]:
            self.next_player(skip=True)
        elif effect["Force Draw"]:
            self.next_player()
            self.force_draw_cards(self.current_player, effect["Force Draw"])
        if effect["Wild Card"]:
            self.wild_card_color_choice(self.current_player)

    def player_turn(self, player_id, card):
        player = self.players[player_id]

        if card and card in player.hand and card.is_playable_on(self.discard_pile[-1]):
            played_card = player.play_card(card)
            self.discard_pile.append(played_card)
            self.log_move(player_id, "play", played_card)
            self.apply_special(played_card)
        else:
            self.force_draw_cards(player_id, 1)
            self.log_move(player_id, "draw", None)

        if not player.hand:
            self.winner = player_id

        self.next_player()

    def bot_turn(self, player_id=100):
        player = self.players[player_id]
        top_card = self.discard_pile[-1]

        if self.difficulty == 1:
            chosen = Strategy.choose_random_card(player.hand, top_card)
        elif self.difficulty == 2:
            chosen = Strategy.choose_with_priority(player.hand, top_card)
        elif self.difficulty == 3:
            chosen = Strategy.monte_carlo_card(self, player_id, simulations=self.simulations)

        if chosen:
            player.play_card(chosen)
            self.discard_pile.append(chosen)
            self.log_move(player_id, "play", chosen)
            self.apply_special(chosen)
        else:
            self.force_draw_cards(player_id, 1)
            self.log_move(player_id, "draw", None)

        if not player.hand:
            self.winner = player_id

        self.next_player()

    def wild_card_color_choice(self, player_id, choice=None):
        if player_id == 100:
            color_choice = random.choice(["Red", "Green", "Blue", "Yellow"])
        else:
            color_choice = choice
        self.discard_pile[-1].color = color_choice

    def force_draw_cards(self, player_id, num_cards):
        player = self.players[player_id]
        for i in range(num_cards):
            if not self.deck:
                self.reshuffle_deck()
            player.draw_card(self.deck.pop())

    def special_cards(self, card):
        card_effect = {
            "Wild Card": False,
            "Force Draw": 0,
            "Skip": False,
            "Reverse": False
        }

        if card.special == "Draw Two":
            card_effect["Force Draw"] = 2
        elif card.special == "Wild Draw Four":
            card_effect["Force Draw"] = 4
            card_effect["Wild Card"] = True
        elif card.special == "Wild":
            card_effect["Wild Card"] = True
        elif card.special == "Skip":
            card_effect["Skip"] = True
        elif card.special == "Reverse":
            card_effect["Reverse"] = True
        
        return card_effect

    def log_move(self, player_id, action, card):
        self.game_history.append({
            "player_id": player_id,
            "action": action,
            "card": str(card) if card else None,
            "hand_size": len(self.players[player_id].hand),
            "top_card": str(self.discard_pile[-1])
        })

    def return_game_history(self):
        return pd.DataFrame(self.game_history)