
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

| Class                     | Description |
|---------------------------|-------------|
| `GameConfig`              | Game settings like decks, bets, payout, etc. |
| `GameStats`               | Tracks session statistics |
| `GameConstants`           | Card values, count tables, etc. |
| `Hand`                    | Represents and manages a blackjack hand |
| `BlackjackGameEngine`     | The core engine with dealer/player logic |
| `BlackjackGameController` | Generator-based interface for GUIs/bots |
| `BlackjackCLI`            | CLI-based game driver |

---

## 🎮 How It Works

1. Player places a bet.
2. Cards are dealt to the dealer and player.
3. The player chooses legal actions based on hand state.
4. The dealer plays out their hand.
5. Results are calculated, payouts distributed, and stats updated.

---

## 🧩 Integration Options

### CLI (Terminal Game)

```python
from BlackjackEngine import BlackjackCLI

cli = BlackjackCLI()
cli.play_game()
```

### Programmatic (Bot, GUI, AI)

```python
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

### Quick Simulation

```python
result = controller.quick_play(bet=50, actions=["hit", "stand"])
print(result)
```

---

## 📊 Stats Tracked

- Hands played, won, lost, pushed
- Blackjacks
- Total wagered
- Maximum bankroll achieved
- Session profit/loss
- Win rate %

---

## 🔧 Customization

- Adjust `GameConfig` to change game rules
- Use controller’s generator loop to make your own UIs or AI agents
- Inject mods via the modding system (below)

---

## 🔌 Modding API

The Blackjack engine includes built-in support for mods, enabling you to hook into gameplay events, register new card types, and even introduce new player actions.

### 🔧 How Modding Works

Mods are dynamically loaded from the `mods/` folder using the `load_mods_from_folder()` function. They can patch the engine, add new behavior, or override existing rules.

### 🧩 Key Concepts

- **Signals/Events** — Mods can hook into core gameplay signals like:
  - `round_started`
  - `card_dealt`
  - `round_resolved`

- **Custom Cards** — Add new card faces and assign them game values:

  ```python
  register_custom_card('🔥', value=10, count_value=-1)
  ```

- **Custom Actions** — Register new player actions with custom handlers:

  ```python
  def handle_flip(engine, hand_index):
      print("🃏 You flipped your cards!")
      return True

  register_custom_action('flip', handler=handle_flip)
  ```

### 📁 Example Mod Structure

Each mod should define a class that inherits from a shared `BlackjackMod` base and registers functionality in its constructor.

```python
# mods/my_mod.py

class MyFunMod(BlackjackMod):
    name = "Fun Mod"
    version = "1.0"
    description = "Adds a silly action"

    def __init__(self):
        register_custom_action('flip', handler=self.handle_flip)

    def handle_flip(self, engine, hand_index):
        print("You flipped your cards in frustration!")
        return True
```

### 🧪 Development Flow

1. Drop your `.py` mod files in the `mods/` folder.
2. Call `load_mods_from_folder()` to apply patches and register content.
3. Use `get_loaded_mods()` to see active mods.
4. Use `unload_all_mods()` to clear everything.

### 🧼 Engine Patching

The following engine methods are patched during mod load:

- `start_round()` – emits `round_started`
- `deal_card()` – emits `card_dealt`
- `resolve_round()` – emits `round_resolved`
- `create_deck()` – injects custom cards
- `execute_action()` – supports custom actions
- `get_legal_actions()` – adds modded actions to UI

### Example Entry Point

```python
if __name__ == "__main__":
    Engine = load_mods_from_folder()

    cli = Engine.BlackjackCLI(Engine.GameConfig())
    cli.play_game()
```

---

## 📜 License

MIT License — free to use and modify.
