from transaction import get_transactions
from category_tree import get_all_leaf_nodes_below_any_node, category_tree_dictionary, get_path_string_from_root_to_node
from yag_email import send_email

from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
import operator
import os
import numpy as np
import json
import pandas as pd


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


def get_readable_name_from_datetime(datetime_object):
    return datetime_object.strftime("%d-%b-%y")


def get_datetime_obj(date):
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        return date_obj
    except Exception as e:
        print "Error: {}".format(e.__str__())
        return None


def get_between_dates(start, end):
    try:
        d1 = datetime.strptime(start, "%Y-%m-%d")
        d2 = datetime.strptime(end, "%Y-%m-%d")
    except Exception as e:
        print "Error: {}".format(e.__str__())
        return None

    delta = d2 - d1  # timedelta

    dates = list()
    for i in range(delta.days + 1):
        dates.append((d1 + timedelta(days=i)).strftime("%Y-%m-%d"))

    return dates


def get_between_dateobjects(start, end):
    try:
        d1 = datetime.strptime(start, "%Y-%m-%d")
        d2 = datetime.strptime(end, "%Y-%m-%d")
    except Exception as e:
        print "Error: {}".format(e.__str__())
        return None

    delta = d2 - d1  # timedelta

    dates = list()
    for i in range(delta.days + 1):
        dates.append(d1 + timedelta(days=i))

    return dates


def get_number_of_dates_between_dates(start, end):
    try:
        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d")
    except Exception as e:
        print "Error: {}".format(e.__str__())
        return None

    delta = end_date - start_date

    return delta.days + 1


def split_date_range(start, end):
    between_dates = get_between_dateobjects(start, end)

    between_dates_weekdays = [get_weekday_name_from_datetime(datetime_obj) for datetime_obj in between_dates]
    unique_weekdays = set(between_dates_weekdays)

    between_dates_months = [get_month_name_from_datetime(datetime_obj) for datetime_obj in between_dates]
    unique_months = set(between_dates_months)

    if len(unique_weekdays) < 7 or (len(unique_weekdays) == 7 and len(between_dates) == 7):
        return [[date.strftime("%Y-%m-%d"), date.strftime("%Y-%m-%d")] for date in between_dates]
    elif len(unique_months) == 1:
        final_list_of_splits = list()
        temp_list = list()
        for between_date, between_dates_weekday in zip(between_dates, between_dates_weekdays):
            if between_dates_weekday == 'Monday':
                if len(temp_list):
                    final_list_of_splits.append(temp_list)
                temp_list = [between_date.strftime("%Y-%m-%d")]
            else:
                temp_list.append(between_date.strftime("%Y-%m-%d"))

        if len(temp_list):
            final_list_of_splits.append(temp_list)
    else:
        final_list_of_splits = list()
        temp_list = list()

        for between_date in between_dates:
            date_number = get_date_number_from_datetime(between_date)

            if date_number == 1:
                if len(temp_list):
                    final_list_of_splits.append(temp_list)
                temp_list = [between_date.strftime("%Y-%m-%d")]
            else:
                temp_list.append(between_date.strftime("%Y-%m-%d"))

        if len(temp_list):
            final_list_of_splits.append(temp_list)

    return final_list_of_splits


def get_date_split_names(date_splits):
    split_names = list()
    if all([date_split[0] == date_split[-1] for date_split in date_splits]):
        days = [date_split[0] for date_split in date_splits]

        for day in days:
            split_names.append(day.split('-')[-1])
    else:
        if date_splits[0][0].split('-')[1] != date_splits[1][0].split('-')[1]:
            for month in date_splits:
                first_date = month[0]
                last_date = month[-1]

                month_number = first_date.split('-')[1]
                first_date_num = first_date.split('-')[-1]
                last_date_num = last_date.split('-')[-1]

                split_names.append(str(month_number)+'/'+str(first_date_num)+'-'+str(month_number)+'/'+str(last_date_num))
        else:
            for week in date_splits:
                week_start_date = week[0].split('-')[-1]
                week_end_date = week[-1].split('-')[-1]

                split_names.append(week_start_date+'-'+week_end_date)

    return split_names


def flatten_list_of_lists(orig_list):
    flat_list = [item for sublist in orig_list for item in sublist]

    return flat_list


