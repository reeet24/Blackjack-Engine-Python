import random
from collections import deque
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import logging
 
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class GameConfig:
    """Configuration settings for the blackjack game."""
    num_decks: int = 6
    starting_bankroll: int = 500
    min_bet: int = 5
    max_bet: int = 500
    blackjack_payout: float = 1.5
    min_cards_before_shuffle: int = 15

@dataclass
class GameStats:
    """Statistics tracking for game performance."""
    hands_played: int = 0
    hands_won: int = 0
    hands_lost: int = 0
    hands_pushed: int = 0
    blackjacks: int = 0
    total_wagered: int = 0
    max_bankroll: int = 0
    current_session_profit: int = 0

class GameConstants:
    """Constants used throughout the game."""
    CARD_VALUES = {
        '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
        '7': 7, '8': 8, '9': 9, '10': 10,
        'J': 10, 'Q': 10, 'K': 10, 'A': 11
    }
    
    HI_LO_VALUES = {
        '2': 1, '3': 1, '4': 1, '5': 1, '6': 1,
        '7': 0, '8': 0, '9': 0,
        '10': -1, 'J': -1, 'Q': -1, 'K': -1, 'A': -1
    }
    
    CARDS_PER_DECK = 52
    SOFT_17_THRESHOLD = 17

def create_deck(num_decks: int) -> deque:
    """Create a shuffled deck with the specified number of standard decks."""
    single_deck = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'] * 4
    return deque(single_deck * num_decks)

class Hand:
    """Represents a player's hand in blackjack."""
    
    def __init__(self, cards: List[str], bet: int):
        self.cards = cards
        self.bet = bet
        self.finished = False
        self.doubled = False
        self.surrendered = False
        self._cached_value: Optional[int] = None
        self._cards_hash: Optional[int] = None

    def value(self) -> int:
        """Calculate the best possible value of the hand."""
 
        current_hash = hash(tuple(self.cards))
        if self._cached_value is not None and self._cards_hash == current_hash:
            return self._cached_value
        
        val = sum(GameConstants.CARD_VALUES[c] for c in self.cards)
        aces = self.cards.count('A')
        
 
        while val > 21 and aces:
            val -= 10
            aces -= 1
        
        self._cached_value = val
        self._cards_hash = current_hash
        return val

    def is_blackjack(self) -> bool:
        """Check if hand is a natural blackjack."""
        return len(self.cards) == 2 and self.value() == 21

    def is_bust(self) -> bool:
        """Check if hand value exceeds 21."""
        return self.value() > 21

    def can_split(self) -> bool:
        """Check if hand can be split."""
        return (len(self.cards) == 2 and 
                GameConstants.CARD_VALUES[self.cards[0]] == GameConstants.CARD_VALUES[self.cards[1]])

    def can_double(self, bankroll: int) -> bool:
        """Check if hand can be doubled down."""
        return len(self.cards) == 2 and bankroll >= self.bet

    def can_surrender(self) -> bool:
        """Check if hand can be surrendered."""
        return len(self.cards) == 2 and not self.is_blackjack()

    def get_legal_actions(self, bankroll: int) -> List[str]:
        """Get all legal actions for this hand."""
        if self.finished:
            return []
        
        actions = ['hit', 'stand']
        
        if len(self.cards) == 2:
            if self.can_double(bankroll):
                actions.append('double')
            if self.can_split() and bankroll >= self.bet:
                actions.append('split')
            if self.can_surrender():
                actions.append('surrender')
        
        return actions

    def __str__(self) -> str:
        """String representation of the hand."""
        return f"Hand: {self.cards} (Value: {self.value()}, Bet: ${self.bet})"

