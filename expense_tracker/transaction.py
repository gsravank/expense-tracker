from imessage import get_messages
from constants import incoming_action_words, outgoing_action_words, transaction_sources, usd_to_inr, CITI_ACCOUNT, CITI_CREDIT, CITI_DEBIT, PAYTM

import spacy


nlp = spacy.load('en')


class Transaction:
    def __init__(self, message):
        self.message = message
        self.amount = None
        self.source = None
        self.vendor_name = None
        self.flow = None

        # Extract vendor name and the amount for the transaction from message text
        try:
            self.get_details()
        except Exception:
            pass

    def get_details(self):
        processed_text = process_text(self.message.text)
        first_sent = get_first_statement(processed_text)

        sent_words = first_sent.strip().split()
        action_word = get_first_matching_action_word(sent_words, incoming_action_words+outgoing_action_words)

        # Handle each case separately
        if action_word == 'added':
            # One case
            if first_sent.startswith('paytm has added'):
                self.amount = float(sent_words[3].strip('rs.').replace(',', ''))
                self.source = PAYTM
                self.vendor_name = 'paytm'
                self.flow = 'in'
        elif action_word == 'credited':
            # Two cases
            if first_sent.startswith('your a/c no.xxxxxx3819 is credited by'):
                self.amount = float(sent_words[6].strip('rs.').replace(',', ''))
                self.source = CITI_ACCOUNT
                self.vendor_name = " ".join(sent_words[13:15])
                self.flow = 'in'
            elif first_sent.startswith('your citibank account xxxxxx3819 has been credited with salary'):
                self.amount = float(sent_words[10].strip('rs.').replace(',', ''))
                self.source = CITI_ACCOUNT
                self.vendor_name = 'unbxd'
                self.flow = 'in'
        elif action_word == 'debited':
            # One case
            if first_sent.startswith('your a/c no.xxxxxx3819 is debited for'):
                self.amount = float(sent_words[6].strip('rs.').replace(',', ''))
                self.source = CITI_ACCOUNT
                self.vendor_name = " ".join(sent_words[10:12])
                self.flow = 'out'
        elif action_word == 'paid':
            # Three cases
            if first_sent.startswith('paid rs.'):
                self.amount = float(sent_words[1].strip('rs.').replace(',', ''))
                self.source = PAYTM
                self.flow = 'out'
                # Vendor name could be multiple tokens
                if len(sent_words) == 4:
                    self.vendor_name = sent_words[3]
                else:
                    # Find index of token 'at'
                    at_index = -1
                    for idx, word in enumerate(sent_words):
                        if word == 'at':
                            at_index = idx
                            break

                    if at_index == -1:
                        self.vendor_name = sent_words[3]
                    else:
                        self.vendor_name = " ".join(sent_words[3:at_index])
            elif first_sent.startswith('rs.'):
                self.amount = float(sent_words[0].strip('rs.').replace(',', ''))
                self.source = PAYTM
                self.flow = 'out'
                self.vendor_name = " ".join(sent_words[5:])
            elif first_sent.startswith('you paid'):
                self.amount = float(sent_words[-1].strip('rs.').replace(',', ''))
                self.source = PAYTM
                self.flow = 'out'
                self.vendor_name = " ".join(sent_words[2:-1])
        elif action_word == 'purchase':
            # One case
            if first_sent.startswith('your debit card 5181xxxxxxxx4504 has been used'):
                self.amount = float(sent_words[12].strip('rs.').replace(',', ''))
                self.source = CITI_DEBIT
                self.flow = 'out'

                # Vendor name could be multiple tokens
                # Message has 2 formats: 'at' comes before 'on' and vice-versa
                at_index = -1
                on_index = -1
                for idx, word in enumerate(sent_words):
                    if word == 'on':
                        on_index = idx
                    if word == 'at':
                        at_index = idx

                if at_index != -1 and on_index != -1:
                    if on_index < at_index:
                        self.vendor_name = " ".join(sent_words[at_index+1:])
                    elif at_index < on_index:
                        self.vendor_name = " ".join(sent_words[at_index+1:on_index])
                    else:
                        self.amount = None
                        self.source = None
                        self.flow = None
                        self.vendor_name = None
                else:
                    self.amount = None
                    self.source = None
                    self.flow = None
                    self.vendor_name = None
        elif action_word == 'received':
            # One case
            if first_sent.startswith('you have received a credit'):
                # Find the word 'via'
                via_idx = -1
                for idx, word in enumerate(sent_words):
                    if word == 'via':
                        via_idx = idx
                        break

                if via_idx != -1:
                    self.vendor_name = " ".join(sent_words[17:via_idx])

                    self.amount = float(sent_words[10].strip('rs.').replace(',', ''))
                    self.source = CITI_ACCOUNT
                    self.source = 'in'
        elif action_word == 'refunded':
            # Two cases
            if 'for a transaction on your debit card' in first_sent:
                self.amount = float(sent_words[0].strip('rs.').replace(',', ''))
                self.source = CITI_ACCOUNT
                self.flow = 'in'
                self.vendor_name = 'unknown'
            elif 'refunded in your paytm wallet' in first_sent:
                self.amount = float(sent_words[0].strip('rs.').replace(',', ''))
                self.source = PAYTM
                self.flow = 'in'
                self.vendor_name = " ".join(sent_words[-1])
        elif action_word == 'spent':
            # One case
            if first_sent.startswith('$') or first_sent.startswith('rs.'):
                if first_sent.startswith('$'):
                    self.amount = float(sent_words[0].strip('$').replace(',', ''))
                else:
                    self.amount = float(sent_words[0].strip('rs.').replace(',', ''))
                self.source = CITI_CREDIT
                self.flow = 'out'

                at_index = -1

                for idx, word in enumerate(sent_words):
                    if word == 'at':
                        at_index = idx

                if at_index != -1:
                    self.vendor_name = " ".join(sent_words[at_index+1:])
                else:
                    self.amount = None
                    self.source = None
                    self.vendor_name = None
                    self.flow = None
        elif action_word == 'withdrawn':
            # One case
            if first_sent.startswith('rs.'):
                self.amount = float(sent_words[0].strip('rs.').replace(',', ''))
                self.source = CITI_ACCOUNT
                self.vendor_name = "cash"
                self.flow = 'out'
        elif action_word == 'request':
            if first_sent.startswith('your request on'):
                self.amount = float(sent_words[6].strip('rs.').replace(",", ""))
                self.source = CITI_ACCOUNT
                self.flow = 'out'

                to_index = -1
                was_index = -1

                for idx, word in enumerate(sent_words):
                    if word == 'to':
                        to_index = idx
                    if word == 'was':
                        was_index = idx

                if to_index != -1 and was_index != -1 and to_index < was_index:
                    self.vendor_name = " ".join(sent_words[to_index+1: was_index])
                else:
                    self.amount = None
                    self.source = None
                    self.vendor_name = None
                    self.flow = None

        if self.vendor_name:
            self.vendor_name = self.vendor_name.title()

    def __repr__(self):
        if self.flow == 'in':
            return 'Amount: {}, Via: {}, From: {}'.format(self.amount, self.source, self.vendor_name)
        else:
            return 'Amount: {}, Via: {}, To: {}'.format(self.amount, self.source, self.vendor_name)


