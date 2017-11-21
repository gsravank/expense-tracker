from imessage import get_recent_messages


class Transaction:
    def __init__(self, message):
        self.message = message
        self.amount = 0
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


def check_valid_transaction():
    return


def get_recent_transactions(period='1w'):
    recent_messages = get_recent_messages(period=period)

    transactions = list()

    for message in recent_messages:
        if check_valid_transaction(message):
            transactions.append(Transaction(message))
        
    return transactions