class BlackjackGameEngine:
    """Core blackjack game engine with card counting support."""
    
    def __init__(self, config: Optional[GameConfig] = None):
        self.config = config or GameConfig()
        self.deck = create_deck(self.config.num_decks)
        random.shuffle(self.deck)
        self.running_count = 0
        self.bankroll = self.config.starting_bankroll
        self.player_hands: List[Hand] = []
        self.dealer_hand: List[str] = []
        self.card_history: List[str] = []
        self.round_complete = False
        self.stats = GameStats()
        self.stats.max_bankroll = self.bankroll
        
        logger.info(f"Game initialized with {self.config.num_decks} decks, ${self.bankroll} bankroll")

    def shuffle_deck(self) -> None:
        """Shuffle the deck and reset the running count."""
        self.deck = create_deck(self.config.num_decks)
        random.shuffle(self.deck)
        self.running_count = 0
        logger.info("Deck shuffled, running count reset")

    def deal_card(self) -> str:
        """Deal a single card and update the running count."""
        if len(self.deck) < self.config.min_cards_before_shuffle:
            self.shuffle_deck()
        
        if not self.deck:
            raise RuntimeError("Deck is empty after shuffle")
        
        card = self.deck.popleft()
        self.running_count += GameConstants.HI_LO_VALUES.get(card, 0)
        self.card_history.append(card)
        return card
    
    def deal_set_card(self, card: str = "A") -> str:
        """Deal a single set card and update the running count."""
        if len(self.deck) < self.config.min_cards_before_shuffle:
            self.shuffle_deck()
        
        if not self.deck:
            raise RuntimeError("Deck is empty after shuffle")
        
        self.deck.remove(card)
        self.running_count += GameConstants.HI_LO_VALUES.get(card, 0)
        self.card_history.append(card)
        return card

    def get_true_count(self) -> float:
        """Calculate the true count (running count / decks remaining)."""
        decks_remaining = max(len(self.deck) / GameConstants.CARDS_PER_DECK, 0.5)
        return round(self.running_count / decks_remaining, 2)

    def can_take_insurance(self) -> bool:
        """Check if insurance bet is available."""
        return (len(self.dealer_hand) >= 2 and 
                GameConstants.CARD_VALUES[self.dealer_hand[1]] == 11)  # Dealer shows Ace

    def validate_bet(self, bet: int) -> Tuple[bool, str]:
        """Validate if a bet is legal."""
        if bet <= 0:
            return False, "Bet must be positive"
        if bet < self.config.min_bet:
            return False, f"Minimum bet is ${self.config.min_bet}"
        if bet > self.config.max_bet:
            return False, f"Maximum bet is ${self.config.max_bet}"
        if bet > self.bankroll:
            return False, "Insufficient funds"
        return True, ""

    def start_round(self, bet: int) -> Dict:
        """Start a new round of blackjack."""
        is_valid, error_msg = self.validate_bet(bet)
        if not is_valid:
            raise ValueError(error_msg)
        
 
        self.bankroll -= bet
        self.stats.total_wagered += bet
        
 
        self.card_history = []
        self.round_complete = False
        
 
        self.dealer_hand = [self.deal_card(), self.deal_card()]
        self.player_hands = [Hand([self.deal_card(), self.deal_card()], bet)]
        
        self.stats.hands_played += 1
        logger.info(f"Round started with bet ${bet}")
        
        return self.get_game_state()
    
    def start_set_round(self, player_hands: list, dealer_hand: list, bet: int) -> Dict:
        """Start a new round of blackjack with set hands. Included for testing."""
        is_valid, error_msg = self.validate_bet(bet)
        if not is_valid:
            raise ValueError(error_msg)
        
 
        self.bankroll -= bet
        self.stats.total_wagered += bet
        
 
        self.card_history = []
        self.round_complete = False
        
 
        self.dealer_hand = dealer_hand
        self.player_hands = player_hands
        
        self.stats.hands_played += 1
        logger.info(f"Round started with bet ${bet}")
        
        return self.get_game_state()

    def execute_action(self, hand_index: int, action: str) -> bool:
        """Execute a player action on the specified hand."""
        if hand_index >= len(self.player_hands):
            return False
        
        hand = self.player_hands[hand_index]
        
        if action == 'hit':
            hand.cards.append(self.deal_card())
            if (hand.is_bust()) or (hand.value == 21):
                hand.finished = True
        
        elif action == 'stand':
            hand.finished = True
        
        elif action == 'double':
            if hand.can_double(self.bankroll):
                self.bankroll -= hand.bet  # Deduct additional bet
                hand.cards.append(self.deal_card())
                hand.bet *= 2
                hand.doubled = True
                hand.finished = True
        
        elif action == 'split':
            if hand.can_split() and self.bankroll >= hand.bet:
                self.bankroll -= hand.bet  # Deduct bet for second hand
                card_value = hand.cards[0]
                
 
                new_hand1 = Hand([card_value, self.deal_card()], hand.bet)
                new_hand2 = Hand([card_value, self.deal_card()], hand.bet)
                
 
                self.player_hands.pop(hand_index)
                self.player_hands.insert(hand_index, new_hand2)
                self.player_hands.insert(hand_index, new_hand1)
        
        elif action == 'surrender':
            if hand.can_surrender():
                hand.surrendered = True
                hand.finished = True
 
                self.bankroll += hand.bet // 2
        
        else:
            return False
        
        return True

    def has_soft_ace(self, hand: List[str]) -> bool:
        """Check if hand has a soft ace (ace counted as 11)."""
        if 'A' not in hand:
            return False
        
        total = sum(GameConstants.CARD_VALUES[c] for c in hand)
        aces = hand.count('A')
        
 
        return total - (aces - 1) * 10 <= 21

    def dealer_play(self) -> None:
        """Execute dealer's turn according to standard rules."""
        while True:
            dealer_value = self.get_hand_value(self.dealer_hand)
            
 
            if (dealer_value < GameConstants.SOFT_17_THRESHOLD or 
                (dealer_value == GameConstants.SOFT_17_THRESHOLD and self.has_soft_ace(self.dealer_hand))):
                self.dealer_hand.append(self.deal_card())
            else:
                break

    def resolve_round(self) -> List[Dict]:
        """Resolve the round and calculate payouts."""
        self.dealer_play()
        self.round_complete = True
        dealer_value = self.get_hand_value(self.dealer_hand)
        dealer_blackjack = self.is_dealer_blackjack()
        
        results = []
        
        for hand in self.player_hands:
            result = {
                'hand': hand.cards[:],
                'bet': hand.bet,
                'result': '',
                'payout': 0
            }
            
            if hand.surrendered:
                result['result'] = 'surrender'
                result['payout'] = 0  # Already handled in execute_action
                
            elif hand.is_blackjack():
                if dealer_blackjack:
                    result['result'] = 'push'
                    result['payout'] = hand.bet  # Return original bet
                else:
                    result['result'] = 'blackjack'
                    result['payout'] = hand.bet + int(self.config.blackjack_payout * hand.bet)
                    self.stats.blackjacks += 1
                    
            elif hand.is_bust():
                result['result'] = 'bust'
                result['payout'] = 0  # Already lost
                
            elif dealer_value > 21:
                result['result'] = 'dealer_bust'
                result['payout'] = hand.bet * 2  # Return bet + winnings
                
            elif hand.value() > dealer_value:
                result['result'] = 'win'
                result['payout'] = hand.bet * 2
                
            elif hand.value() == dealer_value:
                result['result'] = 'push'
                result['payout'] = hand.bet  # Return original bet
                
            else:
                result['result'] = 'lose'
                result['payout'] = 0  # Already lost
            
 
            self.bankroll += result['payout']
            self.stats.max_bankroll = max(self.stats.max_bankroll, self.bankroll)
            
            if result['result'] in ['win', 'blackjack', 'dealer_bust']:
                self.stats.hands_won += 1
            elif result['result'] in ['lose', 'bust']:
                self.stats.hands_lost += 1
            else:
                self.stats.hands_pushed += 1
            
            results.append(result)
        
        self.stats.current_session_profit = self.bankroll - self.config.starting_bankroll
        logger.info(f"Round resolved. Bankroll: ${self.bankroll}")
        
        return results

    def is_dealer_blackjack(self) -> bool:
        """Check if dealer has blackjack."""
        return self.get_hand_value(self.dealer_hand) == 21 and len(self.dealer_hand) == 2

    def get_hand_value(self, hand: List[str]) -> int:
        """Calculate the value of any hand."""
        val = sum(GameConstants.CARD_VALUES[c] for c in hand)
        aces = hand.count('A')
        
        while val > 21 and aces:
            val -= 10
            aces -= 1
        
        return val

    def all_hands_finished(self) -> bool:
        """Check if all player hands are finished."""
        return all(hand.finished for hand in self.player_hands)

    def get_game_state(self) -> Dict:
        """Get the current game state."""
        return {
            'player_hands': [
                {
                    'cards': hand.cards[:],
                    'value': hand.value(),
                    'bet': hand.bet,
                    'finished': hand.finished,
                    'is_blackjack': hand.is_blackjack(),
                    'is_bust': hand.is_bust()
                }
                for hand in self.player_hands
            ],
            'dealer_hand': self.dealer_hand[:],
            'dealer_visible_card': self.dealer_hand[1] if len(self.dealer_hand) > 1 else None,
            'dealer_value': self.get_hand_value(self.dealer_hand) if self.round_complete else None,
            'bankroll': self.bankroll,
            'running_count': self.running_count,
            'true_count': self.get_true_count(),
            'can_take_insurance': self.can_take_insurance(),
            'round_complete': self.round_complete,
            'legal_actions': [
                hand.get_legal_actions(self.bankroll) 
                for hand in self.player_hands
            ],
            'stats': self.stats
        }

