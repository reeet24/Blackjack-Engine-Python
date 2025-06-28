# Blackjack Engine Python

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Build Status](https://img.shields.io/github/actions/workflow/status/reeet24/Blackjack-Engine-Python/ci.yml?branch=main)](https://github.com/reeet24/Blackjack-Engine-Python/actions)

A modular, extensible, object-oriented Blackjack engine written in Python, complete with built-in card-counting, statistics tracking, legal move validation, and both CLI and programmable interfaces. Designed to serve as the backbone for bots, GUIs, AI agents, and more.

---

## Table of Contents

1. [Key Features](#key-features)
2. [Installation](#installation)
3. [Quick Start](#quick-start)

   * [CLI Usage](#cli-usage)
   * [Programmatic Usage](#programmatic-usage)
4. [Core Concepts & Code Structure](#core-concepts--code-structure)
5. [Modding API](#modding-api)
6. [Statistics & Logging](#statistics--logging)
7. [Testing & CI](#testing--ci)
8. [Contributing](#contributing)
9. [License](#license)

---

## Key Features

* **Full Blackjack Rule Support**

  * Double down, split (including resplits), surrender
  * Customizable blackjack payouts
  * Soft/hard hand logic and multiple deck shoe

* **Card Counting (Hi-Lo)**

  * Running count & true count calculations
  * Built-in support for count-based betting strategies

* **Bankroll & Bet Validation**

  * Minimum/maximum bet enforcement
  * Bankroll tracking with automated bet adjustments

* **Generator-Based Controller**

  * Easily drive GUIs, bots, or AI agents via a coroutine interface

* **CLI Interface**

  * Interactive text-based play with real-time statistics

* **Quick Play Simulation**

  * Fast forward mode for automated strategies

* **Extensible Modding API**

  * Hook into game events, register new card types, define custom actions

* **Session Statistics**

  * Hands played, won, lost, pushed
  * Blackjacks, total wagered, max bankroll, profit/loss, win rate

---

## Installation

```bash
# Clone the repository
git clone https://github.com/reeet24/Blackjack-Engine-Python.git
cd Blackjack-Engine-Python

# (Optional) Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
```

*No external dependencies* beyond Python 3.8+. Everything lives in the standard library.

---

## Quick Start

### CLI Usage

```bash
python BlackjackEngine.py
```

The CLI will prompt you to:

1. Place a bet
2. Select legal actions (`hit`, `stand`, `double`, `split`, `surrender`, etc.)
3. View running statistics at any time

### Programmatic Usage

```python
from BlackjackEngine import BlackjackGameController

controller = BlackjackGameController()
session = controller.game_session()

prompt = next(session)
while prompt['type'] != 'game_over':
    if prompt['type'] == 'bet_input':
        # adjust based on your strategy
        prompt = session.send(100)
    elif prompt['type'] == 'action_input':
        # choose from prompt['legal_actions']
        prompt = session.send("stand")
    else:
        prompt = next(session)

# Final result returned when type == 'game_over'
print("Session summary:", prompt['summary'])
```

For quick simulations:

```python
result = controller.quick_play(bet=50, actions=["hit", "stand"])
print(result)
```

---

## Core Concepts & Code Structure

| Class/Module              | Responsibility                                   |
| ------------------------- | ------------------------------------------------ |
| `GameConfig`              | Defines decks, payouts, bet limits, game rules   |
| `GameStats`               | Accumulates and reports session metrics          |
| `GameConstants`           | Card values, count tables, legal-action mappings |
| `Hand`                    | Encapsulates a player or dealer hand             |
| `BlackjackGameEngine`     | Core engine: deals cards, resolves rounds        |
| `BlackjackGameController` | Generator-based interface for driving play loops |
| `BlackjackCLI`            | Text-based command-line driver                   |

---

## Modding API

Dynamically load custom “mods” to inject new behavior:

1. **Drop** Python files into `mods/`.

2. **Load** them via the entry point:

   ```python
   from mod_loader import load_mods_from_folder

   Engine = load_mods_from_folder()
   cli = Engine.BlackjackCLI(Engine.GameConfig())
   cli.play_game()
   ```

3. **Hooks & Events**

   * `round_started`, `card_dealt`, `round_resolved`, etc.
   * Use `register_custom_card(face, value, count_value)`
   * Use `register_custom_action(name, handler, validator=None)`

4. **Example Mod Skeleton**

   ```python
   # mods/my_flip_mod.py
   from modding import BlackjackMod

   class FlipMod(BlackjackMod):
       name = "Flip-Action Mod"
       version = "1.0"
       description = "Adds a 'flip' action"

       def __init__(self):
           self.registry.register_custom_action('flip', handler=self.flip_handler)

       def flip_handler(self, engine, hand_index):
           print("You flipped your cards in frustration!")
           return True
   ```

5. **Management**

   * `get_loaded_mods() → List[BlackjackMod]`
   * `unload_all_mods()` to reset

---

## Statistics & Logging

* **Built-In Stats**: Tracks hands played/won/lost/pushed, blackjacks, total wagered, peak bankroll, profit/loss, win rate.
* **Export**: Customize or extend `GameStats` to serialize to CSV/JSON for offline analysis.
* **Visualization**: Integrate with plotting libraries to chart performance over time.

---

## Testing & CI

* **Unit Tests**: `run_tests.py` runs the test suite in `tests/`.
* **Continuous Integration**: A GitHub Actions workflow (`.github/workflows/ci.yml`) automatically runs linting and tests on every push.

```bash
# Run all tests
python run_tests.py
```

---

## Contributing

1. **Fork** the repo
2. **Create** a feature branch (`git checkout -b feature/YourFeature`)
3. **Commit** your changes with clear messages
4. **Push** and **Open** a Pull Request
5. **Review** & **Merge**

Please follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines and include tests for new functionality.

---

## License

This project is released under the **MIT License**. See [LICENSE](LICENSE) for full terms.
Feel free to fork, modify, and extend for your own Blackjack experiments and projects.
