import sqlite3
import datetime
from dateutil.relativedelta import relativedelta
from os.path import expanduser


# Epoch time stamp of 2001-01-01
OSX_EPOCH = 978307200


# Class to represent a user with whom messages can be exchanged
class User:
        def __init__(self, id, name_or_number):
            self.id = id
            self.name_or_number = name_or_number

        def __repr__(self):
            return 'User: {}'.format(self.name_or_number)

        def __eq__(self, other):
            return self.__dict__ == other.__dict__


# Class to represent a message
class Message:
        def __init__(self, text, time, user):
            self.text = text.encode('ascii', 'ignore') # Remove any non-ASCII characters
            self.time = datetime.datetime.fromtimestamp(time/1000000000 + OSX_EPOCH)
            if isinstance(user, User):
                self.user = user
            else:
                self.user = User(None, None)

        def __repr__(self):
            return 'Message Content: "{}", Received At: {}, {}'.format(self.text, self.time, self.user)


def _connection():
    # The current logged-in user's Messages sqlite database is found at:
    #  ~/Library/Messages/chat.db

    # db_path = expanduser("~") + '/Library/Messages/chat.db'
    db_path = 'data/chat.db'

    return sqlite3.connect(db_path)


# Return a list of all messages
def get_all_messages():
    connection = _connection()
    c = connection.cursor()

    # Get all messages and join with user details
    query = """
    select message.text, message.handle_id, message.date, handle.id
    from message 
    left join handle on message.handle_id = handle.ROWID
    """

    c.execute(query)

    all_messages = list()

    for row in c:
        user = User(row[1], row[3])
        message = Message(row[0], row[2], user)

        if user.name_or_number is not None:
            all_messages.append(message)

    connection.close()

    return all_messages


# Return a list of messages received within the past "period" time
def get_recent_messages(period='1w'):
    # Get dates for today and the day which is "period" days back from today
    today = datetime.datetime.now().date()

    if period == '1w':
        time_delta_first = datetime.timedelta(weeks=1)
    elif period == '1m':
        time_delta_first = relativedelta(months=1)
    else:
        time_delta_first = relativedelta(months=1)

    first_day = today - time_delta_first

    all_messages = get_all_messages()
    recent_messages = list()

    for message in all_messages:
        if first_day <= message.time.date() < today:
            recent_messages.append(message)

    return recent_messages
