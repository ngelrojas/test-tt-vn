import re
import unittest
import uuid

class UsernameException(Exception):
    pass

class PaymentException(Exception):
    pass

class CreditCardException(Exception):
    pass

class Payment:
    def __init__(self, amount, actor, target, note):
        self.id = str(uuid.uuid4())
        self.amount = float(amount)
        self.actor = actor
        self.target = target
        self.note = note

class User:
    activities = []

    def __init__(self, username):
        self.credit_card_number = None
        self.balance = 0.0

        if self._is_valid_username(username):
            self.username = username
        else:
            raise UsernameException('Username not valid.')

        self.friends = []

    def retrieve_feed(self):

        feed = []
        for event in User.activities:
            if isinstance(event, Payment):
                if event.actor == self or event.target == self:
                    feed.append(event)
            elif isinstance(event, tuple) and event[0] == 'friend':
                actor, new_friend = event[1], event[2]
                if actor == self or new_friend == self:
                    feed.append(event)
        return feed

    def add_friend(self, new_friend):
        if new_friend.username == self.username:
            raise PaymentException('User cannot befriend themselves.')
        
        if new_friend not in self.friends:
            self.friends.append(new_friend)
            new_friend.friends.append(self)

            User.activities.append(('friend', self, new_friend))

    def add_to_balance(self, amount):
        self.balance += float(amount)

    def add_credit_card(self, credit_card_number):
        if self.credit_card_number is not None:
            raise CreditCardException('Only one credit card per user!')

        if self._is_valid_credit_card(credit_card_number):
            self.credit_card_number = credit_card_number
        else:
            raise CreditCardException('Invalid credit card number.')

    def pay(self, target, amount, note):
        amount = float(amount)
        
        if self.username == target.username:
            raise PaymentException('User cannot pay themselves.')
        if amount <= 0.0:
            raise PaymentException('Amount must be a non-negative number.')
        
        if self.balance >= amount:
            payment = self.pay_with_balance(target, amount, note)
        else:
            payment = self.pay_with_card(target, amount, note)
        # record payment activity
        User.activities.append(payment)
        return payment

    def pay_with_card(self, target, amount, note):
        amount = float(amount)

        if self.username == target.username:
            raise PaymentException('User cannot pay themselves.')
        elif amount <= 0.0:
            raise PaymentException('Amount must be a non-negative number.')
        elif self.credit_card_number is None:
            raise PaymentException('Must have a credit card to make a payment.')

        self._charge_credit_card(self.credit_card_number)
        payment = Payment(amount, self, target, note)

        target.add_to_balance(amount)
        return payment

    def pay_with_balance(self, target, amount, note):
        amount = float(amount)

        if self.username == target.username:
            raise PaymentException('User cannot pay themselves.')
        if amount <= 0.0:
            raise PaymentException('Amount must be a non-negative number.')
        if self.balance < amount:
            raise PaymentException('Insufficient balance.')

        self.balance -= amount
        payment = Payment(amount, self, target, note)
        # credit target balance
        target.add_to_balance(amount)
        return payment

    def _is_valid_credit_card(self, credit_card_number):
        return credit_card_number in ["4111111111111111", "4242424242424242"]

    def _is_valid_username(self, username):
        # username: 4-15 chars, letters, numbers, underscore, or hyphen
        return re.match(r'^[A-Za-z0-9_\-]{4,15}$', username)

    def _charge_credit_card(self, credit_card_number):
        # magic method that charges a credit card thru the card processor
        pass

class MiniVenmo:
    def __init__(self):
        self.users = []

    def create_user(self, username, balance, credit_card_number):
        user = User(username)
        user.add_to_balance(balance)
        user.add_credit_card(credit_card_number)
    
        self.users.append(user)
        return user

    def render_feed(self, feed):
        for event in feed:
            if isinstance(event, Payment):
                print(f"{event.actor.username} paid {event.target.username} ${event.amount:.2f} for {event.note}")
            elif isinstance(event, tuple) and event[0] == 'friend':
                actor, new_friend = event[1], event[2]
                print(f"{actor.username} and {new_friend.username} are now friends")

    @classmethod
    def run(cls):
        venmo = cls()

        bobby = venmo.create_user("Bobby", 5.00, "4111111111111111")
        carol = venmo.create_user("Carol", 10.00, "4242424242424242")

        try:
            # should complete using balance
            bobby.pay(carol, 5.00, "Coffee")

            # should complete using card
            carol.pay(bobby, 15.00, "Lunch")
        except PaymentException as e:
            print(e)

        feed = bobby.retrieve_feed()
        venmo.render_feed(feed)

        bobby.add_friend(carol)

class TestUser(unittest.TestCase):
    def test_this_works(self):
        with self.assertRaises(UsernameException):
            raise UsernameException()

if __name__ == '__main__':
    unittest.main()