def get_total_expense(start_date, end_date):
    expense_transactions = get_expense_transactions(start_date, end_date)

    total_expenditure = 0.0

    for transaction in expense_transactions:
        total_expenditure += transaction.amount

    return total_expenditure


def total_amount_in_transactions(transactions):
    total_amount = 0.0

    for tran in transactions:
        total_amount += tran.amount

    return total_amount


def get_total_expense_from_transactions(transactions):
    expense_transactions = get_expense_transactions_from_transactions(transactions)
    return total_amount_in_transactions(expense_transactions)


def get_total_income(start_date, end_date):
    income_transactions = get_income_transactions(start_date, end_date)

    total_expenditure = 0.0

    for transaction in income_transactions:
        total_expenditure += transaction.amount

    return total_expenditure


def get_total_income_from_transactions(transactions):
    income_transactions = get_income_transactions_from_transactions(transactions)
    return total_amount_in_transactions(income_transactions)


def get_expense_transactions(start_date, end_date):
    transactions = get_transactions(start_date, end_date)

    expense_transactions = list()
    for transaction in transactions:
        if transaction.flow == 'out':
            expense_transactions.append(transaction)

    return expense_transactions


def get_expense_transactions_from_transactions(transactions):
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


def get_income_transactions_from_transactions(transactions):
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


def get_transactions_of_leaf_node_from_transactions(transactions, leaf_node):
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


def get_transactions_of_leaf_nodes_below_any_node_from_transactions(transactions, any_node):
    all_leaf_nodes_of_node = get_all_leaf_nodes_below_any_node(any_node)

    each_leaf_node_transactions = [[transaction for transaction in transactions if transaction.category_node == leaf_node]for leaf_node in all_leaf_nodes_of_node]

    all_leaf_node_transactions = flatten_list_of_lists(each_leaf_node_transactions)

    return all_leaf_node_transactions


def node_total_expense_or_income(start_date, end_date, node):
    all_leaf_node_transactions = get_transactions_of_leaf_nodes_below_any_node(start_date, end_date, node)

    total_expense_or_income = 0.0

    for transaction in all_leaf_node_transactions:
        total_expense_or_income += transaction.amount

    return total_expense_or_income


def node_total_expense_or_income_from_transactions(transactions, node):
    all_leaf_node_transactions = get_transactions_of_leaf_nodes_below_any_node_from_transactions(transactions, node)

    return total_amount_in_transactions(all_leaf_node_transactions)


def get_transactions_in_date_range_from_transactions(transactions, start, end):
    try:
        start_date = datetime.strptime(start, '%Y-%m-%d')
        end_date = datetime.strptime(end, '%Y-%m-%d')
    except Exception as e:
        print 'Could not understand date inputs'
        print 'Error: "{}"'.format( e.__str__() )

        return []

    relevant_transactions = list()

    for transaction in transactions:
        if start_date.date() <= transaction.time.date() <= end_date.date():
            relevant_transactions.append(transaction)

    return relevant_transactions


