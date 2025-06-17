import importlib
import os
import BlackjackEngine
from modding import global_dispatcher
import random
from collections import deque

patched = False
active_mods = []
custom_cards = {}
custom_actions = {}
custom_stats = {}
custom_config = {}

class CustomAction:
    def __init__(self, name: str, handler, validator=None):
        self.name = name
        self.handler = handler
        self.validator = validator or (lambda engine, hand_index: True)

class Utilities:
    def __init__(self):
        pass

    def register_custom_card(card: str, value: int, count_value: int = 0):
        custom_cards[card] = {
            'value': value,
            'count_value': count_value
        }
        BlackjackEngine.GameConstants.CARD_VALUES[card] = value
        BlackjackEngine.GameConstants.HI_LO_VALUES[card] = count_value

    def register_custom_action(name: str, handler, validator=None):
        custom_actions[name] = CustomAction(name, handler, validator)

def patch_engine():
    global patched
    if patched:
        return

    original_start_round = BlackjackEngine.BlackjackGameEngine.start_round
    original_deal_card = BlackjackEngine.BlackjackGameEngine.deal_card
    original_resolve_round = BlackjackEngine.BlackjackGameEngine.resolve_round
    original_create_deck = BlackjackEngine.create_deck
    original_execute_action = BlackjackEngine.BlackjackGameEngine.execute_action
    original_get_legal_actions = BlackjackEngine.Hand.get_legal_actions
    original_shuffle_deck = BlackjackEngine.BlackjackGameEngine.shuffle_deck

    def patched_start_round(self, bet):
        result = original_start_round(self, bet)
        global_dispatcher.emit('round_started', bet=bet, engine=self)
        return result

    def patched_deal_card(self):
        card = original_deal_card(self)
        global_dispatcher.emit('card_dealt', card=card, engine=self)
        return card

    def patched_resolve_round(self):
        results = original_resolve_round(self)
        global_dispatcher.emit('round_resolved', results=results, engine=self)
        return results
    
    def patched_shuffle_deck(self):
        original_shuffle_deck(self)
        global_dispatcher.emit('deck_shuffled', self.deck, engine=self)

    def patched_create_deck(num_decks: int):
        base_cards = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        all_cards = base_cards + list(custom_cards.keys())
        single_deck = all_cards * 4
        final_deck = deque(single_deck * num_decks)
        global_dispatcher.emit('deck_created', results=final_deck)
        return final_deck

    def patched_execute_action(self, hand_index, action):
        if action in custom_actions:
            custom = custom_actions[action]
            if custom.validator(self, hand_index):
                return custom.handler(self, hand_index)
            else:
                print(f"Action '{action}' is not currently valid.")
                return False
        return original_execute_action(self, hand_index, action)

    def patched_get_legal_actions(self, bankroll):
        actions = original_get_legal_actions(self, bankroll)
        for name, custom in custom_actions.items():
            if custom.validator(self.owner_engine, self.owner_index):
                actions.append(name)
        return actions

    BlackjackEngine.BlackjackGameEngine.start_round = patched_start_round
    BlackjackEngine.BlackjackGameEngine.deal_card = patched_deal_card
    BlackjackEngine.BlackjackGameEngine.resolve_round = patched_resolve_round
    BlackjackEngine.BlackjackGameEngine.execute_action = patched_execute_action
    BlackjackEngine.create_deck = patched_create_deck
    BlackjackEngine.Hand.get_legal_actions = patched_get_legal_actions
    BlackjackEngine.BlackjackGameEngine.shuffle_deck = patched_shuffle_deck

    patched = True



def load_mods_from_folder(folder='mods'):
    patch_engine()
    active_mods.clear()
    for filename in os.listdir(folder):
        if filename.endswith('.py') and filename != 'base_mod.py':
            module_name = filename[:-3]
            module = importlib.import_module(f'{folder}.{module_name}')
            for attr in dir(module):
                obj = getattr(module, attr)
                if isinstance(obj, type) and hasattr(obj, '__bases__') and any('BlackjackMod' in str(base) for base in obj.__bases__):
                    instance = obj()
                    active_mods.append(instance)
 
    return BlackjackEngine

def get_loaded_mods():
    return [
        {
            'name': mod.name,
            'version': mod.version,
            'description': mod.description
        }
        for mod in active_mods
    ]

def unload_all_mods(): 
    for mod in active_mods:
        if hasattr(mod, 'unregister'):
            try:
                mod.unregister()
            except Exception as e:
                print(f"Error during mod unregister: {e}")
    active_mods.clear()
    custom_cards.clear()
    custom_actions.clear()

if __name__ == "__main__":
    Engine = load_mods_from_folder()

    print(Engine.GameConstants.CARD_VALUES)

    config = Engine.GameConfig(
        num_decks=1,
        starting_bankroll=1000,
        min_bet=10,
        max_bet=500,
        blackjack_payout=1.5
    )

    cli = Engine.BlackjackCLI(config)
    cli.play_game()