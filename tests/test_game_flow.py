import unittest
import BlackjackEngine

class TestGameFlow(unittest.TestCase):
    def setUp(self):
        self.controller = BlackjackEngine.BlackjackGameController()
        self.results = self.controller.quick_play(10,['stand'])

    def test_game_starts_with_two_cards(self):
        player_hand = self.controller.engine.player_hands[0]
        self.assertEqual(len(player_hand.cards), 2)

    def test_dealer_has_two_cards(self):
        self.assertEqual(len(self.controller.engine.dealer_hand), 2)

    def test_game_ends_properly(self):
        # Stand immediately to force game end
        self.assertTrue(self.results['success'])

if __name__ == '__main__':
    unittest.main()
