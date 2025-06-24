from collections import defaultdict
from typing import Callable, Dict, List

class CustomAction:
    def __init__(self, name: str, handler, validator=None):
        self.name = name
        self.handler = handler
        self.validator = validator or (lambda engine, hand_index: True)

class Registry:
    def __init__(self):
        self.custom_cards = {}
        self.custom_actions = {}
        self.custom_stats = {}
        self.custom_config = {}
        self.engine = None

    def register_custom_card(self, card: str, value: int, count_value: int = 0):
        self.custom_cards[card] = {
            'value': value,
            'count_value': count_value
        }
    
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
        return self.engine.GameConstants

    def register_custom_action(self, name: str, handler, validator=None):
        self.custom_actions[name] = CustomAction(name, handler, validator)

    def clear_registry(self):
        self.custom_cards = {}
        self.custom_actions = {}
        self.custom_stats = {}
        self.custom_config = {}

    def set_engine(self, engine):
        self.engine = engine

    def push_registry_to_engine(self):

        if not self.engine:
            print(f'No engine loaded.')
            return

        for card, data in self.custom_cards.items():
            self.engine.GameConstants.CARD_VALUES[card] = data['value']
            self.engine.GameConstants.HI_LO_VALUES[card] = data['count_value']

class SignalDispatcher:
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = defaultdict(list)

    def connect(self, signal_name: str, callback: Callable):
        self._listeners[signal_name].append(callback)

    def disconnect(self, signal_name: str, callback: Callable):
        if callback in self._listeners[signal_name]:
            self._listeners[signal_name].remove(callback)

    def emit(self, signal_name: str, *args, **kwargs):
        for callback in self._listeners[signal_name]:
            callback(*args, **kwargs)

global_dispatcher = SignalDispatcher()
global_registry = Registry()