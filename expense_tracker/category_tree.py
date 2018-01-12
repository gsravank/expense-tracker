from anytree import Node, RenderTree, search, PreOrderIter


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


def get_node_from_node_name(node_name, root_node):
    nodes = search.findall(root_node, filter_=lambda node: node.name == node_name)
    if len(nodes):
        return nodes[0]
    else:
        return None


def get_path_string_from_root_to_node(node_name, sep='|'):
    node_names = list()

    for node in node_name.path:
        node_names.append(node.name)

    return sep.join(node_names)


def get_all_leaf_nodes_below_any_node(node_name):
    leaf_nodes = list()

    for node in PreOrderIter(node_name):
        if len(node.children) == 0:
            leaf_nodes.append(node)

    return leaf_nodes


expenses_categories_file = '/Users/sravan/Desktop/projects/expense-tracker/expense_tracker/data/expenses_categories.txt'
income_categories_file = '/Users/sravan/Desktop/projects/expense-tracker/expense_tracker/data/income_categories.txt'
debt_loan_categories_file = '/Users/sravan/Desktop/projects/expense-tracker/expense_tracker/data/debt_loan_categories.txt'

expenses_category_tree = get_category_tree_from_file(expenses_categories_file)
income_category_tree = get_category_tree_from_file(income_categories_file)
debt_loan_category_tree = get_category_tree_from_file(debt_loan_categories_file)
unknown_category_tree = Node('Unknown')

category_tree_dictionary = {'expenses': expenses_category_tree, 'income': income_category_tree, 'debt/loan': debt_loan_category_tree, 'unknown': unknown_category_tree}

# print_tree(expenses_category_tree)
# print_tree(income_category_tree)
# print_tree(debt_loan_category_tree)