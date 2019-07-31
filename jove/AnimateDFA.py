import os
import contextlib
from jove.AnimationUtils import *

with open(os.devnull, 'w') as devnull:
    with contextlib.redirect_stdout(devnull):
        from jove.DotBashers import *
        from jove.Def_DFA import *

import ipywidgets as widgets
from ipywidgets import Layout
from IPython.display import display, clear_output, Javascript, HTML
from traitlets import Unicode, validate, List, observe, Instance
from graphviz import Source

# TODO: resolve issue where replace may attempt to replace portions of html code
# TODO: this is an issue for AnimateDFA and AnimateNFA because they are replacing single characters

# TODO: NOTE - the above is potentially not prob


class AnimateDFA:    
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
        
        # Totalize the machine and display with blackhole
        self.machine = totalize_dfa(m_desc)
        self.machine_obj = dotObj_dfa_w_bh(self.machine, FuseEdges=FuseEdges)
        self.copy_source = reformat_edge_labels(set_graph_size(self.machine_obj.source, max_width))
        
        # Set things we need for the animation
#        self.forward_steps = []
#        self.backward_steps = []
        self.machine_steps = []
        self.feed_steps = []
#        self.is_back_step = False
        self.from_node = self.machine['q0']
        self.to_node = self.machine['q0']        
        self.animated = False
        
        # Setup the widgets
        # Top row for user input
        self.user_input = widgets.Text(value='',
                                       placeholder='Sigma: {{{}}}'.format(','.join(sorted(self.machine['Sigma']))),
                                       description='Input:',
                                       layout=Layout(width='500px')
                                       )
        self.user_input.observe(self.on_input_change, names='value')   
        self.generate_button = widgets.Button(description="Animate", 
                                              button_style='primary', 
                                              disabled=False)
        self.generate_button.on_click(self.generate_animation)
        self.alternate_start = widgets.Dropdown(options=sorted(self.machine['Q']),
                                                value=self.machine['q0'],
                                                description='Start State:',
                                                disabled=False,
                                                layout=Layout(width='200px')
                                                )

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

        # TODO: REMOVE TESTING CODE
        self.test_output = widgets.Output()

        # arrange the widgets in the display area
        row1 = widgets.HBox([self.user_input, self.generate_button])
        if pick_start:
            row1 = widgets.HBox([self.user_input, self.alternate_start, self.generate_button])
        row2 = widgets.HBox([self.play_controls, self.backward, self.forward, self.speed_control])
        w = widgets.VBox([row1, self.machine_display, self.feed_display, row2, self.test_output])
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
            self.generate_button.description = 'Change Input'
            self.feed_steps = []
            self.machine_steps = []

            self.play_controls.max = len(self.user_input.value)*2
            # generate the feed display
            for i in range(self.play_controls.max+1):
                self.feed_steps.append(self.generate_feed(i))
                self.machine_steps.append(self.generate_machine_steps(i))
            with self.feed_display:
                clear_output(wait=True)
                display(Source(self.feed_steps[0]))
            # display the machine            
            self.play_controls.value = 0
            self.on_play_step({'new': 0})

            #with self.test_output:
            #    for s in self.machine_steps:
            #        print(s)
        
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
            self.from_node = self.alternate_start.value
            self.to_node = self.from_node
        # on the last step check for acceptance
        if step == self.play_controls.max:
            if self.to_node in self.machine['F']:
                return color_nodes(self.copy_source, {self.to_node}, self.color_accept)
            else:
                return color_nodes(self.copy_source, {self.to_node}, self.color_reject)
        # even steps we are on a node
        elif step % 2 == 0:
            return color_nodes(self.copy_source, {self.to_node}, self.color_neutral)
        # odd steps we are on an edge
        else:
            self.from_node = self.to_node
            self.to_node = step_dfa(self.machine, self.from_node, self.user_input.value[step//2])
            return self.set_edge_display(self.from_node, self.to_node, self.user_input.value[step//2], self.to_node, self.color_neutral)


    def set_edge_display(self, src, dest, i, node, color):
        i = special[i] if i in special.keys() else i
        # color the node
        place = self.copy_source.find(']', self.copy_source.find('\t{} ['.format(node)))
        edge_display = self.copy_source[:place] + ' fontcolor="{}" fillcolor=white color="{}" style=filled penwidth=2'.format(color, color) + self.copy_source[place:]
        # color the edge
        label_start = -1
        if self.fuse:
            label_start = edge_display.find('=', edge_display.find('\t{} -> {}'.format(src, dest)))
        else:
            label_start = edge_display.find('=', edge_display.find('\t{} -> {} [label=< {}>'.format(src, dest, i)))
        label_end = edge_display.find(']', label_start)
        label = edge_display[label_start+1:label_end]
        replacement = label.replace(' {}'.format(i), '<font color="{}"> {}</font>'.format(color, i))
        edge_display = edge_display[:label_start+1] + replacement + ' color="{}" arrowsize=1.5 penwidth=2'.format(color) + edge_display[label_end:]

        return edge_display

    def generate_feed(self, step):
        input_string = self.user_input.value
        if step == 0:
            return write_feed_source('', '  ', replace_special(input_string), self.max_width)
        elif step == self.play_controls.max:
            return write_feed_source(replace_special(input_string), '  ', '', self.max_width)
        elif step % 2 == 0:
            return write_feed_source(replace_special(input_string[:step//2]),
                                     '  ',
                                     replace_special(input_string[step//2:]),
                                     self.max_width)
        else:
            return write_feed_source(replace_special(input_string[:step//2]),
                                     replace_special(input_string[step//2]),
                                     replace_special(input_string[step//2+1:]),
                                     self.max_width)
