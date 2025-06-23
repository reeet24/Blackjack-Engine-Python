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

    def register_custom_card(self, card: str, value: int, count_value: int = 0):
        self.custom_cards[card] = {
            'value': value,
            'count_value': count_value
        }

    def register_custom_action(self, name: str, handler, validator=None):
        self.custom_actions[name] = CustomAction(name, handler, validator)
        print(self.custom_actions)

    def clear_registry(self):
        self.custom_cards = {}
        self.custom_actions = {}
        self.custom_stats = {}
        self.custom_config = {}

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