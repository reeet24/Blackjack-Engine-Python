from mods.base_mod import BlackjackMod
from mod_loader import Utilities

class ExampleMod(BlackjackMod):
    name = "Example Mod"
    version = "1.0.0"
    description = "An example mod template."

    def register(self):
        self.dispatcher.connect('round_started', self.on_round_start)
        self.dispatcher.connect('card_dealt', self.on_card_dealt)
        self.dispatcher.connect('deck_shuffled', self.on_deck_shuffle)

        Utilities.register_custom_card('-2', value=-2, count_value=1)

        Utilities.register_custom_action('lucky_draw', self.draw_ace, self.can_draw_ace)

        print(f'ExampleMod Loaded!')

    def draw_ace(engine, hand_index):
        engine.player_hands[hand_index].cards.append("A")
        print("💫 You magically drew an Ace!")
        return True
    
    def can_draw_ace(engine, hand_index):
        return len(engine.player_hands[hand_index].cards) == 2

    def unregister(self):
        self.dispatcher.disconnect('round_started', self.on_round_start)
        self.dispatcher.disconnect('card_dealt', self.on_card_dealt)
        print(f'ExampleMod Unloaded!')

    def on_round_start(self, bet, engine):
        print(f"ExampleMod: A new round has begun! Bet placed: ${bet}")

    def on_card_dealt(self, card, engine):
        print(f"ExampleMod: A {card} was dealt!")

    def on_deck_shuffle(self, deck, engine):
        print(f"ExampleMod: Deck '{deck}' has been shuffled")