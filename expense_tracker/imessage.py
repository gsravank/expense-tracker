import sqlite3
from os.path import expanduser


# Epoch time stamp of 2001-01-01
OSX_EPOCH = 978307200


def _new_connection():
    # The current logged-in user's Messages sqlite database is found at:
    #  ~/Library/Messages/chat.db

    # db_path = expanduser("~") + '/Library/Messages/chat.db'
    db_path = 'data/chat.db'

    return sqlite3.connect(db_path)


def get_all_messages():
    connection = _new_connection()
    c = connection.cursor()

    # Get all messages and join with recipient details
    query = """
    select message.text, message.handle_id, message.date, message.date_delivered, message.date_read, handle.id, handle.service 
    from message 
    left join handle on message.handle_id = handle.ROWID
    """

    c.execute(query)

    for row in c:
        print row

    connection.close()

    return

get_all_messages()