def generate_category_wise_report(transactions, tree_name, start_date, end_date, level='top'):
    category_tree = category_tree_dictionary[tree_name]

    if level == 'top':
        nodes = category_tree.children
    else:
        nodes = get_all_leaf_nodes_below_any_node(category_tree)

    node_amount_dictionary = dict()
    for node in nodes:
        node_amount_dictionary[get_path_string_from_root_to_node(node)] = node_total_expense_or_income_from_transactions(transactions, node)

    sorted_node_amount_dictionary = sorted(node_amount_dictionary.items(), key=operator.itemgetter(1), reverse=True)
    names = [tup[0].split('|')[-1] for tup in sorted_node_amount_dictionary if tup[1] > 0.0]
    amounts = [tup[1] for tup in sorted_node_amount_dictionary if tup[1] > 0.0]

    if len(names):
        percents = [float(amount) / sum(amounts) for amount in amounts]

        idx = -1
        for i in range(len(percents) - 1, -1, -1):
            if percents[i] > 0.005 and idx == -1:
                idx = i

        names = names[:idx+1]
        amounts = amounts[:idx+1]

        # Create a pieplot
        fig = plt.figure(dpi=800)
        plt.style.use('fivethirtyeight')
        ax = fig.add_subplot(1, 1, 1)

        patches, texts, autotexts = ax.pie(amounts, labels=names, autopct='%1.1f%%', labeldistance=1.05, counterclock=False)
        [_.set_fontsize(10) for _ in texts]
        [_.set_fontsize(10) for _ in autotexts]

        ax.set_title("{}\nRs. {}".format(tree_name.title(), sum(amounts)), fontdict={'fontsize': 12})

        # draw a circle at the center of pie to make it look like a donut
        centre_circle = plt.Circle((0, 0), 0.75, color='black', fc='white', linewidth=1.1)
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)

        # Set aspect ratio to be equal so that pie is drawn as a circle.
        plt.axis('equal')
    else:
        return None

    dir_path = os.path.dirname(os.path.realpath(__file__))
    image_file = os.path.join(dir_path, 'reports/{}_category_report_{}_{}.png'.format(tree_name, start_date, end_date))

    try:
        plt.savefig(image_file, bbox_inches='tight')
        plt.close(fig)
    except Exception as e:
        print 'Could not save image to file: {}'.format(e.__str__())
        plt.close(fig)
        return None

    return image_file


def generate_vendor_wise_report(transactions, start, end):
    expense_transactions = get_expense_transactions_from_transactions(transactions)

    vendor_cat_amount_dict = dict()

    for tran in expense_transactions:
        vendor = tran.vendor
        category_leaf_node = tran.category_path.split('|')[-1]

        vendor_display_name = vendor + ' ({})'.format(category_leaf_node)
        amount = tran.amount

        if vendor_display_name in vendor_cat_amount_dict:
            vendor_cat_amount_dict[vendor_display_name] += amount
        else:
            vendor_cat_amount_dict[vendor_display_name] = amount

    sorted_vendor_cat_amount_tups = sorted(vendor_cat_amount_dict.items(), key=operator.itemgetter(1), reverse=True)

    names = [tup[0].split('|')[-1] for tup in sorted_vendor_cat_amount_tups if tup[1] > 0.0]
    amounts = [tup[1] for tup in sorted_vendor_cat_amount_tups if tup[1] > 0.0]

    if len(names):
        percents = [float(amount) / sum(amounts) for amount in amounts]

        idx = -1
        for i in range(len(percents) - 1, -1, -1):
            if percents[i] >= 0.01 and idx == -1:
                idx = i

        names = names[:idx+1]
        amounts = amounts[:idx+1]

        # Create a pieplot
        fig = plt.figure(dpi=800)
        plt.style.use('fivethirtyeight')
        ax = fig.add_subplot(1, 1, 1)

        patches, texts, autotexts = ax.pie(amounts, labels=names, autopct='%1.1f%%', labeldistance=1.05, counterclock=False)
        [_.set_fontsize(10) for _ in texts]
        [_.set_fontsize(10) for _ in autotexts]
        ax.set_title("Vendor Report\nRs. {}".format(sum(amounts)), fontdict={'fontsize': 12})

        # draw a circle at the center of pie to make it look like a donut
        centre_circle = plt.Circle((0, 0), 0.75, color='black', fc='white', linewidth=1.1)
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)

        # Set aspect ratio to be equal so that pie is drawn as a circle.
        plt.axis('equal')
    else:
        return None

    dir_path = os.path.dirname(os.path.realpath(__file__))
    image_file = os.path.join(dir_path, 'reports/vendor_report_{}_{}.png'.format(start, end))

    try:
        plt.savefig(image_file, bbox_inches='tight')
        plt.close(fig)
    except Exception as e:
        print 'Could not save image to file: {}'.format(e.__str__())
        plt.close(fig)
        return None

    return image_file


