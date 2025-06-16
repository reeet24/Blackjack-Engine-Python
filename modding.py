from collections import defaultdict
from typing import Callable, Dict, List

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