import unittest
import mod_loader
from BlackjackEngine import GameConfig

class TestModLoader(unittest.TestCase):
    def setUp(self):
        self.Modded_engine = mod_loader.load_mods_from_folder()
        self.engine = self.Modded_engine.BlackjackGameEngine()
        self.state = self.engine.start_set_round([self.Modded_engine.Hand(['Q', 'K'], 10)],['A','J'],500)
        mod_loader.global_registry.set_custom_game_stat("Pitty", 100)
        print(mod_loader.global_registry.get_custom_game_stat("Pitty"))

    def test_modded_engine_initialization(self):
        self.assertEqual(self.Modded_engine.GameConfig, GameConfig)
    
    def test_modded_player_starts_with_two_cards(self):
        player_hand = self.engine.player_hands[0]
        self.assertEqual(len(player_hand.cards), 2)

    def test_modded_dealer_has_two_cards(self):
        self.assertEqual(len(self.engine.dealer_hand), 2)
    
    def test_modded_player_hand_value(self):
        self.assertEqual(self.engine.player_hands[0].value(),20)
    
    def test_modded_player_is_blackjack(self):
        self.assertEqual(self.engine.player_hands[0].is_blackjack(), False)
    
    def test_modded_player_can_split(self):
        self.assertEqual(self.engine.player_hands[0].can_split(), True)
    
    def test_modded_player_can_double(self):
        self.assertEqual(self.engine.player_hands[0].can_double(self.engine.bankroll), False)
    
    def test_modded_player_can_surrender(self):
        self.assertEqual(self.engine.player_hands[0].can_surrender(), True)

    def test_modded_player_hit(self):
        hitResult = self.engine.execute_action(0,"hit")
        self.assertEqual(hitResult and self.engine.player_hands[0].value() == 21, True)

    def test_modded_player_stand(self):
        self.assertEqual(self.engine.execute_action(0,"stand"), True)

if __name__ == '__main__':
    unittest.main()