class BlackjackGameController:
    """Generator-based controller for easy integration into other scripts."""
    
    def __init__(self, config: Optional[GameConfig] = None):
        self.engine = BlackjackGameEngine(config)
        self.current_state = None
        self.current_hand_index = 0
    
    def game_session(self):
        """
        Main game session generator. Yields dictionaries with game state and input requirements.
        
        Yields:
            dict: Contains 'type', 'state', 'message', and sometimes 'options' or 'validation'
        
        Usage:
            controller = BlackjackGameController()
            game_gen = controller.game_session()
            
            for prompt in game_gen:
                if prompt['type'] == 'bet_input':
                    bet = get_bet_somehow()
                    game_gen.send(bet)
                elif prompt['type'] == 'action_input':
                    action = get_action_somehow() 
                    game_gen.send(action)
 
        """
        
        while self.engine.bankroll >= self.engine.config.min_bet:
 
            bet_prompt = {
                'type': 'bet_input',
                'state': self.engine.get_game_state(),
                'message': f'Enter bet (${self.engine.config.min_bet}-${self.engine.config.max_bet})',
                'validation': {
                    'min': self.engine.config.min_bet,
                    'max': min(self.engine.config.max_bet, self.engine.bankroll),
                    'type': 'int'
                }
            }
            
            bet = yield bet_prompt
            
 
            try:
                bet = int(bet)
                is_valid, error_msg = self.engine.validate_bet(bet)
                if not is_valid:
                    error_prompt = {
                        'type': 'error',
                        'state': self.engine.get_game_state(),
                        'message': error_msg
                    }
                    yield error_prompt
                    continue
            except (ValueError, TypeError):
                error_prompt = {
                    'type': 'error',
                    'state': self.engine.get_game_state(), 
                    'message': 'Invalid bet amount'
                }
                yield error_prompt
                continue
            
 
            try:
                self.current_state = self.engine.start_round(bet)
                
 
                round_start_prompt = {
                    'type': 'round_start',
                    'state': self.current_state,
                    'message': 'Round started'
                }
                yield round_start_prompt
                
 
                self.current_hand_index = 0
                while self.current_hand_index < len(self.engine.player_hands):
                    hand = self.engine.player_hands[self.current_hand_index]
                    
                    while not hand.finished:
 
                        self.current_state = self.engine.get_game_state()
                        
 
                        actions = hand.get_legal_actions(self.engine.bankroll)
                        
                        if not actions:
                            break
                        
 
                        action_prompt = {
                            'type': 'action_input',
                            'state': self.current_state,
                            'hand_index': self.current_hand_index,
                            'message': f'Choose action for hand {self.current_hand_index + 1}',
                            'options': actions
                        }
                        
                        action = yield action_prompt
                        
 
                        if action in actions:
                            success = self.engine.execute_action(self.current_hand_index, action)
                            if success:
 
                                self.current_state = self.engine.get_game_state()
                                
                                action_result_prompt = {
                                    'type': 'action_result',
                                    'state': self.current_state,
                                    'action': action,
                                    'hand_index': self.current_hand_index,
                                    'message': f'Action "{action}" executed'
                                }
                                yield action_result_prompt
                                
 
 
                                if action != 'split':
                                    pass  # Continue with same hand until finished
                                else:
                                    hand = self.engine.player_hands[self.current_hand_index]
                                    continue
                            else:
                                error_prompt = {
                                    'type': 'error',
                                    'state': self.current_state,
                                    'message': 'Action failed'
                                }
                                yield error_prompt
                        else:
                            error_prompt = {
                                'type': 'error',
                                'state': self.current_state,
                                'message': f'Invalid action. Available: {", ".join(actions)}'
                            }
                            yield error_prompt
                    
                    self.current_hand_index += 1
                
 
                results = self.engine.resolve_round()
                final_state = self.engine.get_game_state()
                
 
                round_complete_prompt = {
                    'type': 'round_complete',
                    'state': final_state,
                    'results': results,
                    'message': 'Round completed'
                }
                yield round_complete_prompt
                
            except ValueError as e:
                error_prompt = {
                    'type': 'error',
                    'state': self.engine.get_game_state(),
                    'message': str(e)
                }
                yield error_prompt
                continue
            
 
            if self.engine.bankroll >= self.engine.config.min_bet:
                continue_prompt = {
                    'type': 'continue_input',
                    'state': self.engine.get_game_state(),
                    'message': 'Continue playing?',
                    'options': ['yes', 'no', 'y', 'n']
                }
                
                continue_response = yield continue_prompt
                
                if str(continue_response).lower() not in ['yes', 'y', '1', 'true']:
                    break
            else:
 
                game_over_prompt = {
                    'type': 'game_over',
                    'state': self.engine.get_game_state(),
                    'message': 'Insufficient funds to continue',
                    'reason': 'bankrupt'
                }
                yield game_over_prompt
                break
        
 
        final_prompt = {
            'type': 'game_over',
            'state': self.engine.get_game_state(),
            'message': 'Game session ended',
            'reason': 'completed'
        }
        yield final_prompt
    
    def quick_play(self, bet: int, actions: List[str]):
        """
        Play a single round with predetermined actions.
        
        Args:
            bet: Bet amount
            actions: List of actions for each decision point
        
        Returns:
            dict: Round results and final state
        """
        action_index = 0
        
        try:
            state = self.engine.start_round(bet)
            
 
            hand_index = 0
            while hand_index < len(self.engine.player_hands):
                hand = self.engine.player_hands[hand_index]
                
                while not hand.finished and action_index < len(actions):
                    available_actions = hand.get_legal_actions(self.engine.bankroll)
                    action = actions[action_index]
                    
                    if action in available_actions:
                        self.engine.execute_action(hand_index, action)
                        if action != 'split':  # Don't increment for splits
                            action_index += 1
                    else:
 
                        hand.finished = True
                    
                    action_index += 1
                
                hand_index += 1
            
 
            results = self.engine.resolve_round()
            final_state = self.engine.get_game_state()
            
            return {
                'success': True,
                'results': results,
                'state': final_state
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'state': self.engine.get_game_state()
            }

