from game_engine import *

def print_hand(player):
    print("Your hand:")
    for idx, card in enumerate(player.hand):
        print(f"  {idx + 1}: {card}")

def get_player_move(player, top_card):
    print(f"Top card: {top_card}")
    print_hand(player)
    while True:
        move = input("Enter the number of the card to play, or 'd' to draw: ").strip()
        if move.lower() == 'd':
            return None
        if move.isdigit():
            idx = int(move) - 1
            if 0 <= idx < len(player.hand):
                card = player.hand[idx]
                if card.is_playable_on(top_card):
                    return card
                else:
                    print("You can't play that card.")
            else:
                print("Invalid card number.")
        else:
            print("Invalid input.")

def main():
    print("Welcome to CLI Uno!")
    num_players = 1
    difficulty = 1
    while True:
        try:
            difficulty = int(input("Choose bot difficulty (1: Random, 2: Smart): "))
            if difficulty in [1, 2]:
                break
        except ValueError:
            pass
        print("Invalid input. Please enter 1 or 2.")

    game = Game(num_players=num_players, difficulty=difficulty)
    game.game_setup()
    player = game.players[0]
    bot = game.players[100]
    turn = 0

    while True:
        game.reshuffle_deck()
        top_card = game.discard_pile[-1]
        print("\n--- New Turn ---")
        print(f"Top card: {top_card}")
        if turn == 0:
            playable = any(card.is_playable_on(top_card) for card in player.hand)
            if playable:
                card = get_player_move(player, top_card)
                if card:
                    player.play_card(card)
                    game.discard_pile.append(card)

                    if card.special in ["Wild", "Wild Draw Four"]:
                        color = input("Choose a color (Red, Green, Blue, Yellow): ").strip().capitalize()
                        while color not in ["Red", "Green", "Blue", "Yellow"]:
                            color = input("Invalid color. Choose (Red, Green, Blue, Yellow): ").strip().capitalize()
                        game.wild_card_color_choice(0, color)
                    effect = game.special_cards(card)
                    if effect["Force Draw"]:
                        print(f"Bot draws {effect['Force Draw']} cards!")
                        game.force_draw_cards(100, effect["Force Draw"])
                    if effect["Skip"]:
                        print("Bot's turn skipped!")
                        turn = 0
                        continue
                else:
                    if not game.deck:
                        game.reshuffle_deck()
                    drawn = game.deck.pop()
                    print(f"You drew: {drawn}")
                    player.draw_card(drawn)
            else:
                print("No playable cards. Drawing a card...")
                if not game.deck:
                    game.reshuffle_deck()
                drawn = game.deck.pop()
                print(f"You drew: {drawn}")
                player.draw_card(drawn)
            if not player.hand:
                print("Congratulations! You win!")
                break
            turn = 1
        else:
            
            print("Bot's turn...")
            before = len(bot.hand)
            result = game.bot_turn(100)
            after = len(bot.hand)
            if before == after:
                
                if not game.deck:
                    game.reshuffle_deck()
                drawn = game.deck.pop()
                bot.draw_card(drawn)
                print("Bot drew a card.")
            else:
                played_card = game.discard_pile[-1]
                print(f"Bot played: {played_card}")
                
                if played_card.special in ["Wild", "Wild Draw Four"]:
                    game.wild_card_color_choice(100)
                    print(f"Bot chose color: {game.discard_pile[-1].color}")
                
                effect = game.special_cards(played_card)
                if effect["Force Draw"]:
                    print(f"You draw {effect['Force Draw']} cards!")
                    game.force_draw_cards(0, effect["Force Draw"])
                if effect["Skip"]:
                    print("Your turn is skipped!")
                    turn = 1
                    continue
            if not bot.hand:
                print("Bot wins! Better luck next time.")
                break
            turn = 0

if __name__ == "__main__":
    main()
