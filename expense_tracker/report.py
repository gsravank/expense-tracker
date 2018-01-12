from transaction import get_all_transactions, get_transactions
from category_tree import get_all_leaf_nodes_below_any_node

from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta


week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']


def get_previous_date_with_diff(end_date, period):
    if period == '1w':
        time_delta = timedelta(weeks=1)
    elif period == '1m':
        time_delta = relativedelta(months=1)
    else:
        return None

    end_date_datetime = datetime.strptime(end_date, '%Y-%m-%d')

    first_date_datetime = end_date_datetime - time_delta
    first_date_string = first_date_datetime.strftime('%Y-%m-%d')

    return first_date_string


def get_month_name_from_datetime(datetime_object):
    return datetime_object.strftime("%B")


def get_date_number_from_datetime(datetime_object):
    return datetime_object.day


def get_weekday_name_from_datetime(datetime_object):
    return week_days[datetime_object.weekday()]


def get_year_from_datetime(datetime_object):
    return datetime_object.year


def get_between_dates(start, end):
    try:
        d1 = datetime.strptime(start, "%Y-%m-%d")
        d2 = datetime.strptime(end, "%Y-%m-%d")
    except Exception as e:
        print "Error: {}".format(e.__str__())
        print "Provide dates in 'YYYY-MM-DD' format"
        return None

    delta = d2 - d1  # timedelta

    dates = list()
    for i in range(delta.days + 1):
        dates.append((d1 + timedelta(days=i)).strftime("%Y-%m-%d"))

    return dates


def flatten_list_of_lists(orig_list):
    flat_list = [item for sublist in orig_list for item in sublist]

    return flat_list


def get_total_expense(start_date, end_date):
    expense_transactions = get_expense_transactions(start_date, end_date)

    total_expenditure = 0.0

    for transaction in expense_transactions:
        total_expenditure += transaction.amount

    return total_expenditure


def get_total_income(start_date, end_date):
    income_transactions = get_income_transactions(start_date, end_date)

    total_expenditure = 0.0

    for transaction in income_transactions:
        total_expenditure += transaction.amount

    return total_expenditure


def get_expense_transactions(start_date, end_date):
    transactions = get_transactions(start_date, end_date)

    expense_transactions = list()
    for transaction in transactions:
        if transaction.flow == 'out':
            expense_transactions.append(transaction)

    return expense_transactions


def get_income_transactions(start_date, end_date):
    transactions = get_transactions(start_date, end_date)

    income_transactions = list()
    for transaction in transactions:
        if transaction.flow == 'in':
            income_transactions.append(transaction)

    return income_transactions


def get_transactions_of_leaf_node(start_date, end_date, leaf_node):
    transactions = get_transactions(start_date, end_date)

    node_transactions = list()

    for transaction in transactions:
        if transaction.category_node == leaf_node:
            node_transactions.append(transaction)

    return node_transactions


def get_transactions_of_leaf_nodes_below_any_node(start_date, end_date, any_node):
    all_leaf_nodes_of_node = get_all_leaf_nodes_below_any_node(any_node)

    each_leaf_node_transactions = [get_transactions_of_leaf_node(start_date, end_date, leaf_node) for leaf_node in all_leaf_nodes_of_node]

    all_leaf_node_transactions = flatten_list_of_lists(each_leaf_node_transactions)

    return all_leaf_node_transactions


def node_total_expense_or_income(start_date, end_date, node):
    all_leaf_node_transactions = get_transactions_of_leaf_nodes_below_any_node(start_date, end_date, node)

    total_expense_or_income = 0.0

    for transaction in all_leaf_node_transactions:
        total_expense_or_income += transaction.amount

    return total_expense_or_income


