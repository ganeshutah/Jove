#Tyler Sorensen
#University of Utah
#March 1, 2012
#dot_bdd.py

#This simply prints a .dot file for visualizing the bdd

#Only public function
def print_bdd(bdd, fileName):
    """
    Generate a dot file with the bdd in it. Run the dot file through
    dot and generate a ps file.
    """
    #open the file
    print('bdd in dot file', bdd)
    print('filename in dot', fileName)
    
    f1 = open(fileName, 'w')

    #Give it a readable header
    _prDotHeader(f1)

    #Print the Nodes
    _prNodes(f1, bdd)

    #Print the ranks
    _prRanks(f1, bdd)

    #Determine and print the edges
    _prEdges(f1, bdd, bdd["u"], [])

    #Close the file
    _prClosing(f1)
    print("dot printed")

def _prClosing(f1):
    """
    A nice readable closing
    """
    f1.write("/* Unix command: dot -Tps bdd.dot > bdd.ps */\n")
    f1.write(r"/* For further details, see the `dot' manual */")
    f1.write("\n}")

def _prDotHeader(f1):
    """
    Header that sets up initial variables and settings
    """
    f1.write("digraph G {\n"        )
    f1.write("/* Defaults */\n"     )
    f1.write(" fontsize = 12;\n"    )
    f1.write(" graph [dpi = 600];\n"    )
    f1.write(" ratio = compress; \n")
    f1.write("/* Bounding box */\n" )
    f1.write(" size = \"4,4\";\n"     )

def _prNodes(f1, bdd):
    """
    prints the definition for the Nodes
    """
    u = bdd["u"]
    if u != 1:
        s = "Node0 [label=0, color=Red, shape=box, peripheries=2]\n"
        f1.write(s)

    if u != 0:
        s = "Node1 [label=1, color=Blue, shape=box, peripheries=2]\n"
        f1.write(s)

    for q in bdd["t_table"]:
        if q != 0 and q!= 1:
            s = "Node%i " % q
            s = "%s[label=%s" % (s, _get_var_name(bdd,q))
            s = "%s, shape=circle, peripheries=1]\n" % s
            f1.write(s)

#Helper for _prNodes
def _get_var_name(bdd, u):
    """
    Given a variable index u in the BDD, return the variable
    Name
    """
    var_index = bdd["t_table"][u][0]-1
    return bdd["var_order"][var_index]

def _prEdges(f1, bdd, u, drawn_list):
    """
    Recursive function to draw all the edges.
    Red for low, Blue for High
    """
    if u == 1:
        return
    if u == 0:
        return

    if u not in drawn_list:
        s = "Node%i->Node%i [color=red, label = \"0\"]\n" % (u, bdd["t_table"][u][1])
        f1.write(s)
        
        s = "Node%i->Node%i [color=blue, label = \"1\"]\n" % (u, bdd["t_table"][u][2])
        f1.write(s)
        
        _prEdges(f1, bdd, bdd["t_table"][u][1], drawn_list)
        _prEdges(f1, bdd, bdd["t_table"][u][2], drawn_list)
        drawn_list.append(u)

def _prRanks(f1, bdd):
    """
    Make all the nodes with the same variables the same rank
    """
    ar = [0]*len(bdd["var_order"])
    
    #Count how many times each variable appears
    for q in bdd["t_table"]:
        if q != 0 and q != 1:
            ar[bdd["t_table"][q][0]-1] += 1

    i = 0
    while i < len(bdd["var_order"]):
        
        if ar[i] > 1:
            l = find(bdd, i)
            s = "{rank=same;"
            for q in l:
                s = "%s Node%s" % (s, str(q))

            s = "%s}\n" % s
            f1.write(s)

        i += 1

#Helper function for prRanks
def find(bdd, i):
    """
    returns a list of all the u numbers of variable i
    """
    l = []
    for q in bdd["t_table"]:
        if bdd["t_table"][q][0]-1 == i:
            l.append(q)

    return l
