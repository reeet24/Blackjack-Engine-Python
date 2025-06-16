import unittest
import BlackjackEngine

class TestGameFlow(unittest.TestCase):
    def setUp(self):
        self.engine = BlackjackEngine.BlackjackGameEngine()
        self.state = self.engine.start_set_round([BlackjackEngine.Hand(['5', '5'], 10)],['A','J'],500)

    def test_player_starts_with_two_cards(self):
        player_hand = self.engine.player_hands[0]
        self.assertEqual(len(player_hand.cards), 2)

    def test_dealer_has_two_cards(self):
        self.assertEqual(len(self.engine.dealer_hand), 2)
    
    def test_player_hand_value(self):
        self.assertEqual(self.engine.player_hands[0].value(),10)
    
    def test_player_is_blackjack(self):
        self.assertEqual(self.engine.player_hands[0].is_blackjack(), False)
    
    def test_player_can_split(self):
        self.assertEqual(self.engine.player_hands[0].can_split(), True)
    
    def test_player_can_double(self):
        self.assertEqual(self.engine.player_hands[0].can_double(self.engine.bankroll), False)
    
    def test_player_can_surrender(self):
        self.assertEqual(self.engine.player_hands[0].can_surrender(), True)

    def test_player_hit(self):
        self.assertEqual(self.engine.execute_action(0,"hit"), True)

    def test_player_stand(self):
        self.assertEqual(self.engine.execute_action(0,"stand"), True)

if __name__ == '__main__':
    unittest.main()
