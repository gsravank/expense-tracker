from imessage import get_messages
import json
import re


class Transaction:
    def __init__(self, message):
        self.message = message
        self.amount = 0
        self.source = ''
        self.vendor_name = ''

        # Extract vendor name and the amount for the transaction from message text
        self.get_amount()
        self.get_vendor()
        self.get_source()

    def get_amount(self):
        self.amount = 0

    def get_vendor(self):
        self.vendor_name = ''

    def get_source(self):
        self.source = ''

    def __repr__(self):
        return 'Amount: {}, Via: {}, To: {}'.format(self.amount, self.source, self.vendor_name)


def message_is_a_transaction(message):
    return True


def get_transactions(start, end):
    messages = get_messages(start, end)

    transactions = list()

    for message in messages:
        if message_is_a_transaction(message):
            transactions.append(Transaction(message))

    return transactions
