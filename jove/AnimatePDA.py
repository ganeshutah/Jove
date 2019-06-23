from jove.DotBashers import *
from jove.Def_PDA import *
from jove.AnimationUtils import *

import ipywidgets as widgets
from ipywidgets import Layout
from IPython.display import display, clear_output, Javascript, HTML
from IPython.utils import io
from traitlets import Unicode, validate, List, observe, Instance
from graphviz import Source


class AnimatePDA:
    def __init__(self, m_desc, FuseEdges=False, max_stack=30, max_width=9.0):
        # Options
        self.color_accept = 'chartreuse3'
        self.color_reject = 'red'
        self.color_neutral = 'dodgerblue2'
        self.max_width = max_width
        self.fuse = FuseEdges
        # PDA specific options
        self.condition = 'ACCEPT_F'
        self.stack_size = 6
        # initialize
        self.valid_input = True
        self.machine = m_desc
        self.machine_obj = dotObj_pda(self.machine, FuseEdges=FuseEdges)
        self.copy_source = reformat_edge_labels(set_graph_size(self.machine_obj.source, max_width))
        
        # Set things we need for the animation
        self.machine_steps = []
        self.feed_steps = []
        self.stack_steps = []
        self.from_nodes = self.machine['q0']
        self.to_nodes = self.machine['q0']
        self.animated = False
        self.is_back_step = False
        
        # Setup the widgets
        # Top row for user input
        self.user_input = widgets.Text(value='',
                                       placeholder='Sigma: {{{}}}'.format(','.join(sorted(self.machine['Sigma']))),
                                       description='Input:',
                                       layout=Layout(width='500px')
                                       )
        self.user_input.observe(self.on_input_change, names='value')   
        self.alternate_start = widgets.Dropdown(options=sorted(self.machine['Q']),
                                                value=self.machine['q0'],
                                                description='Start State:',
                                                disabled=False,
                                                layout=Layout(width='200px')
                                                )
        self.generate_button = widgets.Button(description="Animate", 
                                              button_style='primary', 
                                              disabled=False
                                              )
        self.generate_button.on_click(self.generate_animation)
        self.acceptance_toggle = widgets.Dropdown(options=[('State', 'ACCEPT_F'), ('Stack', 'ACCEPT_S')],
                                                  description='Acceptance:',
                                                  disabled=False,
                                                  layout=Layout(width='160px')
                                                  )

        # Bottom row for player controls
        self.play_controls = widgets.Play(interval=950,
                                          value=0,
                                          min=0,
                                          max=100,
                                          step=1,
                                          description="Press play",
                                          disabled=True
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
            
        # set the widget to display the stack
        self.stack_display = widgets.Output()
        s_state = self.set_stack_display()
        with self.stack_display:
            display(Source(s_state))
        self.stack_size_slider = widgets.IntSlider(value=self.stack_size,
                                                   min=2,
                                                   max=max_stack,
                                                   step=1,
                                                   description='Stack Size:',
                                                   disabled=False,
                                                   continuous_update=False,
                                                   orientation='horizontal',
                                                   readout=True,
                                                   readout_format='d'
                                                   )
        self.stack_size_slider.observe(self.on_stack_size_change, names='value')
            
        # set the widget to display the feed
        self.feed_display = widgets.Output()
        f_state, inspecting = self.generate_feed('', 0, 0, [])
        with self.feed_display:
            display(Source(f_state))
        
        self.path_dropdown = widgets.Dropdown(options={},
                                              value=None,
                                              description='Path:',
                                              disabled=True,
                                              layout=Layout(width='200px')
                                              )
        self.path_dropdown.observe(self.on_path_change, names='value')

        # arrange the widgets in the display area
        row1 = widgets.HBox([self.user_input, self.acceptance_toggle, self.generate_button])
        row2 = widgets.HBox([self.stack_size_slider])
        ms_disp = widgets.HBox([self.stack_display, self.machine_display])
        play_row = widgets.HBox([self.path_dropdown, self.play_controls, self.backward, self.forward, self.speed_control])
        w = widgets.VBox([row1, row2, ms_disp, self.feed_display, play_row])
        display(w)
        
        self.play_controls.disabled = True
        self.forward.disabled = True
        self.backward.disabled = True
        self.speed_control.disabled = True

        
    def on_speed_change(self, change):
        self.play_controls.interval = 1000 - 50 * change['new']
        
        
    def on_stack_size_change(self, change):
        self.stack_size = change['new']
        with self.stack_display:
            clear_output(wait=True)
            display(Source(self.set_stack_display()))
    

    def on_input_change(self, change):
        # check for valid user input
        if not self.valid_user_input():
            self.generate_button.button_style = 'danger'
            self.generate_button.description = 'Invalid Input'
        else:
            self.generate_button.button_style = 'primary'
            self.generate_button.description = 'Animate'

            
    def on_path_change(self, change):
        self.play_controls._playing = False
        new_path = change['new']
        # make sure the there is an existing new path
        if new_path == None:
            return
        self.play_controls.max = new_path[0]
        self.machine_steps = new_path[1]
        self.stack_steps = new_path[2]
        self.feed_steps = new_path[3]
        self.play_controls.value = 0

        
    def on_backward_click(self, b):
        self.play_controls._playing = False    
        self.is_back_step = True
        self.play_controls.value -= 1
    
    
    def on_forward_click(self, b):
        self.play_controls._playing = False        
        self.play_controls.value += 1 
        

    def generate_animation(self, change):
        if self.animated:  # switching to input mode
            # enable the input controls
            self.play_controls._playing = False
            self.animated = False
            self.user_input.disabled = False
            self.alternate_start.disabled = False
            self.stack_size_slider.disabled = False
            self.acceptance_toggle.disabled = False
            # update the button to switch between modes
            self.generate_button.description='Animate'
            self.generate_button.button_style = 'primary'
            # disable the play controls
            self.play_controls.disabled = True
            self.forward.disabled = True
            self.backward.disabled = True
            self.speed_control.disabled = True
            self.path_dropdown.disabled = True
            self.path_dropdown.index = None
            # clean the machine display
            with self.machine_display:
                clear_output(wait=True)
                display(Source(self.copy_source))
            with self.stack_display:
                clear_output(wait=True)
                display(Source(self.set_stack_display()))
            with self.feed_display:
                clear_output(wait=True)
                display(Source(self.generate_feed('', 0, 0, [])[0]))

        else:  # switching to play mode
            # ignore invalid input
            if not self.valid_user_input():
                return
            # disable the input controls
            self.animated = True
            self.user_input.disabled = True
            self.alternate_start.disabled = True
            self.stack_size_slider.disabled = True
            self.acceptance_toggle.disabled = True
            self.generate_button.description='Change Input'
            # clean the current play displays
            self.feed_steps = []
            self.stack_steps = []
            self.machine_steps = []
            
            # find the acceptance paths
            a = ()
            paths = []
            touched = []
            with io.capture_output() as captured:
                a, paths, touched = run_pda(self.user_input.value, self.machine, acceptance=self.acceptance_toggle.value, STKMAX=self.stack_size);
            
            # if there are no acceptance paths we don't have any animations to build
            if len(paths) == 0:
                self.generate_button.button_style = 'danger'
                rejected_machine = set_graph_color(self.copy_source, self.color_reject)
                rejected_machine = set_graph_label(rejected_machine, "< <font color='{}'><b>'{}' was rejected</b></font>>".format(self.color_reject, self.user_input.value))
                with self.machine_display:
                    clear_output(wait=True)
                    display(Source(rejected_machine))
                return
            
            new_dropdown_options = {}          
            # generate all the display steps for each path
            path_count = 1
            for p in paths:
                path_states = p[1]
                max_steps = (len(path_states))*2+1
                path_states.append(p[0])
                
                # generate the feed display
                path_feed_steps = []
                inspecting = ''
                for step in range(max_steps):
                    feed_step, inspecting = self.generate_feed(inspecting, step, max_steps, path_states)
                    path_feed_steps.append(feed_step)
                    
                # generate the machine steps
                path_obj_steps = []
                for step in range(max_steps):
                    path_obj_steps.append(self.generate_machine_steps(path_states, step, max_steps))
                
                # generate the stack steps
                path_stack_steps = []
                for step in range(max_steps):
                    if step == max_steps:
                        path_stack_steps.append(self.set_stack_display(path_states[-1][2]))
                    else:
                        path_stack_steps.append(self.set_stack_display(path_states[step//2][2]))
                
                # add the path as an option in the dropdown
                new_dropdown_options['Path {}'.format(path_count)] = (max_steps-1, path_obj_steps, path_stack_steps, path_feed_steps)
                path_count += 1
                
            # update the dropdown
            self.path_dropdown.options = new_dropdown_options
            self.path_dropdown.index = 0
            # display the machine for this step
            with self.machine_display:
                clear_output(wait=True)
                display(Source(self.machine_steps[0]))
            # display the feed for this step
            with self.feed_display:
                clear_output(wait=True)
                display(Source(self.feed_steps[0]))
            # display the stack for this step
            with self.stack_display:
                clear_output(wait=True)
                display(Source(self.stack_steps[0]))
        
            # enable the controls
            self.backward.disabled = True
            if len(self.user_input.value) == 0:
                self.forward.disabled = True
            else:
                self.forward.disabled = False
            self.play_controls.disabled = False
            self.speed_control.disabled = False
            self.path_dropdown.disabled = False
            
    
    def valid_user_input(self):
        # make sure the input is valid
        for c in self.user_input.value:
            if c not in self.machine['Sigma']:
                return False
        return True


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
        # display the stack for this step
        with self.stack_display:
            clear_output(wait=True)
            display(Source(self.stack_steps[change['new']]))
                
    
    def generate_machine_steps(self, states, step, max_step):
        # on first step reset start node
        if step == 0:
            self.from_nodes = self.alternate_start.value
            self.to_nodes = self.from_nodes
            node_display = self.set_node_display(self.from_nodes, self.color_neutral)
            return node_display
            
        # on the last step check for acceptance type
        if step == max_step-1:
            if self.acceptance_toggle.value == 'ACCEPT_S':
                # color whole graph green
                return set_graph_color(self.copy_source, self.color_accept)
            else:
                # color just the final node green
                return self.set_node_display(states[-1][0], self.color_accept)
        
        # primary steps we are on a node
        elif step%2 == 0:
            self.from_nodes = states[step//2][0]
            node_display = self.set_node_display(self.from_nodes, self.color_neutral)
            return node_display
                       
        # secondary steps are choice steps
        else:
            inspecting = states[step//2][1]
            if len(inspecting) == 0:
                inspecting = ''
            else:
                inspecting = inspecting[0]
            self.to_nodes = step_pda((self.from_nodes, inspecting, states[step//2][2]),[],self.machine)
            return self.set_choice_display(step//2, self.copy_source, states[step//2][0], states[step//2+1][0], self.to_nodes, states, self.color_neutral)
            

    def set_node_display(self, node_set, color):
        node_display = self.copy_source
        for node in node_set:
            place = node_display.find(']', node_display.find('{} ['.format(node)))
            node_display =  node_display[:place] + ' fontcolor=white fillcolor={} style=filled'.format(color) + node_display[place:]
        return node_display
            
    
    def set_edge_display(self, m_state, src_node, state_set, states, color):
        node_set = set([s[0][0] for s in state_set])

        for n in node_set:
            # style the ending node
            place = m_state.find(']', m_state.find('{} ['.format(n)))
            m_state =  m_state[:place] + ' fontcolor={} fillcolor=white color={} style=filled penwidth=2'.format(color,color) + m_state[place:]
            # style the edge between node and n
            place = m_state.find(']', m_state.find('{} -> {} ['.format(src_node,n)))
            m_state = m_state[:place] + ' color={} fontcolor={} arrowsize=1.5 penwidth=2'.format(color,color) + m_state[place:]
        return m_state
    
    
    def set_choice_display(self, step, m_state, src_node, dest_node, state_set, states, color):
        ap = '&apos;&apos;'
        node_set = set([s[0][0] for s in state_set])
        for n in node_set:
            # determine the input part of the label (either front of input or '')
            inspecting = states[step][1]
            if len(inspecting) == 0:
                inspecting = ''
            else:
                inspecting = inspecting[0]
            stack = states[step][2]
            # determine the deltas between the src and n
            transitions = []
            future_stacks = []
            delta_keys = self.machine['Delta'].keys()
            for k in delta_keys:
                if k[0] == src_node and k[1] == inspecting and stack.startswith(k[2]):
                    results = self.machine['Delta'][k]
                    for r in results:
                        if r[0] == n:
                            popping = k[2]
                            pushing = r[1]
                            future_stacks.append(pushing + stack[len(popping):])
                            transitions.append(replace_special('{}, {} ; {}'.format(ap if inspecting == '' else inspecting, ap if popping == '' else popping, ap if pushing == '' else pushing)))
                            
                elif inspecting != '' and k[0] == src_node and k[1] == '' and stack.startswith(k[2]):
                    results = self.machine['Delta'][k]
                    for r in results:
                        if r[0] == n:
                            popping = k[2]
                            pushing = r[1]
                            future_stacks.append(pushing + stack[len(popping):])
                            transitions.append(replace_special('{}, {} ; {}'.format(ap, ap if popping == '' else popping, ap if pushing == '' else pushing)))
            
            # style the edge label    
            if self.fuse:
                label_start = m_state.find('=', m_state.find('{} -> {}'.format(src_node,n)))
                label_end = m_state.find(']', label_start)
                replacement = m_state[label_start+1:label_end]
                for t in transitions:
                    replacement = replacement.replace(' {}'.format(t),'<font color="{}"> {}</font>'.format(color,t))
                if n!= dest_node:
                    replacement += ' color={} arrowsize=1 penwidth=1 style=dashed'.format(color,color)
                else:
                    replacement += ' color={} arrowsize=1.5 penwidth=2'.format(color,color)
                m_state = m_state[:label_start+1] + replacement + m_state[label_end:]
            else:
                for t in range(len(transitions)):
                    label_start = m_state.find('=', m_state.find('{} -> {} [label=< {}>'.format(src_node,n,transitions[t])))
                    label_end = m_state.find(']', label_start)
                    label = m_state[label_start+1:label_end]
                    replacement = label.replace(' {}'.format(transitions[t]),'<font color="{}"> {}</font>'.format(color,transitions[t]))
                    if n!= dest_node or future_stacks[t] != states[step+1][2]:
                        replacement += ' color={} arrowsize=1 penwidth=1 style=dashed'.format(color,color)
                    else:
                        replacement += ' color={} arrowsize=1.5 penwidth=2'.format(color,color)
                    m_state = m_state[:label_start+1] + replacement + m_state[label_end:]
                      
            # style the ending node
            if n != dest_node:
                place = m_state.find(']', m_state.find('{} ['.format(n)))
                m_state =  m_state[:place] + ' fontcolor={} fillcolor=white color={} style=dashed penwidth=1'.format(color,color) + m_state[place:]
            else:
                place = m_state.find(']', m_state.find('{} ['.format(n)))
                m_state =  m_state[:place] + ' fontcolor={} color={} fillcolor=white style=filled penwidth=2'.format(color,color) + m_state[place:]
        return m_state
    

    def set_stack_display(self, contents=''):
        on_stack = len(contents)
        stack_string = 'digraph {{\n\tgraph [rankdir=LR size={}];\n\tnode [fontsize=12 width=0.35 shape=record];\n\tstack [label="'.format(self.max_width)
        # visible stack
        elements_string = ''
        if on_stack == 0:
            on_stack = 1
            elements_string += '<top> '
        else:
            for i in range(on_stack-1,-1,-1):
                elements_string = '{}|'.format(replace_special(contents[i])) + elements_string
                if i == 0:
                    elements_string = '<top> ' + elements_string
        for i in range(self.stack_size - on_stack):
                elements_string = ' |' + elements_string
        stack_string += elements_string[:-1] + '"]\n\tEmpty [width=0 penwidth=0 label="''"]\n\tEmpty -> stack:top\n}'
        return stack_string

    
    def generate_feed(self, inspecting, step, max_steps, states):
        input_string = self.user_input.value
        feed_string = 'digraph {{\n\tgraph [rankdir=LR];\n\tnode [fontsize=12 width=0.35 shape=plaintext];'.format(self.max_width)
        if step == 0:
            feed_string += '\n\tfeed [label=< <table border="0" cellborder="1" cellspacing="0" cellpadding="8"><tr><td></td><td width="16"></td><td>{}</td></tr></table>>];'.format(replace_special(input_string))
        elif step == max_steps:
            current_state = states[step//2]
            prev_state = states[step//2-1]
            if len(current_state[1]) != len(prev_state[1]):
                inspecting = ''
            endpoint = len(current_state[1])+len(inspecting)
            if endpoint == 0:
                feed_string += '\n\tfeed [label=< <table border="0" cellborder="1" cellspacing="0" cellpadding="8"><tr><td>{}</td><td width="16"></td><td></td></tr></table>>];'.format(replace_special(input_string))
            else:
                feed_string += '\n\tfeed [label=< <table border="0" cellborder="1" cellspacing="0" cellpadding="8"><tr><td>{}</td><td width="16">{}</td><td>{}</td></tr></table>>];'.format(replace_special(input_string[:-endpoint]),replace_special(inspecting),replace_special(current_state[1]))
        else:
            current_state = states[step//2]
            # at a node
            if step % 2 == 0:
                prev_state = states[step//2-1]
                if len(current_state[1]) != len(prev_state[1]):
                    inspecting = ''
                endpoint = len(current_state[1][len(inspecting):])+len(inspecting)
                if endpoint == 0:
                    feed_string += '\n\tfeed [label=< <table border="0" cellborder="1" cellspacing="0" cellpadding="8"><tr><td>{}</td><td width="16"></td><td></td></tr></table>>];'.format(replace_special(input_string))
                else:
                    feed_string += '\n\tfeed [label=< <table border="0" cellborder="1" cellspacing="0" cellpadding="8"><tr><td>{}</td><td width="16">{}</td><td>{}</td></tr></table>>];'.format(replace_special(input_string[:-endpoint]),replace_special(inspecting),replace_special(current_state[1][len(inspecting):]))
            # picking a path
            else:
                left = ''
                if len(current_state[1]) == 0:
                    inspecting = ''
                else:
                    inspecting = current_state[1][0]
                right = current_state[1][len(inspecting):]
                endpoint = len(right)+len(inspecting)
                if endpoint == 0:
                    feed_string += '\n\tfeed [label=< <table border="0" cellborder="1" cellspacing="0" cellpadding="8"><tr><td>{}</td><td width="16"></td><td></td></tr></table>>];'.format(replace_special(input_string))
                else:
                    feed_string += '\n\tfeed [label=< <table border="0" cellborder="1" cellspacing="0" cellpadding="8"><tr><td>{}</td><td width="16">{}</td><td>{}</td></tr></table>>];'.format(replace_special(input_string[:-endpoint]),replace_special(inspecting),replace_special(right))
        feed_string += '\n}'
        # return the feed step
        return feed_string, inspecting
