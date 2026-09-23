from collections import deque, defaultdict
from typing import List, Dict, Optional, Tuple, Callable, ClassVar
from dataclasses import dataclass, field


class Registry:
    def __init__(self):
        self.custom_cards = {}
        self.custom_actions = {}
        self.custom_stats = {}
        self.custom_config = {}
        self.engine = None

    def register_engine(self, engine):
        self.engine = engine

    def register_custom_card(self, card: str, value: int, count_value: int = 0, amount_per_deck: Optional[int] = 4, enum: Optional[Callable] = None):
        self.custom_cards[card] = {
            'value': value,
            'count_value': count_value,
            'amount_per_deck': amount_per_deck
        }
        if enum:
            self.custom_cards[card]['enum'] = enum
    
    def register_custom_game_stat(self, name: str, base_value, value_type):
        self.custom_stats[name] = {
            'base_value': base_value,
            'value_type': value_type,
            'current_value': value_type(base_value)
        }

    def get_custom_game_stat(self, name: str):
        stat = self.custom_stats[name]
        if not stat:
            print(f'Custom Stat "{name}" not registered.')
            return None
        else:
            return stat
    
    def set_custom_game_stat(self, name: str, value):
        stat = self.custom_stats[name]
        if not stat:
            print(f'Custom Stat "{name}" not registered.')
            return None
        else:
            try:
                self.custom_stats[name]['current_value'] = self.custom_stats[name]['value_type'](value)
            except:
                print(f'Unable to set Custom Stat "{name}" to "{value}"')
            return self.custom_stats[name]
        
    def get_game_constants(self):
        if self.engine == None:
            return None
        return self.engine.GameConstants

    def register_custom_action(self, name: str, handler, validator=None):
        if self.engine == None:
            return None
        self.custom_actions[name] = self.engine.CustomAction(name, handler, validator)

    def clear_registry(self):
        self.custom_cards = {}
        self.custom_actions = {}
        self.custom_stats = {}
        self.custom_config = {}

    def push_registry_to_engine(self):
        if self.engine == None:
            return None
        for card, data in self.custom_cards.items():
            self.engine.GameConstants.AddCard(card, data['value'], data['count_value'])


class SignalDispatcher:
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = defaultdict(list)

    def register_engine(self, engine):
        self.engine = engine

    def connect(self, signal_name: str, callback: Callable):
        self._listeners[signal_name].append(callback)

    def disconnect(self, signal_name: str, callback: Callable):
        if callback in self._listeners[signal_name]:
            self._listeners[signal_name].remove(callback)

    def emit(self, signal_name: str, *args, **kwargs):
        for callback in self._listeners[signal_name]:
            callback(*args, **kwargs)

global_registry = Registry()
global_dispatcher = SignalDispatcher()

patched = False

