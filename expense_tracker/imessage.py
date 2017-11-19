import sqlite3
from os.path import expanduser


# Epoch time stamp of 2001-01-01
OSX_EPOCH = 978307200


# Class to represent a user with whom messages can be exchanged
class User:
        def __init__(self, id, name_or_number):
            self.id = id
            self.name_or_number = name_or_number

        def __repr__(self):
            return 'User: {}, ID: {}'.format(self.name_or_number, self.id)

        def __str__(self):
            return str(self.__dict__)

        def __eq__(self, other):
            return self.__dict__ == other.__dict__


# Class to represent a message
class Message:
        def __init__(self, text, time, user):
            self.text = text.encode('ascii', 'ignore') # Remove any non-ASCII characters
            self.time = time
            self.user = user

        def __repr__(self):
            return 'Message Content: "{}", Received At: {}, From: {}'.format(self.text, self.time, self.user.name_or_number)


def _connection():
    # The current logged-in user's Messages sqlite database is found at:
    #  ~/Library/Messages/chat.db

    # db_path = expanduser("~") + '/Library/Messages/chat.db'
    db_path = 'data/chat.db'

    return sqlite3.connect(db_path)


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

        all_messages.append(message)

    connection.close()

    return all_messages