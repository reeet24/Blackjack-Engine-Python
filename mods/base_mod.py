from modding import global_dispatcher, global_registry

class BlackjackMod:
    name = "Unnamed Mod"
    version = "0.0.1"
    description = "No description provided."

    def __init__(self):
        self.dispatcher = global_dispatcher
        self.registry = global_registry
        self.register()

    def register(self):
        """Override this to connect to signals."""
        pass

    def unregister(self):
        """Optional: Override to disconnect listeners or cleanup if needed."""
        pass