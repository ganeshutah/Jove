
# coding: utf-8

# In[2]:


#-- Youtube, Python Widgets, Dot graphs, ...

from IPython.display import YouTubeVideo
import ipywidgets as wdg

#-- Useful Python functions

# product(set, set) generates the cartesian product
from itertools import product

# For copy.deepcopy(structure) produces a deep copy of the structure
import copy

# For random.choice(list) produces a random pick from the list
import random

# reduce(lambda x,y: x+y, [], -1000) or reduce(lambda x,y: x+y, [1]) or reduce(lambda x,y: x+y, [1,2])
# -1000 is default
from functools import reduce

# Graphviz functions : produce dot files or display files or dot objects
from graphviz import Digraph, Source

# datetime.datetime.now() - help obtain time in various formats
import datetime


#--end of imports, 5/28/17

