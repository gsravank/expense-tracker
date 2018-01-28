from imessage import get_messages, get_all_messages
from constants import incoming_action_words, outgoing_action_words, transaction_sources, usd_to_inr, CITI_ACCOUNT, CITI_CREDIT, CITI_DEBIT, PAYTM
from category_tree import category_tree_dictionary, get_node_from_node_name, get_path_string_from_root_to_node

import spacy
import pandas as pd
import datetime


nlp = spacy.load('en')


class Transaction:
    def __init__(self, message):
        self.message = message
        self.amount = None
        self.source = None
        self.vendor_name = None
        self.flow = None
        self.category_node = None
        self.category_path = None
        self.vendor = None
        self.time = self.message.time

        # Extract vendor name, flow and the amount for the transaction from message text
        try:
            self.get_details()
        except Exception:
            pass

        # Extract category name
        try:
            self.get_category_path()
        except Exception:
            pass

        # Get readable name for vendor
        try:
            self.get_readable_name()
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
                self.vendor_name = " ".join(sent_words[-1:])
        elif action_word == 'spent':
            # One case
            if first_sent.startswith('$') or first_sent.startswith('rs.'):
                if first_sent.startswith('$'):
                    self.amount = float(sent_words[0].strip('$').replace(',', '')) * usd_to_inr
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
            self.vendor_name = self.vendor_name.title().strip('+')

    def get_category_path(self):
        if not any([elem is None for elem in [self.amount, self.source, self.vendor_name, self.flow]]):
            vendor_category_df = pd.read_csv('data/super_categories.csv')
            rel_df = vendor_category_df[(vendor_category_df['source'] == self.source) & (vendor_category_df['flow'] == self.flow) & (vendor_category_df['vendor_name'] == self.vendor_name)]

            if len(rel_df):
                rel_df = rel_df.iloc[0]

                tree_name = rel_df['tree_name'].strip()
                leaf_name = rel_df['leaf_name'].strip()

                # Special cases handling
                if self.vendor_name == 'Itunes.Com/Bill It' and self.amount < 100.0:
                    leaf_name = 'Online Services'
            else:
                tree_name = 'unknown'
                leaf_name = 'Unknown'

            self.category_node = get_node_from_node_name(leaf_name, category_tree_dictionary[tree_name])

            self.category_path = get_path_string_from_root_to_node(self.category_node, sep='|')

    def get_readable_name(self):
        if not any([elem is None for elem in [self.amount, self.source, self.vendor_name, self.flow]]):
            vendor_category_df = pd.read_csv('data/super_categories.csv')
            rel_df = vendor_category_df[(vendor_category_df['source'] == self.source) & (vendor_category_df['flow'] == self.flow) & (vendor_category_df['vendor_name'] == self.vendor_name)]

            if len(rel_df):
                rel_df = rel_df.iloc[0]

                readable_name = rel_df['readable_name']
            else:
                readable_name = 'Unknown'

            self.vendor = readable_name

    def __repr__(self):
        if self.flow == 'in':
            return 'Amount: {}, Via: {}, From: {}, Category: {}, At: {}'.format(self.amount, self.source, self.vendor, self.category_path, self.time)
        else:
            return 'Amount: {}, Via: {}, To: {}, Category: {}, At: {}'.format(self.amount, self.source, self.vendor, self.category_path, self.time)


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


def resolve_categories_from_file():
    unknown_categories_file = 'data/unknown_categories.csv'
    super_categories_file = 'data/super_categories.csv'

    unknown_categories = pd.read_csv(unknown_categories_file)
    try:
        unknown_categories.drop('Unnamed: 0', axis=1, inplace=True)
    except Exception:
        pass

    super_categories = pd.read_csv(super_categories_file)
    try:
        super_categories.drop('Unnamed: 0', axis=1, inplace=True)
    except Exception:
        pass

    if len(unknown_categories):
        resolved_categories = unknown_categories[(unknown_categories['tree_name'] != 'unknown') & (unknown_categories['leaf_name'] != 'Unknown') & (unknown_categories['readable_name'] != 'Unknown')]
        still_unknown_categories = unknown_categories[(unknown_categories['tree_name'] == 'unknown') | (unknown_categories['leaf_name'] == 'Unknown') | (unknown_categories['readable_name'] == 'Unknown')]

        if len(resolved_categories):
            all_known_categories = [super_categories, resolved_categories]
            all_known_categories_df = pd.concat(all_known_categories)

            all_known_categories_df.to_csv(super_categories_file)
            print 'Appended resolved category maps to super_categories.csv'

            if len(still_unknown_categories):
                still_unknown_categories.to_csv(unknown_categories_file)
                print 'Written still unresolved category maps to unknown_categories.csv'
        else:
            print 'Unknown categories present in file but none resolved'


def get_unknown_categories():
    all_transactions = get_all_transactions()

    unknown_cat_transactions = [tran for tran in all_transactions if tran.category_path == 'Unknown' and tran.vendor == 'Unknown']

    if len(unknown_cat_transactions):
        flows = list()
        sources = list()
        vendor_names = list()
        tree_names = list()
        leaf_names = list()
        vendors = list()

        combinations = list()

        for unknown_tran in unknown_cat_transactions:
            combinations.append((unknown_tran.flow, unknown_tran.source, unknown_tran.vendor_name))

        unique_combinations = list(set(combinations))

        for combination in unique_combinations:
            flows.append(combination[0])
            sources.append(combination[1])
            vendor_names.append(combination[2])
            tree_names.append('unknown')
            leaf_names.append('Unknown')
            vendors.append('Unknown')

        unknown_categories_df = pd.DataFrame({'flow': flows, 'source': sources, 'vendor_name': vendor_names, 'tree_name': tree_names, 'leaf_name': leaf_names, 'readable_name': vendors})
        unknown_categories_df = unknown_categories_df[['flow', 'source', 'vendor_name', 'tree_name', 'leaf_name', 'readable_name']]
        unknown_categories_df.to_csv('data/unknown_categories.csv')

        print 'Written unknown vendor to category maps to unknown_categories.csv'
    else:
        empty_df = pd.DataFrame({'flow': [], 'source': [], 'vendor_name': [], 'tree_name': [], 'leaf_name': [], 'readable_name': []})
        empty_df = empty_df[['flow', 'source', 'vendor_name', 'tree_name', 'leaf_name', 'readable_name']]
        empty_df.to_csv('data/unknown_categories.csv')
        print 'No unknown categories among the transactions'


def get_all_transactions():
    messages = get_all_messages()

    transactions = list()

    for message in messages:
        if message_is_a_transaction(message):
            transaction = Transaction(message)

            if not any([x is None for x in [transaction.amount, transaction.source, transaction.vendor_name, transaction.flow]]):
                if transaction.source == CITI_DEBIT and transaction.vendor == 'PayTM': # Ignore transaction from Citi to PayTM wallet
                    pass
                else:
                    transactions.append(transaction)

    return transactions


def get_transactions(start, end):
    try:
        start_date = datetime.datetime.strptime(start, '%Y-%m-%d')
        end_date = datetime.datetime.strptime(end, '%Y-%m-%d')
    except Exception as e:
        print 'Could not understand date inputs'
        print 'Error: "{}"'.format( e.__str__() )

        return []

    all_transactions = get_all_transactions()

    relevant_transactions = list()

    for transaction in all_transactions:
        transaction_msg = transaction.message

        if start_date.date() <= transaction_msg.time.date() <= end_date.date():
            relevant_transactions.append(transaction)

    return relevant_transactions


# Resolve any unknown vendor category maps
# resolve_categories_from_file()
# get_unknown_categories()