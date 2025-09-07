# UNO AI Bot

A Python implementation of the classic UNO card game with both GUI and CLI modes. Play against a smart AI bot with multiple difficulty levels!

![GUI Gameplay](assets/screenshots/gui.png)

## Features
- Play UNO in a graphical interface (GUI) or in the terminal (CLI)
- AI bot with three difficulty levels: Random, Smart, and Monte Carlo
- Realistic UNO rules, including special cards (Skip, Reverse, Draw Two, Wild, Wild Draw Four)
- Game history tracking and pandas DataFrame export
- Colorful card graphics and smooth gameplay

## How to Run

### Requirements
- Python 3.8+
- `pygame`
- `pandas`

Install dependencies:
```bash
pip install -r requirements.txt
```

### Start the GUI Game
```bash
python gui_game.py
```

### Start the CLI Game
```bash
python cli_game.py
```

## Controls (GUI)
- Click on a card to play it
- Click the deck to draw a card
- Click "End Turn" if you cannot play after drawing
- Choose a color for wild cards via popup

## TODO
- Develop a Reinforcement Learning (RL) Model as an added method in Strategy Class
- Develop an XGBoost Model as an added method in Strategy Class

## Credits
- UNO card graphics by [alexder on itch.io](https://alexder.itch.io/uno-card-game-asset-pack?download)

## License
This project is for educational purposes. Please respect the original asset creator's license for the card images.
