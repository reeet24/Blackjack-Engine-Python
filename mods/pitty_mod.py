from mods.base_mod import BlackjackMod
import random
import math

class PittyMod(BlackjackMod):
    name = "Pitty Mod"
    version = "1.0.0"
    description = "An example mod template."

    def register(self):
        self.dispatcher.connect('round_resolved', self.on_round_resolved)

        self.registry.register_custom_game_stat('Pitty', 0, int)

        self.registry.register_custom_action("hit", self.hit, self.can_hit)
        self.registry.register_custom_action('lucky_draw', self.draw_ace, self.can_draw_ace)

        print(f'ExampleMod Loaded!')

    def can_hit(self, handSelf):
        return True

    def hit(self, engineSelf, hand_index):
        #randomSeed = random.randint(1,3)
        pitty = self.registry.get_custom_game_stat('Pitty')['current_value'] # type: ignore
        hand = engineSelf.player_hands[hand_index]
        print(hand)
        card = engineSelf.deal_card()
        hand.cards.append(card)
        if (hand.is_bust()):
            hand_value = engineSelf.player_hands[hand_index].value()
            value = (hand_value - 21) 
            if pitty > (value ):
                hand.cards.pop(len(hand.cards)-1)
                hand_value = engineSelf.player_hands[hand_index].value()
                cardValue = ((21 - hand_value))
                if cardValue < 1:
                    cardValue = "A"
                card = engineSelf.deal_set_card(str(cardValue))
                hand.cards.append(card)
                print("I pitty you...")
            else:
                hand.finished = True
        elif (hand.value == 21):
            hand.finished = True

        return True

    def draw_ace(self, engineSelf, hand_index):
        hand_value = engineSelf.player_hands[hand_index].value()
        values = self.registry.get_game_constants().CARD_VALUES
        value = str(21 - hand_value)

        if value in values:
            engineSelf.deck.remove(value)
            engineSelf.player_hands[hand_index].cards.append(value)
            print(f"💫 You magically drew an {value}!")
            return True
        elif int(value) > 10:
            engineSelf.deck.remove('A')
            engineSelf.player_hands[hand_index].cards.append("A")
            print(f"💫 You magically drew an Ace!")
            return True
        else:
            print(f'Unable to draw card "{value}"')
            return True
    
    def can_draw_ace(self, handSelf):
        pitty = self.registry.get_custom_game_stat('Pitty')['current_value'] # type: ignore
        return (len(handSelf.cards) == 2) and (pitty >= 10)

    def unregister(self):
        self.dispatcher.disconnect('round_resolved', self.on_round_resolved)
        print(f'ExampleMod Unloaded!')
    
    def on_round_resolved(self, results, engine):
        pitty = self.registry.get_custom_game_stat('Pitty')['current_value'] # type: ignore
        if results[0]['result'] == 'bust':
            self.registry.set_custom_game_stat("Pitty", pitty + 1)
        elif results[0]['result'] == 'lose':
            self.registry.set_custom_game_stat("Pitty", pitty + 2)
        elif results[0]['result'] == 'win':
            self.registry.set_custom_game_stat("Pitty", pitty - 1)
        elif results[0]['result'] == 'blackjack':
            self.registry.set_custom_game_stat("Pitty", 0)
        print(f"ExampleMod: Round ended with results: '{results}' ")