from anytree import Node, RenderTree


def get_category_tree_from_file(file_name):
    with open(file_name, 'r') as f:
        lines = f.readlines()

        tree_name = lines[0].strip()
        root = Node(tree_name)

        for line in lines[1:]:
            strings = line.strip().split(",")

            category_name = strings[0].strip()
            children = [child.strip() for child in strings[1:] if child != '']

            category_node = Node(category_name, parent=root)

            if len(children):
                for child in children:
                    child_node = Node(child, parent=category_node)

    return root


def print_tree(root):
    for pre, fill, node in RenderTree(root):
        print("%s%s" % (pre, node.name))


expenses_categories_file = '/Users/sravan/Desktop/projects/expense-tracker/expense_tracker/data/expenses_categories.txt'
income_categories_file = '/Users/sravan/Desktop/projects/expense-tracker/expense_tracker/data/income_categories.txt'
debt_loan_categories_file = '/Users/sravan/Desktop/projects/expense-tracker/expense_tracker/data/debt_loan_categories.txt'

expenses_category_tree = get_category_tree_from_file(expenses_categories_file)
income_category_tree = get_category_tree_from_file(income_categories_file)
debt_loan_category_tree = get_category_tree_from_file(debt_loan_categories_file)

category_tree_dictionary = {'expenses': expenses_category_tree, 'income': income_category_tree, 'debt/loan': debt_loan_category_tree}

# print_tree(expenses_category_tree)
# print_tree(income_category_tree)
# print_tree(debt_loan_category_tree)