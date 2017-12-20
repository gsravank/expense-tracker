from forex_python.converter import CurrencyRates


# Get exchange rate between USD and INR
c = CurrencyRates()
usd_to_inr = c.get_rate('USD', 'INR')


# Action words to identify a message as a transaction

incoming_action_words = ['refunded', 'credited', 'added', 'received']
outgoing_action_words = ['withdrawn', 'purchase', 'debited', 'spent', 'paid']

transaction_sources = ['citi', 'paytm']
