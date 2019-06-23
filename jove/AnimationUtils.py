special = {'[': '&#91;',
           ']': '&#93;',
           '{': '&#123;',
           '}': '&#125;',
           '(': '&#40;',
           ')': '&#41;',
           '<': '&#8249;',
           '>': '&#8250;',
           '\'': '&apos;',
           '\'\'': '&apos;&apos;',
           '"': '&#34'}


def replace_special(line):
    """
    Replaces every instance of the characters in 'special' with their corresponding HTML code

    :param line: A string
    :return: A string
    """
    for k in special.keys():
        line = line.replace(k, special[k])
    return line


def set_graph_color(graph_description, color):
    """
    Sets the color of graph using the graphviz color option which is applied first.
    If subsequent nodes or edges also set a color option these will take precedence.

    :param graph_description: A source string of a graphviz digraph
    :param color: A color name or HTML color code
    :return: A graphviz digraph source
    """
    place = graph_description.find(']', graph_description.find('graph')) + 1
    graph_description = graph_description[
              :place] + '\n\tnode [fontcolor={} fillcolor=white color={} style=filled];\n\tedge [color={} fontcolor={}];'.format(
        color, color, color, color) + graph_description[place:]
    return graph_description


def set_graph_size(graph_description, dim):
    """
    Sets the maximum width/height using the graphviz size option. The graph is shrunk until
    the width and height are less than dim while maintaining the aspect ratio of the graph

    :param graph_description: A source string of a graphviz digraph
    :param dim: The maximum width and height of the graph in inches
    :return: A graphviz digraph source
    """
    # set the size of the whole graph
    place = graph_description.find(']', graph_description.find('graph'))
    graph_description = graph_description[:place] + ' size={}'.format(dim) + graph_description[place:]
    return graph_description


def set_graph_label(graph_description, message, location):
    """
    Adds a label to the graph at location.

    :param graph_description: A source string of a graphviz digraph
    :param message: A string to display as part of the graph
    :param location: A string indicating the desired location of message. Valid args: 't', 'b'
    :return: A graphviz digraph source
    """
    place = graph_description.find(']', graph_description.find('graph')) + 1
    graph_description = graph_description[:place] + '\n\tlabelloc="{}";\n\tlabel={};'.format(location,message) + graph_description[place:]
    return graph_description


def reformat_edge_labels(graph_description):
    """
    Replaces the graph edge labels with HTML-like labels which support substring coloration

    :param graph_description: A source string of a graphviz digraph
    :return: A graphviz digraph source
    """
    # For each edge in the graph
    edge_pos = graph_description.find('->')
    while edge_pos != -1:
        # extract the next label
        label_start = graph_description.find('=', edge_pos) + 1
        label_end = graph_description.find('"]\n', label_start) + 1
        label = graph_description[label_start:label_end]
        # replace special characters and split into list of labels
        label = label.strip('"')
        label = replace_special(label)
        label_list = label.split('\n')
        # create an HTML-like label from the list of labels
        replacement = '<'
        for elem in range(len(label_list)):
            replacement += ' {}'.format(label_list[elem].strip())
            if elem != len(label_list)-1:
                replacement += '<br/>'
        replacement += '>'
        # splice the new label into the graph
        graph_description = graph_description[:label_start] + replacement + graph_description[label_end:]
        edge_pos = graph_description.find('->', label_end)
    # return the graph which has had all edge labels replaced
    return graph_description
