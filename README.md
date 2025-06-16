
# 🃏 BlackjackEngine

A modular, extensible Python blackjack engine featuring card counting, statistics tracking, legal move validation, and both CLI and programmable interfaces.

## 🚀 Features

- Full blackjack rules with support for:
  - Double down, split, surrender
  - Blackjacks with custom payouts
  - Soft/hard hand logic
- Card counting (Hi-Lo) with running and true count
- Bankroll and bet validation
- Generator-based controller for GUI, bot, or AI integration
- Quick-play for automated strategies
- CLI interface for local play
- Game statistics tracking (wins, losses, pushes, profit, etc.)

---

## 🛠️ Setup

### Requirements

- Python 3.8+
- No external dependencies (standard library only)

### Running the CLI

```bash
python BlackjackEngine.py
```

You’ll be greeted by a text-based blackjack game with prompts to bet, make moves, and view statistics.

---

## 📦 Code Structure

### Main Components

| Class                  | Description |
|------------------------|-------------|
| `GameConfig`           | Holds settings like number of decks, payout rules, and bet limits |
| `GameStats`            | Tracks performance data for the current session |
| `GameConstants`        | Lookup tables for card values and Hi-Lo count |
| `Hand`                 | Represents a single player hand, supports actions like hit, split, double |
| `BlackjackGameEngine`  | Core engine managing cards, rounds, dealer logic, payouts |
| `BlackjackGameController` | Generator-driven controller to allow turn-by-turn integration |
| `BlackjackCLI`         | A full command-line game loop interface |

---

## 🎮 How It Works

### Game Flow

1. **Initialization**  
   The deck is created and shuffled. The bankroll is set to the configured starting value.

2. **Round Start**  
   Player places a bet. Cards are dealt to both player and dealer.

3. **Player Actions**  
   Legal moves are presented based on hand state (e.g. can't double with 3+ cards). Actions are executed via `execute_action()`.

4. **Dealer Play**  
   Dealer plays per blackjack rules, hitting until reaching at least 17 (with soft 17 handling).

5. **Resolution**  
   Winnings are paid out, statistics are updated, and the game state is returned.

---

## 🧩 Integration Options

### CLI

Use the `BlackjackCLI` class for direct terminal interaction:

```python
from BlackjackEngine import BlackjackCLI

cli = BlackjackCLI()
cli.play_game()
```

### Generator (Programmatic UI / Bots)

Use the `BlackjackGameController` to drive gameplay manually or with AI:

```python
controller = BlackjackGameController()
gen = controller.game_session()
prompt = next(gen)

while True:
    print(prompt['message'])
    user_input = get_input_somehow(prompt)
    prompt = gen.send(user_input)
```

### Quick Simulation

Use `quick_play()` to simulate a single round programmatically:

```python
controller = BlackjackGameController()
result = controller.quick_play(bet=100, actions=["hit", "stand"])
print(result)
```

---

## 📊 Stats Tracked

- Total hands played, won, lost, pushed
- Number of blackjacks
- Total wagered
- Max bankroll reached
- Session profit/loss
- Win rate %

---

## 🔧 Customization

You can easily customize:

- Bet limits, blackjack payout, shuffle rules via `GameConfig`
- Strategy logic via `BlackjackGameController` or by extending the `BlackjackEngine`
- Integrate your own UI, AI, or modding system by hooking into the `game_session()` generator

---

## 🧠 Example Usage

```python
from BlackjackEngine import BlackjackGameController

controller = BlackjackGameController()
session = controller.game_session()
prompt = next(session)

while prompt['type'] != 'game_over':
    if prompt['type'] == 'bet_input':
        prompt = session.send(100)
    elif prompt['type'] == 'action_input':
        prompt = session.send("stand")
    else:
        prompt = next(session)
```

---

## 📁 File Entry Point

Running the script directly via `python BlackjackEngine.py` will start the CLI game. You can configure the engine at the bottom of the file by modifying the `GameConfig`.

---

## 📜 License

MIT License — free to use and modify.
