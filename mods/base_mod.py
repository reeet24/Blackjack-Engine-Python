from modding import global_dispatcher

class BlackjackMod:
    name = "Unnamed Mod"
    version = "0.0.1"
    description = "No description provided."

    def __init__(self):
        self.dispatcher = global_dispatcher
        self.register()

    def register(self):
        """Override this to connect to signals."""
        pass

    def unregister(self):
        """Optional: Override to disconnect listeners or cleanup if needed."""
        pass