from imessage import get_messages
from constants import incoming_action_words, outgoing_action_words, transaction_sources, usd_to_inr

import spacy


nlp = spacy.load('en')


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


def check_if_price(string):
    each_char_check = [char == '.' or char == ',' or char.isdigit() for char in string]
    return all(each_char_check) and len(string)


def process_text(text):
    text_tokens = text.lower().strip().split()

    final_tokens = list()

    curr_idx = 0
    while curr_idx < len(text_tokens):
        token = text_tokens[curr_idx]
        if token == 'rs' or token == 'rs.':
            curr_idx += 1

            if curr_idx < len(text_tokens):
                next_token = text_tokens[curr_idx]

                if check_if_price(next_token):
                    final_tokens.append('rs.' + next_token)
                else:
                    final_tokens.append(token)
                    final_tokens.append(next_token)
            else:
                final_tokens.append('rs.')
        else:
            if token == 'usd':
                final_tokens.append('$')
            else:
                final_tokens.append(token)

        curr_idx += 1

    text_tokens = final_tokens
    final_tokens = list()
    curr_idx = 0
    while curr_idx < len(text_tokens):
        token = text_tokens[curr_idx]
        if check_if_price(token):
            curr_idx += 1

            if curr_idx < len(text_tokens):
                next_token = text_tokens[curr_idx]

                if next_token == '$':
                    final_tokens.append('$' + token)
                else:
                    final_tokens.append(token)
                    final_tokens.append(next_token)
        else:
            final_tokens.append(token)

        curr_idx += 1

    return ' '.join(final_tokens).strip()


def message_is_a_transaction(message):
    message_text = message.text
    user_name = message.user.name_or_number
    processed_text = process_text(message_text)

    # If source of message is not from list of known sources, then ignore message
    if not any([tran_source in user_name for tran_source in transaction_sources]):
        return False

    # If first line from the processed text does not contain a Rs. or $ token, then ignore the message
    doc = nlp(unicode(processed_text))
    sentences = doc.sents
    for sentence in sentences:
        first_sentence = sentence.text
        break

    if '$' not in first_sentence and 'rs.' not in first_sentence:
        return False

    # If none of the action words occur in the text, then ignore the message
    message_words = processed_text.strip().split()
    action_words = incoming_action_words + outgoing_action_words

    if not any([msg_word in action_words for msg_word in message_words]):
        return False

    return True


def get_transactions(start, end):
    messages = get_messages(start, end)

    transactions = list()

    for message in messages:
        if message_is_a_transaction(message):
            transactions.append(Transaction(message))

    return transactions