def generate_date_splits_wise_report(date_splits, date_split_names, transactions):
    split_incomes = list()
    split_expenses = list()

    for date_split in date_splits:
        split_transactions = get_transactions_in_date_range_from_transactions(transactions, date_split[0],
                                                                              date_split[-1])

        split_incomes.append(get_total_income_from_transactions(split_transactions))
        split_expenses.append(-1.0 * get_total_expense_from_transactions(split_transactions))

    print split_incomes
    print split_expenses

    fig = plt.figure(dpi=800)
    plt.style.use('fivethirtyeight')
    ax = fig.add_subplot(1, 1, 1)

    ax.bar(date_split_names, split_expenses, color='red')
    ax.bar(date_split_names, split_incomes, color='green')

    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(10)
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(10)

    total_income = sum(split_incomes) + sum(split_expenses)
    if total_income > 0.0:
        sign = '+'
    elif total_income == 0.0:
        sign = ''
    else:
        sign = '-'

    ax.set_title('Net Income\n{} Rs {}'.format(sign, np.abs(total_income)), fontdict={'fontsize': 12})

    dir_path = os.path.dirname(os.path.realpath(__file__))
    image_file = os.path.join(dir_path,
                              'reports/date_report_{}_{}.png'.format(date_splits[0][0], date_splits[-1][-1]))

    try:
        plt.savefig(image_file, bbox_inches='tight')
        plt.close(fig)
    except Exception as e:
        print 'Could not save image to file: {}'.format(e.__str__())
        plt.close(fig)
        return None

    return image_file


