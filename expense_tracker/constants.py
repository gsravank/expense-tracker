from forex_python.converter import CurrencyRates


# Get exchange rate between USD and INR
c = CurrencyRates()
usd_to_inr = c.get_rate('USD', 'INR')


# Action words to identify a message as a transaction

incoming_action_words = ['refunded', 'credited', 'added', 'received']
outgoing_action_words = ['withdrawn', 'purchase', 'debited', 'spent', 'paid']


# Names of transaction sources in messages
transaction_sources = ['citi', 'paytm']

# Actual sources
CITI_ACCOUNT = 'Citibank Account'
CITI_DEBIT = 'Citibank Debit Card'
CITI_CREDIT = 'Citibank Credit Card'
PAYTM = 'PayTM Wallet'