class BlackjackModloader:
    """Handles loading and managing mods for the blackjack game."""
    
    def __init__(self, folder: str):
        self.folder = folder
        self.active_mods = []
        self.load_mods_from_folder(folder)

    def patch_engine(self):
        global patched, create_deck, global_dispatcher, global_registry
        if patched:
            return
        
        import BlackjackEngine as BJE

        original_start_round = BJE.BlackjackGameEngine.start_round
        original_deal_card = BJE.BlackjackGameEngine.deal_card
        original_resolve_round = BJE.BlackjackGameEngine.resolve_round
        original_create_deck = BJE.create_deck
        original_execute_action = BJE.BlackjackGameEngine.execute_action
        original_get_legal_actions = BJE.Hand.get_legal_actions
        original_shuffle_deck = BJE.BlackjackGameEngine.shuffle_deck
        original_value = BJE.Hand.value
        original_print_stats = BJE.BlackjackCLI.print_statistics

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
            single_deck = base_cards * 4

            for card, data in global_registry.custom_cards.items():
                if 'amount_per_deck' in data:
                    single_deck.extend([card] * data['amount_per_deck'])
                else:
                    single_deck.append(card)

            final_deck = deque(single_deck * num_decks)
            global_dispatcher.emit('deck_created', results=final_deck)
            return final_deck

        def patched_execute_action(self, hand_index, action):
            hand = self.player_hands[hand_index]
            if action in global_registry.custom_actions:
                custom = global_registry.custom_actions[action]
                if custom.validator(hand):
                    return custom.handler(self, hand_index)
                else:
                    print(f"Action '{action}' is not currently valid.")
                    return False
            return original_execute_action(self, hand_index, action)

        def patched_get_legal_actions(self, bankroll):
            actions = original_get_legal_actions(self, bankroll)
            for name, custom in global_registry.custom_actions.items():
                if custom.validator(self) and (name not in actions):
                    actions.append(name)
            return actions
        
        def patched_value(self):
            value = original_value(self)
            for card in self.cards:
                if card in global_registry.custom_cards and "enum" in global_registry.custom_cards[card]:
                    value += global_registry.custom_cards[card]["enum"](value)
            global_dispatcher.emit('hand_value_calculated', hand=self, value=value)
            return value
        
        def patched_print_stats(self):
            original_print_stats(self)
            print(f"\n{'='*50}")
            print("📊 MODDED STATISTICS:")
            stats = global_registry.custom_stats
            for stat, val in stats.items():
                print(f"{stat}: {val}")


        BJE.BlackjackGameEngine.start_round = patched_start_round
        BJE.BlackjackGameEngine.deal_card = patched_deal_card
        BJE.BlackjackGameEngine.resolve_round = patched_resolve_round
        BJE.BlackjackGameEngine.execute_action = patched_execute_action
        BJE.create_deck = patched_create_deck
        BJE.Hand.get_legal_actions = patched_get_legal_actions
        BJE.BlackjackGameEngine.shuffle_deck = patched_shuffle_deck
        BJE.Hand.value = patched_value
        BJE.BlackjackCLI.print_statistics = patched_print_stats

        patched = True

        return BJE
    
    def load_mod(self, name, current_working_directory: str = 'mods'):
        global global_dispatcher, global_registry
        """Load a mod by name from the specified directory."""
        import importlib
        try:
            module = importlib.import_module(f'{current_working_directory}.{name}')
            mod_class = getattr(module, name)
            if hasattr(mod_class, 'BlackjackMod'):
                mod_instance = mod_class(global_dispatcher, global_registry)
                self.active_mods.append(mod_instance)
                print(f'Mod {name} loaded successfully.')
                return mod_instance
            else:
                print(f'Mod {name} does not inherit from BlackjackMod.')
        except Exception as e:
            print(f'Error loading mod {name}: {e}')
        return None

    def load_mods_from_folder(self, folder: str ='mods'):
        
        import os
        self.active_mods.clear()
        for filename in os.listdir(folder):
            if os.path.isdir(os.path.join(folder, filename)) and not filename.startswith('__'):
                print(f'Loading mod folder: {filename}')
                self.load_mods_from_folder(f'{folder}/{filename}')
                continue

            if filename.endswith('.py') and filename != 'base_mod.py':
                print(f'Loading mod: {filename}')
                module_name = filename[:-3]
                module_dir = folder.replace('/', '.')
                self.load_mod(module_name, module_dir)
        
        global_registry.push_registry_to_engine()

    def get_loaded_mods(self):
        return [
            {
                'name': mod.name,
                'version': mod.version,
                'description': mod.description
            }
            for mod in self.active_mods
        ]

    def unload_all_mods(self): 
        for mod in self.active_mods:
            if hasattr(mod, 'unregister'):
                try:
                    mod.unregister()
                except Exception as e:
                    print(f"Error during mod unregister: {e}")
        self.active_mods.clear()
        global_registry.clear_registry()

if __name__ == "__main__":

    modloader = BlackjackModloader('modsNew')
    patched_engine = modloader.patch_engine()
    global_dispatcher.register_engine(patched_engine)
    global_registry.register_engine(patched_engine)
    global_registry.push_registry_to_engine()
    print(patched)

    if not patched_engine:
        raise Exception("Failed to patch engine")

    print(patched_engine.GameConstants.CARD_VALUES)
    print(patched_engine.GameConstants.HI_LO_VALUES)
    print("Loaded mods:", modloader.get_loaded_mods())

    config = patched_engine.GameConfig(
        num_decks=1,
        starting_bankroll=1000,
        min_bet=1,
        max_bet=10000000,
        blackjack_payout=1.5
    )

    cli = patched_engine.BlackjackCLI(config)
    cli.play_game()