import pygame
import sys
import os
from game_engine import *

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 600
CARD_WIDTH, CARD_HEIGHT = 80, 120
HAND_Y = SCREEN_HEIGHT - CARD_HEIGHT - 30
BOT_HAND_Y = 30
DISCARD_X, DISCARD_Y = SCREEN_WIDTH // 2 - CARD_WIDTH // 2, SCREEN_HEIGHT // 2 - CARD_HEIGHT // 2
BG_COLOR = (34, 139, 34)
TABLE_IMAGE_PATH = os.path.join("assets", "Table.png")
def draw_background():
    if os.path.exists(TABLE_IMAGE_PATH):
        table_img = pygame.transform.scale(pygame.image.load(TABLE_IMAGE_PATH), (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(table_img, (0, 0))
    else:
        screen.fill(BG_COLOR)
FONT_COLOR = (255, 255, 255)

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("UNO - GUI Edition")
font = pygame.font.SysFont(None, 32)

# Load card images
def load_card_image(card):
    if card.path and os.path.exists(card.path):
        return pygame.transform.scale(pygame.image.load(card.path), (CARD_WIDTH, CARD_HEIGHT))
    # fallback: draw a colored rect
    surf = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
    surf.fill((200, 200, 200))
    pygame.draw.rect(surf, (0, 0, 0), surf.get_rect(), 2)
    text = font.render(str(card), True, (0, 0, 0))
    surf.blit(text, (5, CARD_HEIGHT // 2 - 10))
    return surf

# Load deck image
def load_deck_image():
    deck_path = os.path.join("assets", "Deck.png")
    if os.path.exists(deck_path):
        return pygame.transform.scale(pygame.image.load(deck_path), (CARD_WIDTH, CARD_HEIGHT))
    surf = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
    surf.fill((80, 80, 80))
    pygame.draw.rect(surf, (0, 0, 0), surf.get_rect(), 2)
    text = font.render("Deck", True, (255, 255, 255))
    surf.blit(text, (10, CARD_HEIGHT // 2 - 10))
    return surf

def draw_hand(hand, y, selected_idx=None, hide_cards=False):
    x = 40
    for idx, card in enumerate(hand):
        if hide_cards:
            # Show Deck.png for bot's cards
            deck_img = load_deck_image()
            screen.blit(deck_img, (x, y))
            pygame.draw.rect(screen, (0, 0, 0), (x, y, CARD_WIDTH, CARD_HEIGHT), 2)
        else:
            img = load_card_image(card)
            screen.blit(img, (x, y))
            if selected_idx == idx:
                pygame.draw.rect(screen, (255, 215, 0), (x, y, CARD_WIDTH, CARD_HEIGHT), 4)
        x += CARD_WIDTH + 10

def draw_discard(card):
    img = load_card_image(card)
    screen.blit(img, (DISCARD_X, DISCARD_Y))

def draw_text(text, x, y, color=FONT_COLOR):
    surf = font.render(text, True, color)
    screen.blit(surf, (x, y))

def choose_color_popup():
    colors = ["Red", "Green", "Blue", "Yellow"]
    color_rects = []
    for i, color in enumerate(colors):
        rect = pygame.Rect(200 + i * 150, SCREEN_HEIGHT // 2 - 40, 120, 80)
        pygame.draw.rect(screen, (255, 0, 0) if color == "Red" else (0, 255, 0) if color == "Green" else (0, 0, 255) if color == "Blue" else (255, 255, 0), rect)
        pygame.draw.rect(screen, (0, 0, 0), rect, 3)
        draw_text(color, rect.x + 20, rect.y + 25, (0, 0, 0))
        color_rects.append((rect, color))
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                for rect, color in color_rects:
                    if rect.collidepoint(mx, my):
                        return color

def main():
    game = Game(num_players=1, difficulty=2)
    game.game_setup()
    player = game.players[0]
    bot = game.players[100]
    turn = 0  # 0: player, 1: bot
    selected_idx = None
    message = ""
    running = True
    clock = pygame.time.Clock()

    player_drawn_this_turn = False
    player_must_end_turn = False
    while running:
        draw_background()
        # Draw hands
        draw_hand(player.hand, HAND_Y, selected_idx)
        draw_hand(bot.hand, BOT_HAND_Y, hide_cards=True)
        # Draw discard pile
        draw_discard(game.discard_pile[-1])
        # Draw message
        draw_text(message, 20, SCREEN_HEIGHT // 2 - 30)
        # Draw deck
        deck_img = load_deck_image()
        screen.blit(deck_img, (DISCARD_X - 120, DISCARD_Y))
        # Draw end turn button if needed
        if player_must_end_turn:
            end_turn_rect = pygame.Rect(SCREEN_WIDTH - 180, SCREEN_HEIGHT - 80, 160, 50)
            pygame.draw.rect(screen, (200, 50, 50), end_turn_rect)
            draw_text("End Turn", end_turn_rect.x + 30, end_turn_rect.y + 10, (255,255,255))
        pygame.display.flip()
        clock.tick(30)

        if turn == 0:
            # Player's turn
            playable = [i for i, card in enumerate(player.hand) if card.is_playable_on(game.discard_pile[-1])]
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    # End turn button
                    if player_must_end_turn:
                        end_turn_rect = pygame.Rect(SCREEN_WIDTH - 180, SCREEN_HEIGHT - 80, 160, 50)
                        if end_turn_rect.collidepoint(mx, my):
                            player_drawn_this_turn = False
                            player_must_end_turn = False
                            turn = 1
                            message = ""
                            continue
                    # Select card
                    for idx, card in enumerate(player.hand):
                        x = 40 + idx * (CARD_WIDTH + 10)
                        if x <= mx <= x + CARD_WIDTH and HAND_Y <= my <= HAND_Y + CARD_HEIGHT:
                            selected_idx = idx
                            if idx in playable and not player_must_end_turn:
                                played_card = player.hand[idx]
                                player.play_card(played_card)
                                game.discard_pile.append(played_card)
                                selected_idx = None
                                # Wild color choice
                                if played_card.special in ["Wild", "Wild Draw Four"]:
                                    color = choose_color_popup()
                                    game.wild_card_color_choice(0, color)
                                # Special cards
                                effect = game.special_cards(played_card)
                                if effect["Force Draw"]:
                                    message = f"Bot draws {effect['Force Draw']} cards!"
                                    game.force_draw_cards(100, effect["Force Draw"])
                                if effect["Skip"]:
                                    message = "Bot's turn skipped!"
                                    turn = 0
                                    break
                                if not player.hand:
                                    message = "You win!"
                                    running = False
                                    break
                                turn = 1
                                break
                            elif player_must_end_turn and idx in playable and player_drawn_this_turn:
                                # Allow playing the drawn card if playable
                                played_card = player.hand[idx]
                                if played_card.is_playable_on(game.discard_pile[-1]):
                                    player.play_card(played_card)
                                    game.discard_pile.append(played_card)
                                    selected_idx = None
                                    player_drawn_this_turn = False
                                    player_must_end_turn = False
                                    # Wild color choice
                                    if played_card.special in ["Wild", "Wild Draw Four"]:
                                        color = choose_color_popup()
                                        game.wild_card_color_choice(0, color)
                                    # Special cards
                                    effect = game.special_cards(played_card)
                                    if effect["Force Draw"]:
                                        message = f"Bot draws {effect['Force Draw']} cards!"
                                        game.force_draw_cards(100, effect["Force Draw"])
                                    if effect["Skip"]:
                                        message = "Bot's turn skipped!"
                                        turn = 0
                                        break
                                    if not player.hand:
                                        message = "You win!"
                                        running = False
                                        break
                                    turn = 1
                                    break
                    # Draw from deck
                    if DISCARD_X - 120 <= mx <= DISCARD_X - 120 + CARD_WIDTH and DISCARD_Y <= my <= DISCARD_Y + CARD_HEIGHT:
                        if not game.deck:
                            game.reshuffle_deck()
                        if game.deck and not player_drawn_this_turn and not player_must_end_turn:
                            drawn = game.deck.pop()
                            player.draw_card(drawn)
                            message = f"You drew: {drawn}"
                            # If the drawn card is playable, allow to play it, else must end turn
                            if drawn.is_playable_on(game.discard_pile[-1]):
                                player_drawn_this_turn = True
                                player_must_end_turn = True
                            else:
                                player_drawn_this_turn = True
                                player_must_end_turn = True
                                message += " (No playable move, end your turn)"
            # No playable cards: must draw, but only once
            if not playable and not player_drawn_this_turn and not player_must_end_turn and not message:
                if not game.deck:
                    game.reshuffle_deck()
                if game.deck:
                    drawn = game.deck.pop()
                    player.draw_card(drawn)
                    message = f"No playable cards. Drew: {drawn}"
                    if drawn.is_playable_on(game.discard_pile[-1]):
                        player_drawn_this_turn = True
                        player_must_end_turn = True
                    else:
                        player_drawn_this_turn = True
                        player_must_end_turn = True
                        message += " (No playable move, end your turn)"
        else:
            # Bot's turn
            pygame.time.wait(800)
            top_card = game.discard_pile[-1]
            if game.difficulty == 1:
                chosen = Strategy.choose_random_card(bot.hand, top_card)
            else:
                chosen = Strategy.choose_with_priority(bot.hand, top_card)

            if chosen:
                bot.play_card(chosen)
                game.discard_pile.append(chosen)
                message = f"Bot played: {chosen}"
                if chosen.special in ["Wild", "Wild Draw Four"]:
                    game.wild_card_color_choice(100)
                    message += f" (Color: {game.discard_pile[-1].color})"
                effect = game.special_cards(chosen)
                if effect["Force Draw"]:
                    message = f"You draw {effect['Force Draw']} cards!"
                    game.force_draw_cards(0, effect["Force Draw"])
                if effect["Skip"]:
                    message = "Your turn is skipped!"
                    turn = 1
                    continue
            else:
                if not game.deck:
                    game.reshuffle_deck()
                if game.deck:
                    drawn = game.deck.pop()
                    bot.draw_card(drawn)
                    message = "Bot drew a card."
            if not bot.hand:
                message = "Bot wins!"
                running = False
            turn = 0
    # Game over
    while True:
        draw_background()
        draw_text(message, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2)
        draw_text("Press any key to exit...", SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 40)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                pygame.quit()
                sys.exit()

if __name__ == "__main__":
    main()
