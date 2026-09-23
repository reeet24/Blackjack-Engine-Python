import unittest
from BlackjackEngine import create_deck

class TestDeck(unittest.TestCase):
    def test_deck_initialization(self):
        deck = create_deck(1)
        self.assertEqual(len(deck), 52)

if __name__ == '__main__':
    unittest.main()
