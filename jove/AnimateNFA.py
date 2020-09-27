import os
import contextlib
from jove.AnimationUtils import *

with open(os.devnull, 'w') as devnull:
    with contextlib.redirect_stdout(devnull):
        from jove.DotBashers import *
        from jove.Def_NFA import *

import ipywidgets as widgets
from ipywidgets import Layout
from IPython.display import display, clear_output, Javascript, HTML
from traitlets import Unicode, validate, List, observe, Instance
from graphviz import Source


class AnimateNFA:
    '''
    This is the NFA animation class.
    Call it with the NFA to be animated, and also FuseEdges=True/False
    to draw the NFA with edges either fused or not.
    For producing drawings in Colab, it is important to have these in
    every cell that calls animation.
    
    AnimateNFA(myNFA, FuseEdges='True/False')
    followed by
    display(HTML('<link rel="stylesheet" href="//stackpath.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css"/>'))

    Then the animation works in one's own install or Colab.
    '''
    
    def __init__(self, m_desc,
                 FuseEdges=False,
                 pick_start=False,
                 max_width=10.0,
                 accept_color='chartreuse3',
                 reject_color='red',
                 neutral_color='dodgerblue2'):
        # Options
        self.color_accept = accept_color
        self.color_reject = reject_color
        self.color_neutral = neutral_color
        self.max_width = max_width
        self.fuse = FuseEdges
        # DFA specific option
        
        self.valid_input = True
        self.machine = m_desc
        self.machine_obj = dotObj_nfa(self.machine, FuseEdges=FuseEdges)
        self.copy_source = reformat_edge_labels(set_graph_size(self.machine_obj.source, max_width),
                                                additional=' color=black arrowsize=1 penwidth=1')
        
        # Set things we need for the animation
        self.machine_steps = []
        self.feed_steps = []
        self.from_nodes = self.machine['Q0']
        self.to_nodes = self.machine['Q0']
        self.animated = False
        
        # Setup the widgets
        # Top row for user input
        self.user_input = widgets.Text(value='',
                                       placeholder='Sigma: {{{}}}'.format(','.join(sorted(self.machine['Sigma']))),
                                       description='Input:',
                                       layout=Layout(width='500px')
                                       )
        self.user_input.observe(self.on_input_change, names='value')   
        self.alternate_start = widgets.SelectMultiple(options=sorted(self.machine['Q']),
                                                      value=tuple(self.machine['Q0']),
                                                      rows=5,
                                                      description='Start States:',
                                                      disabled=False,
                                                      layout=Layout(width='200px')
                                                      )
        self.generate_button = widgets.Button(description="Animate", 
                                              button_style='primary', 
                                              disabled=False
                                              )
        self.generate_button.on_click(self.generate_animation)

        # Bottom row for player controls
        self.play_controls = widgets.Play(interval=950,
                                          value=0,
                                          min=0,
                                          max=100,
                                          step=1,
                                          description="Press play"
                                          )
        self.play_controls.observe(self.on_play_step, names='value')

        self.speed_control = widgets.IntSlider(value=1,
                                               min=1,
                                               max=10,
                                               step=1,
                                               description='Speed:',
                                               disabled=False,
                                               continuous_update=False,
                                               orientation='horizontal',
                                               readout=True,
                                               readout_format='d'
                                               )
        self.speed_control.observe(self.on_speed_change, names='value')
                
        # Create the controls for stepping through the animation
        self.backward = widgets.Button(icon='step-backward', 
                                       layout=Layout(width='40px'), 
                                       disabled=True
                                       )
        self.forward = widgets.Button(icon='step-forward', 
                                      layout=Layout(width='40px'),
                                      disabled=True
                                      )
        self.backward.on_click(self.on_backward_click)
        self.forward.on_click(self.on_forward_click)
        
        # set the widget to display the machine
        self.machine_display = widgets.Output()
        with self.machine_display:
            display(Source(self.copy_source))
            
        # set the widget to display the feed
        self.feed_display = widgets.Output()

        # arrange the widgets in the display area
        row1 = widgets.HBox([self.user_input, self.generate_button])
        if pick_start:
            row1 = widgets.HBox([self.user_input, self.alternate_start, self.generate_button])
        row2 = widgets.HBox([self.play_controls, self.backward, self.forward, self.speed_control])
        w = widgets.VBox([row1, self.machine_display, self.feed_display, row2])
        display(w)
        
        self.play_controls.disabled = True
        self.forward.disabled = True
        self.backward.disabled = True
        self.speed_control.disabled = True
        
    def on_speed_change(self, change):
        self.play_controls.interval = 1000 - 50 * change['new']

    def on_backward_click(self, b):
        self.play_controls._playing = False      
        self.play_controls.value -= 1
    
    def on_forward_click(self, b):
        self.play_controls._playing = False        
        self.play_controls.value += 1

    def generate_animation(self, change):
        if self.animated:
            self.play_controls._playing = False
            self.animated = False
            self.user_input.disabled = False
            self.alternate_start.disabled = False
            self.generate_button.description = 'Animate'
            with self.machine_display:
                clear_output(wait=True)
                display(Source(self.machine_obj))
            with self.feed_display:
                clear_output()
            self.play_controls.disabled = True
            self.forward.disabled = True
            self.backward.disabled = True
            self.speed_control.disabled = True
            # clean the machine display
            with self.machine_display:
                clear_output(wait=True)
                display(Source(self.copy_source))
        
        else:
            # ignore invalid input
            if not self.valid_user_input():
                return
            # clean-up animation
            self.animated = True
            self.user_input.disabled = True
            self.alternate_start.disabled = True
            self.generate_button.description='Change Input'
            self.feed_steps = []
            self.machine_steps = []
            
            self.play_controls.max = len(self.user_input.value)*3
            # generate the feed display
            for i in range(self.play_controls.max+1):
                self.feed_steps.append(self.generate_feed(i))
                self.machine_steps.append(self.generate_machine_steps(i))
            with self.feed_display:
                clear_output(wait=True)
                display(Source(self.feed_steps[0]))
            # display the machine            
            self.play_controls.value = 0
            self.on_play_step({'new':0})
        
            # enable the controls
            self.backward.disabled = True
            if len(self.user_input.value) == 0:
                self.forward.disabled = True
            else:
                self.forward.disabled = False
            self.play_controls.disabled = False
            self.speed_control.disabled = False

    def valid_user_input(self):
        # make sure the input is valid
        for c in self.user_input.value:
            if c not in self.machine['Sigma']:
                return False
        return True
    
    def on_input_change(self, change):
        # check for valid user input
        if not self.valid_user_input():
            self.generate_button.button_style = 'danger'
            self.generate_button.description = 'Invalid Input'
        else:
            self.generate_button.button_style = 'primary'
            self.generate_button.description = 'Animate'

    def on_play_step(self, change): 
        # set the step controls
        if change['new'] == 0:
            self.backward.disabled = True
            self.forward.disabled = False
        elif change['new'] == self.play_controls.max:
            self.backward.disabled = False
            self.forward.disabled = True
        else:
            self.backward.disabled = False
            self.forward.disabled = False
                
        # display the machine for this step
        with self.machine_display:
            clear_output(wait=True)
            display(Source(self.machine_steps[change['new']]))
        # display the feed for this step
        with self.feed_display:
            clear_output(wait=True)
            display(Source(self.feed_steps[change['new']]))
    
    def generate_machine_steps(self, step):
        # on first step reset start node
        if step == 0:
            self.from_nodes = set([i for i in self.alternate_start.value])
            self.to_nodes = self.from_nodes
            e_close_nodes = set()
            m_state = color_nodes(self.copy_source, self.from_nodes, self.color_neutral)
            for node in self.to_nodes:
                intermediates = Eclosure(self.machine, {node})
                m_state = self.set_eclose_display(m_state, node, intermediates, self.color_neutral)
                e_close_nodes = e_close_nodes | intermediates
            self.to_nodes = self.to_nodes | e_close_nodes
            self.from_nodes = self.to_nodes
            return m_state
            
        # check if the set of states is empty
        if len(self.to_nodes) == 0:
            # do something dramatic
            return self.set_graph_color(self.copy_source, self.color_reject)
            
        # on the last step check for acceptance
        elif step == self.play_controls.max:
            # if any node is in the set of final states then color all the nodes green
            for node in self.to_nodes:
                if node in self.machine['F']:
                    return color_nodes(self.copy_source, self.to_nodes, self.color_accept)
            # otherwise color all of them red
            return color_nodes(self.copy_source, self.to_nodes, self.color_reject)
        
        # primary steps we are on a node
        elif step % 3 == 0:
            self.from_nodes = self.to_nodes
            return color_nodes(self.copy_source, self.from_nodes, self.color_neutral)
            
        # secondary steps we are on an edge
        elif step % 3 == 1:
            self.to_nodes = set()
            m_state = self.copy_source
            for node in self.from_nodes:
                intermediates = step_nfa(self.machine, node, self.user_input.value[step//3])
                m_state = self.set_edge_display(m_state, node, intermediates, self.user_input.value[step//3], self.color_neutral)
                self.to_nodes = self.to_nodes | intermediates
            return m_state
            
        # tertiary steps are e-closure
        else:
            e_close_nodes = set()
            m_state = self.machine_steps[step-1]           
            for node in self.to_nodes:
                intermediates = Eclosure(self.machine, {node})
                m_state = self.set_eclose_display(m_state, node, intermediates, self.color_neutral)
                e_close_nodes = e_close_nodes | intermediates
            self.to_nodes = self.to_nodes | e_close_nodes
            return m_state

#    def set_node_display(self, node_set, color):
#        m_state = self.copy_source
#        for node in node_set:
#            place = m_state.find(']', m_state.find('{} ['.format(node)))
#            m_state = m_state[:place] + ' fontcolor=white fillcolor={} style=filled'.format(color) + m_state[place:]
#        return m_state
    
    def set_edge_display(self, m_state, src_node, node_set, i, color):
        i = special[i] if i in special.keys() else i
        for n in node_set:
            # style the ending node if it not already
            node_start = m_state.find('\t{} ['.format(n))
            node_end = m_state.find(']', node_start)
            node_desc = m_state[node_start:node_end+1]
            if 'fontcolor=' not in node_desc:
                m_state =  m_state[:node_end] + ' fontcolor="{}" fillcolor=white color="{}" style=filled penwidth=2'.format(color,color) + m_state[node_end:]
            # style the edge between node and n
            label_start = -1
            if self.fuse:
                label_start = m_state.find('=', m_state.find('\t{} -> {}'.format(src_node,n)))
            else:
                label_start = m_state.find('=', m_state.find('\t{} -> {} [label=< {}>'.format(src_node,n,i)))
            label_end = m_state.find('> color', label_start)
            replace_label = m_state[label_start:label_end]
            replace_label = replace_label.replace(' {}'.format(i), '<font color="{}"> {}</font>'.format(color,i))
            edge_end = m_state.find(']', label_start)
            replace_style = m_state[label_end:edge_end]
            replace_style = replace_style.replace('> color=black arrowsize=1 penwidth=1','> color="{}" arrowsize=1.5 penwidth=2'.format(color))
            m_state = m_state[:label_start] + replace_label + replace_style + m_state[edge_end:]
        return m_state
    
    def set_eclose_display(self, m_state, src_node, node_set, color):
        for n in node_set:
            # style the ending node if it not already
            node_start = m_state.find('\t{} ['.format(n))
            node_end = m_state.find(']', node_start)
            node_desc = m_state[node_start:node_end+1]
            if 'fontcolor=' not in node_desc:
                m_state =  m_state[:node_end] + ' fontcolor="{}" fillcolor=white color="{}" style=filled penwidth=2'.format(color,color) + m_state[node_end:]
            # style the edge between node and n
            label_start = -1
            if self.fuse:
                label_start = m_state.find('=', m_state.find('\t{} -> {}'.format(src_node, n)))
            else:
                label_start = m_state.find('=', m_state.find('\t{} -> {} [label=< {}>'.format(src_node, n, '&#39;&#39;')))
            label_end = m_state.find('> color', label_start)
            replace_label = m_state[label_start:label_end]
            if '&#39;&#39;' in replace_label:
                replace_label = replace_label.replace(' &#39;&#39;', '<font color="{}"> &#39;&#39;</font>'.format(color))
                edge_end = m_state.find(']', label_start)
                replace_style = m_state[label_end:edge_end]
                replace_style = replace_style.replace('> color=black arrowsize=1 penwidth=1','> color="{}" arrowsize=1.5 penwidth=2'.format(color))
                m_state = m_state[:label_start] + replace_label + replace_style + m_state[edge_end:]
        return m_state
    
    def set_graph_color(self, m_state, color):
        # do thing here
        place = m_state.find(']', m_state.find('graph'))+1
        m_state = m_state[:place] + '\n\tnode [fontcolor={} fillcolor=white color={} style=filled];'.format(color,color) + m_state[place:]
        m_state = m_state.replace(' color=black arrowsize=1 penwidth=1', ' color={} fontcolor={} arrowsize=1 penwidth=1'.format(color,color))
        return m_state
    
    def generate_feed(self, step):
        input_string = self.user_input.value
        if step == 0:
            return write_feed_source('', '  ', replace_special(input_string), self.max_width)
        elif step == self.play_controls.max:
            return write_feed_source(replace_special(input_string), '  ', '', self.max_width)
        elif step % 3 == 0:
            return write_feed_source(replace_special(input_string[:step//3]), '  ',
                                     replace_special(input_string[step//3:]), self.max_width)
        elif step % 3 == 1:
            return write_feed_source(replace_special(input_string[:step//3]),
                                     replace_special(input_string[step//3]),
                                     replace_special(input_string[step//3+1:]), self.max_width)
        else:
            return write_feed_source(replace_special(input_string[:step//3+1]), '&#39;&#39;',
                                     replace_special(input_string[step//3+1:]), self.max_width)

print(''' "help(AnimateNFA)" gives you info on how to use animations with NFA ''')