class BlackjackCLI:
    """Command-line interface for the blackjack game."""
    
    def __init__(self, config: Optional[GameConfig] = None):
        self.controller = BlackjackGameController(config)
    
    @property
    def engine(self):
        """Access to the underlying engine for backward compatibility."""
        return self.controller.engine

    def display_game_state(self, state: Dict) -> None:
        """Display the current game state."""
        print(f"\n{'='*50}")
        print(f"💰 Bankroll: ${state['bankroll']}")
        print(f"📊 Running Count: {state['running_count']} | True Count: {state['true_count']}")
        
        if state['dealer_visible_card']:
            print(f"🎰 Dealer shows: {state['dealer_visible_card']}")
        
        if state['round_complete'] and state['dealer_value']:
            print(f"🎰 Dealer hand: {state['dealer_hand']} (Value: {state['dealer_value']})")
        
        for i, hand_info in enumerate(state['player_hands']):
            status = ""
            if hand_info['is_blackjack']:
                status = " 🎉 BLACKJACK!"
            elif hand_info['is_bust']:
                status = " 💥 BUST!"
            
            print(f"🃏 Hand {i+1}: {hand_info['cards']} (Value: {hand_info['value']}, Bet: ${hand_info['bet']}){status}")

    def get_valid_bet(self) -> int:
        """Get a valid bet from the user."""
        while True:
            try:
                bet = int(input(f"Enter your bet (${self.engine.config.min_bet}-${self.engine.config.max_bet}): "))
                is_valid, error_msg = self.engine.validate_bet(bet)
                if is_valid:
                    return bet
                else:
                    print(f"❌ {error_msg}")
            except ValueError:
                print("❌ Please enter a valid number")

    def play_game(self) -> None:
        """Main game loop using the controller."""
        print("🎲 Welcome to Blackjack with Card Counting!")
        print(f"Starting bankroll: ${self.controller.engine.bankroll}")
        
 
        game_gen = self.controller.game_session()
        prompt = next(game_gen)
        
        try:
            while True:
                if prompt['type'] == 'bet_input':
                    #self.display_game_state(prompt['state'])
                    bet = self.get_valid_bet()
                    prompt = game_gen.send(bet)
                
                elif prompt['type'] == 'action_input':
                    self.display_game_state(prompt['state'])
                    if len(self.controller.engine.player_hands) > 1:
                        print(f"\n--- Playing Hand {prompt['hand_index'] + 1} ---")
                    
                    print(f"Available actions: {', '.join(prompt['options'])}")
                    action = input("Choose action: ").lower().strip()
                    prompt = game_gen.send(action)
                
                elif prompt['type'] == 'action_result':
                    self.display_game_state(prompt['state'])
                    prompt = next(game_gen)
                
                elif prompt['type'] == 'round_start':
                    self.display_game_state(prompt['state'])
                    prompt = next(game_gen)
                
                elif prompt['type'] == 'round_complete':
                    print(f"\n{'='*50}")
                    print("🎯 ROUND RESULTS:")
                    self.display_game_state(prompt['state'])
                    
                    total_payout = sum(result['payout'] for result in prompt['results'])
                    print(f"💰 Total payout: ${total_payout}")
                    
                    for i, result in enumerate(prompt['results']):
                        result_emoji = {
                            'win': '🟢', 'blackjack': '🎉', 'dealer_bust': '🟢',
                            'lose': '🔴', 'bust': '🔴', 'push': '🟡', 'surrender': '🟠'
                        }.get(result['result'], '⚪')
                        print(f"{result_emoji} Hand {i+1}: {result['result'].upper()}")
                    
                    prompt = next(game_gen)
                
                elif prompt['type'] == 'continue_input':
                    continue_game = input("\nPlay another round? (y/n): ").lower().strip()
                    prompt = game_gen.send(continue_game)
                
                elif prompt['type'] == 'error':
                    print(f"❌ {prompt['message']}")
                    prompt = next(game_gen)
                
                elif prompt['type'] == 'game_over':
                    if prompt['reason'] == 'bankrupt':
                        print("💸 Insufficient funds to continue!")
                    break
                
                else:
 
                    prompt = next(game_gen)
        
        except StopIteration:
            pass
        
 
        stats = self.controller.engine.stats
        print(f"\n{'='*50}")
        print("📊 FINAL STATISTICS:")
        print(f"Final bankroll: ${self.controller.engine.bankroll}")
        print(f"Session profit/loss: ${stats.current_session_profit}")
        print(f"Hands played: {stats.hands_played}")
        print(f"Hands won: {stats.hands_won}")
        print(f"Hands lost: {stats.hands_lost}")
        print(f"Hands pushed: {stats.hands_pushed}")
        print(f"Blackjacks: {stats.blackjacks}")
        print(f"Total wagered: ${stats.total_wagered}")
        print(f"Max bankroll reached: ${stats.max_bankroll}")
        
        if stats.hands_played > 0:
            win_rate = (stats.hands_won / stats.hands_played) * 100
            print(f"Win rate: {win_rate:.1f}%")

if __name__ == "__main__":

    config = GameConfig(
        num_decks=6,
        starting_bankroll=1000,
        min_bet=10,
        max_bet=500,
        blackjack_payout=1.5
    )

    cli = BlackjackCLI(config)
    cli.play_game()