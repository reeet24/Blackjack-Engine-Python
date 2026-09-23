from mods.base_mod import BlackjackMod

class wildcards(BlackjackMod):
    name = "Wildcard Mod"
    version = "1.0.0"
    description = "A mod that adds various new cards."
    BlackjackMod = BlackjackMod

    def register(self):

        self.registry.register_custom_card('-2', value=-2, count_value=1)
        self.registry.register_custom_card('JOKER', value=0, count_value=-1)

        self.registry.register_custom_action('use_joker', self.use_joker, self.can_use_joker)
        self.registry.register_custom_action('hit', self.hit, self.can_hit)

        print(f'Wildcards Loaded!')

    def hit(self, engineSelf, hand_index):
        hand = engineSelf.player_hands[hand_index]
        print(hand)
        card = engineSelf.deal_card()
        hand.cards.append(card)
        if (hand.is_bust()):
            if "JOKER" not in hand.cards:
                hand.finished = True
            else:
                hand.cards.pop(len(hand.cards)-1)
                hand.cards.remove('JOKER')
        elif (hand.value == 21):
            hand.finished = True

        return True
    
    def can_hit(self, hand_self):
        return True

    def use_joker(self, engineSelf, hand_index):
        hand_value = engineSelf.player_hands[hand_index].value()
        values = self.registry.get_game_constants().CARD_VALUES
        value = str(21 - hand_value)

        if value in values:
            engineSelf.player_hands[hand_index].cards.remove('JOKER')
            engineSelf.deck.remove(value)
            engineSelf.player_hands[hand_index].cards.append(value)
            print(f"💫 You magically drew an {value}!")
            return True
        elif int(value) > 10 or int(value) == 1:
            engineSelf.player_hands[hand_index].cards.remove('JOKER')
            engineSelf.deck.remove('A')
            engineSelf.player_hands[hand_index].cards.append("A")
            print(f"💫 You magically drew an Ace!")
            return True
        else:
            print(f'Unable to draw card "{value}"')
            return True
    
    def can_use_joker(self, handSelf):
        return ('JOKER' in handSelf.cards)

    def unregister(self):
        pass
