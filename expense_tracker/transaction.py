from imessage import get_recent_messages
import json
import re


class Transaction:
    def __init__(self, message, pattern):
        self.message = message
        self.pattern = pattern
        self.amount = 0
        self.source = ''
        self.vendor_name = ''

        # Extract vendor name and the amount for the transaction from message text
        self.get_amount()
        self.get_vendor()

    def get_amount(self):
        self.amount = 0

    def get_vendor(self):
        self.vendor_name = ''

    def __repr__(self):
        return 'Amount: {}, Via: {}, To: {}'.format(self.amount, self.source, self.vendor_name)


def find_matching_expense_pattern(message_content, expense_patterns):
    for pattern, expense_details in expense_patterns.items():
        if re.search(pattern, message_content):
            return pattern

    return ''


def get_recent_transactions(period='1w'):
    recent_messages = get_recent_messages(period=period)

    with open('data/expense_patterns.json', 'rb') as f:
        expense_patterns = json.load(f)

    transactions = list()

    for message in recent_messages:
        matched_pattern = find_matching_expense_pattern(message.text, expense_patterns)
        if matched_pattern != '':
            transactions.append(Transaction(message, matched_pattern))

    return transactions
