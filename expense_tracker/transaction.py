class Transaction:
        def __init__(self, message):
            self.message = message
            self.source = ''
            self.amount = 0
            self.vendor_name = ''

            # Evaluate source, vendor names and the amount for the transaction from message details
            self.get_source()
            self.get_amount()
            self.get_vendor()

        def get_source(self):
            name_or_number = self.message.user.name_or_number

            if 'paytm' in name_or_number:
                self.source = 'Paytm'
            elif 'citi' in  name_or_number:
                if 'debit card' in self.message.text.lower():
                    self.source = 'Citi Debit'
                elif 'credit card' in self.message.text.lower():
                    self.source = 'Citi Credit'
            else:
                self.source = 'Unknown'

        def get_amount(self):
            self.amount = 0

        def get_vendor(self):
            self.vendor_name = ''

        def __repr__(self):
            return 'Amount: {}, Via: {}, To: {}'.format(self.amount, self.source, self.vendor_name)


def get_recent_transactions(period='1w'):
    return