def check_if_price(string):
    each_char_check = [char == '.' or char == ',' or char.isdigit() for char in string]
    return all(each_char_check) and len(string)


def process_text(text):
    text_tokens = text.lower().strip().split()

    final_tokens = list()

    # Change all Rs amount related tokens to Rs.1234.56 format
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
                final_tokens.append('rs')
        else:
            if token == 'usd':
                final_tokens.append('$')
            else:
                final_tokens.append(token)

        curr_idx += 1

    # Change all $ amount related tokens to $1234.56 format
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

    processed_text = " ".join(final_tokens).strip()

    # If after a period there is an alphabet character, then add space after the period
    # Except when it ends with .com or when it starts with www.
    prev_three_chars_to_avoid = ['www']
    next_three_chars_to_avoid = ['com', 'org', 'in ']

    final_chars = list()
    temp_chars = list()
    for idx, char in enumerate(processed_text):
        if char == ".":
            temp_chars.append(".")
        else:
            if len(temp_chars) == 0:
                final_chars.append(char)
            else:
                three_chars_after_period = "".join(processed_text[idx:idx+3])
                three_chars_before_period = "".join(processed_text[idx-4:idx-1])

                if char.isalpha() and char != 'x' and not(any([three_chars_before_period == triple for triple in prev_three_chars_to_avoid])) and not(any([three_chars_after_period == triple for triple in next_three_chars_to_avoid])):
                    temp_chars.append(" ")
                    temp_chars.append(char)
                else:
                    temp_chars.append(char)

                final_chars.extend(temp_chars)
                temp_chars = list()

    final_processed_text = "".join(final_chars)

    return final_processed_text


def get_first_statement(text):
    # If first line from the processed text does not contain a Rs. or $ token, then ignore the message
    # doc = nlp(unicode(text))
    # sentences = doc.sents
    # for sentence in sentences:
    #     first_sentence = sentence.text
    #     break

    # Simpler and works better (although not perfect)
    statements = text.split('. ')
    first_sentence = statements[0]

    return first_sentence


def get_first_matching_action_word(message_words, action_words):
    for token in message_words:
        for action_word in action_words:
            if token == action_word:
                return action_word

    return 'None'


def message_is_a_transaction(message):
    message_text = message.text
    user_name = message.user.name_or_number
    processed_text = process_text(message_text)

    # If source of message is not from list of known sources, then ignore message
    if not any([tran_source in user_name for tran_source in transaction_sources]):
        return False

    # If none of the action words occur in the text, then ignore the message
    message_words = processed_text.strip().split()
    action_words = incoming_action_words + outgoing_action_words

    if not any([msg_word in action_words for msg_word in message_words]):
        return False

    # If first line from the processed text does not contain a Rs. or $ token, then ignore the message
    first_sentence = get_first_statement(processed_text)

    if '$' not in first_sentence and 'rs.' not in first_sentence:
        return False

    return True


def get_transactions(start, end):
    messages = get_messages(start, end)

    transactions = list()

    for message in messages:
        if message_is_a_transaction(message):
            transactions.append(Transaction(message))

    return transactions