class Report():
    def __init__(self, start, end):
        print 'Date related operations..\n'
        self.start_date = start
        self.end_date = end
        self.start_datetime = get_datetime_obj(start)
        self.end_datetime = get_datetime_obj(end)
        self.all_datetimes = get_between_dateobjects(start, end)
        self.all_dates = get_between_dates(start, end)
        self.number_of_days = len(self.all_dates)

        print 'Getting date splits..\n'
        self.date_splits = split_date_range(start, end)
        self.date_split_names = get_date_split_names(self.date_splits)

        print 'Getting transactions..\n'
        self.transactions = get_transactions(start, end)
        self.transactions_dataframe = self.get_dataframe_from_transactions()

        self.total_income = get_total_income_from_transactions(self.transactions)
        self.total_expense = get_total_expense_from_transactions(self.transactions)
        self.net_income = self.total_income - self.total_expense

        # Generate Reports
        print 'Generating date wise report..\n'
        self.date_report = self.generate_date_splits_wise_report()

        print 'Generating category reports..\n'
        self.income_category_report = self.generate_category_wise_report('income')
        self.expense_category_report = self.generate_category_wise_report('expenses')

        self.vendor_report = self.generate_vendor_wise_report()

        self.debt_names, self.debt_values = self.get_debt_and_loan()

        # Mail the reports
        print 'Mailing the report'
        self.send_report()

    def get_dataframe_from_transactions(self):
        amounts = list()
        sources = list()
        vendors = list()
        categories = list()
        times = list()

        for tran in self.transactions:
            amounts.append(tran.amount)
            sources.append(tran.source)
            vendors.append(tran.vendor)
            categories.append(tran.category_path)
            times.append(tran.time)

        df = pd.DataFrame(
            {'Amount': amounts, 'Source': sources, 'Vendor': vendors, 'Category': categories, 'Time': times})
        df = df[['Time', 'Source', 'Vendor', 'Category', 'Amount']]

        dir_path = os.path.dirname(os.path.realpath(__file__))
        df_file = os.path.join(dir_path, 'reports/transactions_{}_{}.csv'.format(self.date_splits[0][0], self.date_splits[-1][-1]))

        try:
            df.to_csv(df_file)
        except Exception as e:
            print 'Could not save dataframe to file: {}'.format(e.__str__())
            return None

        return df_file

    def get_debt_and_loan(self):
        category_tree = category_tree_dictionary['debt/loan']
        nodes = category_tree.children

        node_amount_dictionary = dict()
        for node in nodes:
            node_transactions = get_transactions_of_leaf_nodes_below_any_node_from_transactions(self.transactions, node)

            node_amount_dictionary[get_path_string_from_root_to_node(node)] = get_total_income_from_transactions(
                node_transactions) - get_total_expense_from_transactions(node_transactions)

        sorted_node_amount_dictionary = sorted(node_amount_dictionary.items(), key=operator.itemgetter(1), reverse=True)

        names = [tup[0].split('|')[-1] for tup in sorted_node_amount_dictionary]
        amounts = [tup[1] for tup in sorted_node_amount_dictionary]

        return names, amounts

    def generate_date_splits_wise_report(self):
        split_incomes = list()
        split_expenses = list()

        for date_split in self.date_splits:
            split_transactions = get_transactions_in_date_range_from_transactions(self.transactions, date_split[0],
                                                                                  date_split[-1])

            split_incomes.append(get_total_income_from_transactions(split_transactions))
            split_expenses.append(-1.0 * get_total_expense_from_transactions(split_transactions))

        fig = plt.figure(dpi=800)
        plt.style.use('fivethirtyeight')
        ax = fig.add_subplot(1, 1, 1)

        ax.bar(self.date_split_names, split_expenses, color='red')
        ax.bar(self.date_split_names, split_incomes, color='green')

        for tick in ax.xaxis.get_major_ticks():
            tick.label.set_fontsize(10)
        for tick in ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(10)

        total_income = sum(split_incomes) + sum(split_expenses)
        if total_income > 0.0:
            sign = '+'
        elif total_income == 0.0:
            sign = ''
        else:
            sign = '-'

        ax.set_title('Net Income\n{} Rs {}'.format(sign, np.abs(total_income)), fontdict={'fontsize': 12})

        dir_path = os.path.dirname(os.path.realpath(__file__))
        image_file = os.path.join(dir_path,
                                  'reports/date_report_{}_{}.png'.format(self.date_splits[0][0], self.date_splits[-1][-1]))

        try:
            plt.savefig(image_file, bbox_inches='tight')
            plt.close(fig)
        except Exception as e:
            print 'Could not save image to file: {}'.format(e.__str__())
            plt.close(fig)
            return None

        return image_file

    def generate_category_wise_report(self, tree_name, level='top'):
        category_tree = category_tree_dictionary[tree_name]

        if level == 'top':
            nodes = category_tree.children
        else:
            nodes = get_all_leaf_nodes_below_any_node(category_tree)

        node_amount_dictionary = dict()
        for node in nodes:
            node_amount_dictionary[
                get_path_string_from_root_to_node(node)] = node_total_expense_or_income_from_transactions(self.transactions, node)

        sorted_node_amount_dictionary = sorted(node_amount_dictionary.items(), key=operator.itemgetter(1), reverse=True)
        names = [tup[0].split('|')[-1] for tup in sorted_node_amount_dictionary if tup[1] > 0.0]
        amounts = [tup[1] for tup in sorted_node_amount_dictionary if tup[1] > 0.0]

        if len(names):
            percents = [float(amount) / sum(amounts) for amount in amounts]

            idx = -1
            for i in range(len(percents) - 1, -1, -1):
                if percents[i] > 0.005 and idx == -1:
                    idx = i

            names = names[:idx + 1]
            amounts = amounts[:idx + 1]

            # Create a pieplot
            fig = plt.figure(dpi=800)
            plt.style.use('fivethirtyeight')
            ax = fig.add_subplot(1, 1, 1)

            patches, texts, autotexts = ax.pie(amounts, labels=names, autopct='%1.1f%%', labeldistance=1.05,
                                               counterclock=False)
            [_.set_fontsize(10) for _ in texts]
            [_.set_fontsize(10) for _ in autotexts]

            ax.set_title("{}\nRs. {}".format(tree_name.title(), sum(amounts)), fontdict={'fontsize': 12})

            # draw a circle at the center of pie to make it look like a donut
            centre_circle = plt.Circle((0, 0), 0.75, color='black', fc='white', linewidth=1.1)
            fig = plt.gcf()
            fig.gca().add_artist(centre_circle)

            # Set aspect ratio to be equal so that pie is drawn as a circle.
            plt.axis('equal')
        else:
            return None

        dir_path = os.path.dirname(os.path.realpath(__file__))
        image_file = os.path.join(dir_path, 'reports/{}_category_report_{}_{}.png'.format(tree_name, self.start_date, self.end_date))

        try:
            plt.savefig(image_file, bbox_inches='tight')
            plt.close(fig)
        except Exception as e:
            print 'Could not save image to file: {}'.format(e.__str__())
            plt.close(fig)
            return None

        return image_file

    def generate_vendor_wise_report(self):
        expense_transactions = get_expense_transactions_from_transactions(self.transactions)

        vendor_cat_amount_dict = dict()

        for tran in expense_transactions:
            vendor = tran.vendor
            category_leaf_node = tran.category_path.split('|')[-1]

            vendor_display_name = vendor + ' ({})'.format(category_leaf_node)
            amount = tran.amount

            if vendor_display_name in vendor_cat_amount_dict:
                vendor_cat_amount_dict[vendor_display_name] += amount
            else:
                vendor_cat_amount_dict[vendor_display_name] = amount

        sorted_vendor_cat_amount_tups = sorted(vendor_cat_amount_dict.items(), key=operator.itemgetter(1), reverse=True)

        names = [tup[0].split('|')[-1] for tup in sorted_vendor_cat_amount_tups if tup[1] > 0.0]
        amounts = [tup[1] for tup in sorted_vendor_cat_amount_tups if tup[1] > 0.0]

        if len(names):
            percents = [float(amount) / sum(amounts) for amount in amounts]

            idx = -1
            for i in range(len(percents) - 1, -1, -1):
                if percents[i] >= 0.01 and idx == -1:
                    idx = i

            names = names[:idx + 1]
            amounts = amounts[:idx + 1]

            # Create a pieplot
            fig = plt.figure(dpi=800)
            plt.style.use('fivethirtyeight')
            ax = fig.add_subplot(1, 1, 1)

            patches, texts, autotexts = ax.pie(amounts, labels=names, autopct='%1.1f%%', labeldistance=1.05,
                                               counterclock=False)
            [_.set_fontsize(10) for _ in texts]
            [_.set_fontsize(10) for _ in autotexts]
            ax.set_title("Vendor Report\nRs. {}".format(sum(amounts)), fontdict={'fontsize': 12})

            # draw a circle at the center of pie to make it look like a donut
            centre_circle = plt.Circle((0, 0), 0.75, color='black', fc='white', linewidth=1.1)
            fig = plt.gcf()
            fig.gca().add_artist(centre_circle)

            # Set aspect ratio to be equal so that pie is drawn as a circle.
            plt.axis('equal')
        else:
            return None

        dir_path = os.path.dirname(os.path.realpath(__file__))
        image_file = os.path.join(dir_path, 'reports/vendor_report_{}_{}.png'.format(self.start_date, self.end_date))

        try:
            plt.savefig(image_file, bbox_inches='tight')
            plt.close(fig)
        except Exception as e:
            print 'Could not save image to file: {}'.format(e.__str__())
            plt.close(fig)
            return None

        return image_file

    def send_report(self):
        # Text and Images to be sent
        email_text = ''
        email_text += '\n=========================================\n\n'

        email_text += "Total Expense: Rs. {:.2f}\n".format(self.total_expense)
        email_text += "Total Income: Rs. {:.2f}\n".format(self.total_income)
        email_text += '\n=========================================\n\n'

        # Debt and Loan Details
        if any([value > 0.0 for value in self.debt_values]):
            for name, value in zip(self.debt_names, self.debt_values):
                email_text += '{}: Rs. {}\n'.format(name, value)
            email_text += '\n=========================================\n\n'

        transactions = [self.transactions_dataframe]

        # 3 or 4 plots
        relevant_plots = list()
        relevant_plots.append(self.date_report)
        relevant_plots.append(self.expense_category_report)
        if self.income_category_report is not None:
            relevant_plots.append(self.income_category_report)
        relevant_plots.append(self.vendor_report)

        # Content and Subject
        contents = [email_text]
        contents.extend(transactions)
        contents.extend(relevant_plots)

        subject = 'Expense Report: {} to {}'.format(get_readable_name_from_datetime(self.start_datetime), get_readable_name_from_datetime(self.end_datetime))

        # Get email credentials
        dir_path = os.path.dirname(os.path.realpath(__file__))
        credentials_file = os.path.join(dir_path, 'data/email_credentials.json')

        with open(credentials_file, 'r') as f:
            email_credentials = json.load(f)

        login_user = email_credentials['login_details']['user']
        login_password = email_credentials['login_details']['password']

        receiver_email_address = email_credentials['receiver_details']['email_address']
        sent = send_email(login_user, login_password, receiver_email_address, subject, contents)

        return sent
