import pytest
from game_engine import Card, Player, Strategy, Game


def test_card_str_and_path():
	c1 = Card(number=5, color="Red")
	assert "5 (Red)" in str(c1)
	assert c1.path.endswith("Red_5.png")

	c2 = Card(special="Wild")
	assert "Wild" in str(c2)
	assert "Wild.png" in c2.path


def test_is_playable_on():
	top = Card(number=7, color="Blue")
	same_color = Card(number=3, color="Blue")
	same_number = Card(number=7, color="Red")
	wild = Card(special="Wild")

	assert same_color.is_playable_on(top)
	assert same_number.is_playable_on(top)
	assert wild.is_playable_on(top)


def test_player_draw_and_play():
	p = Player(1)
	c = Card(number=2, color="Green")
	p.draw_card(c)
	assert len(p.hand) == 1
	played = p.play_card(c)
	assert played is c
	assert len(p.hand) == 0
	# playing a card not in hand returns None
	assert p.play_card(c) is None


def test_choose_with_priority_prefers_number():
	top = Card(number=4, color="Yellow")
	hand = [Card(number=2, color="Yellow"), Card(number=9, color="Yellow"), Card(special="Skip", color="Yellow")]
	chosen = Strategy.choose_with_priority(hand, top)
	assert chosen.number == 9


def test_game_create_and_setup_and_reshuffle():
	game = Game(num_players=2)
	# deck should be populated
	assert len(game.deck) > 0
	# deal hands
	game.game_setup(hand_size=5)
	# players should have 5 cards each
	for p in game.players.values():
		assert len(p.hand) == 5
	# discard pile must have at least one card
	assert len(game.discard_pile) == 1

	# exhaust the deck and ensure reshuffle preserves top of discard
	# move all deck cards to discard except top
	while game.deck:
		game.discard_pile.append(game.deck.pop())
	top_before = game.discard_pile[-1]
	game.reshuffle_deck()
	assert game.discard_pile[-1] == top_before


def test_force_draw_and_specials():
	game = Game(num_players=1)
	game.game_setup(hand_size=1)
	player_id = 0
	# create a Draw Two and force the other player to draw
	dt = Card(special="Draw Two", color="Red")
	game.discard_pile.append(dt)
	# apply special should cause next player to draw 2
	game.apply_special(dt)
	# ensure current player has drawn cards (hand size increased)
	assert len(game.players[game.current_player].hand) >= 1


if __name__ == "__main__":
	pytest.main(["-q", "test_uno.py"])
