import os
import contextlib
from jove.AnimationUtils import *

with open(os.devnull, 'w') as devnull:
    with contextlib.redirect_stdout(devnull):
        from jove.DotBashers import *
        from jove.Def_TM import *

import ipywidgets as widgets
from ipywidgets import Layout
from IPython.display import display, clear_output, Javascript, HTML
from IPython.utils import io
from traitlets import Unicode, validate, List, observe, Instance
from graphviz import Source


class AnimateTM:
    '''
    This is the TM animation class.
    Call it with the TM to be animated, and also FuseEdges=True/False
    to draw the TM with edges either fused or not.
    For producing drawings in Colab, it is important to have these in
    every cell that calls animation.
    
    AnimateTM(myTM, FuseEdges='True/False')
    followed by
    display(HTML('<link rel="stylesheet" href="//stackpath.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css"/>'))

    Then the animation works in one's own install or Colab.
    '''
   
    def __init__(self, m_desc,
                 FuseEdges=False,
                 show_rejected=False,
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
        # TM specific option
        self.show_rejected = show_rejected
        
        # initialize
        self.valid_input = True
        self.machine = m_desc
        self.machine_obj = dotObj_tm(self.machine, FuseEdges=FuseEdges)
        self.copy_source = reformat_edge_labels(set_graph_size(self.machine_obj.source, max_width))
        
        # Set things we need for the animation
        self.machine_steps = []
        self.tape_steps = []
        self.from_nodes = self.machine['q0']
        self.to_nodes = self.machine['q0']
        self.animated = False
        self.is_back_step = False
        
        # Top row for user input
        self.user_input = widgets.Text(value='',
                                       placeholder='Sigma: {{{}}}'.format(','.join(sorted(self.machine['Sigma']))),
                                       description='Input:',
                                       layout=Layout(width='500px')
                                       )
        self.user_input.observe(self.on_input_change, names='value')
        self.generate_button = widgets.Button(description="Animate", 
                                              button_style='primary', 
                                              disabled=False
                                              )
        self.generate_button.on_click(self.generate_animation)
        self.start_fuel = widgets.BoundedIntText(value=10,
                                                 min=0,
                                                 max=1000,
                                                 step=1,
                                                 description='Fuel:',
                                                 layout=Layout(width='160px'),
                                                 disabled=False
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

            # set a widget to display rejected output
            self.rejection_display = widgets.Output()
            self.rejection_text = widgets.HTML(value="")
            self.reject_msg_start = '<p style="color:{}; text-align:center"><b>\'<span style="font-family:monospace">'.format(self.color_reject)
            self.reject_msg_end = '</span>\' was REJECTED</b></br>(Try running with more \'fuel\')</p>'
            
        # set the widget to display the tape
        self.tape_display = widgets.Output()
        with self.tape_display:
            display(Source(self.generate_tape('........', 0, '', 10)))

        self.path_dropdown = widgets.Dropdown(options={},
                                              value=None,
                                              description='',
                                              disabled=True,
                                              layout=Layout(width='200px')
                                              )
        self.path_dropdown.observe(self.on_path_change, names='value')

        # TODO: REMOVE TESTING CODE
        self.test_output = widgets.Output()

        # arrange the widgets in the display area
        row1 = widgets.HBox([self.user_input, self.start_fuel, self.generate_button]) # not displaying alternate start state
        ms_disp = widgets.HBox([self.machine_display])
        tp_disp = widgets.HBox([self.tape_display])
        play_row = widgets.HBox([self.path_dropdown, self.play_controls, self.backward, self.forward, self.speed_control])
        w = widgets.VBox([row1, self.rejection_display, ms_disp, tp_disp, play_row, self.test_output])
        display(w)
        
        self.play_controls.disabled = True
        self.forward.disabled = True
        self.backward.disabled = True
        self.speed_control.disabled = True

    def on_speed_change(self, change):
        self.play_controls.interval = 1000 - 50 * change['new']

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
        self.tape_steps = new_path[2]
        self.play_controls.value = 0
        
    def on_backward_click(self, b):
        self.play_controls._playing = False    
        self.is_back_step = True  
        self.play_controls.value -= 1
    
    def on_forward_click(self, b):
        self.play_controls._playing = False        
        self.play_controls.value += 1

    def generate_animation(self, change):
        # switching to input mode
        if self.animated:
            # enable the input controls
            self.play_controls._playing = False
            self.animated = False
            self.user_input.disabled = False
            self.start_fuel.disabled = False
            # update the button to switch between modes
            self.generate_button.description = 'Animate'
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
            with self.tape_display:
                clear_output(wait=True)
                display(Source(self.generate_tape('........', 0, '', 10)))
            with self.rejection_display:
                clear_output()
        
        # switching to play mode
        else:
            # ignore invalid input
            if not self.valid_user_input():
                return
            # disable the input controls
            self.animated = True
            self.user_input.disabled = True
            self.start_fuel.disabled = True
            self.generate_button.description = 'Change Input'
            # clean the current play displays
            self.tape_steps = []
            self.machine_steps = []
            
            # find the acceptance paths
            result = ()
            with io.capture_output() as captured:  # suppress run_tm print statements
                result = run_tm(self.machine, self.user_input.value, self.start_fuel.value)
            paths = result[1]
            
            new_dropdown_options = {}          
            # generate all the display steps for each path
            path_count = 0
            for p in paths:
                # check if this is a rejected path
                if not self.show_rejected and p[0][0] not in self.machine['F']:
                    continue
                    
                path_states = p[1].copy()
                max_steps = (len(path_states))*2+1
                path_states.append(p[0])
                
                # generate the feed display
                path_tape_steps = []
                inspecting = ''
                for step in range(max_steps):
                    tape_contents = path_states[step//2][2]
                    header_pos = path_states[step//2][1]
                    while len(tape_contents) <= header_pos:
                        tape_contents += '.'
                        
                    # make a header message
                    header_message = ''
                    if step == max_steps - 1:
                        header_message = 'STOP'
                    elif step % 2 == 0:
                        header_message = 'READ: {}'.format(tape_contents[header_pos])
                    else:
                        write_val = ''
                        move_dir = ''
                        destinations = self.machine['Delta'][(path_states[step//2][0],
                                                              '{}'.format(tape_contents[header_pos]))]
                        for d in destinations:
                            if d[0] == path_states[step//2+1][0]:
                                write_val = d[1]
                                move_val = d[2]
                                break
                        header_message = 'WRITE: {}'.format(write_val)
                        tape_contents = path_states[step//2+1][2]
                    fuel_amount = self.start_fuel.value - step//2
                    tape_step = self.generate_tape(tape_contents,
                                                   header_pos,
                                                   header_message,
                                                   fuel_amount if step != 0 else self.start_fuel.value)
                    path_tape_steps.append(tape_step)
                    
                # generate the machine steps
                path_obj_steps = []
                for step in range(max_steps):
                    path_obj_steps.append(self.generate_machine_steps(path_states, step, max_steps))
                
                # add the path as an option in the dropdown
                path_count += 1
                path_name = 'Path {}: {}'.format(path_count, 'Accepted' if p[0][0] in self.machine['F'] else 'Rejected')
                new_dropdown_options[path_name] = (max_steps-1, path_obj_steps, path_tape_steps)
                
            # if there are no paths we don't have any animations to build (this should never happen for TM)
            if path_count == 0:
                self.generate_button.button_style = 'danger'
                rejected_machine = set_graph_color(self.copy_source, self.color_reject)
                with self.rejection_display:
                    self.rejection_text.value = '{}{}{}'.format(self.reject_msg_start, self.user_input.value, self.reject_msg_end)
                    display(self.rejection_text)
                with self.machine_display:
                    clear_output(wait=True)
                    display(Source(rejected_machine))
                return
            
            # update the dropdown
            self.path_dropdown.options = new_dropdown_options
            self.path_dropdown.index = 0
            # display the machine for this step
            with self.machine_display:
                clear_output(wait=True)
                display(Source(self.machine_steps[0]))
            # display the feed for this step
            with self.tape_display:
                clear_output(wait=True)
                display(Source(self.tape_steps[0]))
        
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
        # display the tape for this step
        with self.tape_display:
            clear_output(wait=True)
            display(Source(self.tape_steps[change['new']]))
    
    def generate_machine_steps(self, states, step, max_step):
        # on first step reset start node
        if step == 0:
            self.from_nodes = self.machine['q0']
            self.to_nodes = self.from_nodes
            return color_nodes(self.copy_source, {self.from_nodes}, self.color_neutral)
            
        # on the last step check for acceptance type
        if step == max_step-1:
            final_node = states[-1][0]
            if final_node in self.machine['F']:  # accepted path (color node green)
                return color_nodes(self.copy_source, {final_node}, self.color_accept)
            else:  # rejected path (color node red)
                return color_nodes(self.copy_source, {final_node}, self.color_reject)
        
        # even steps we are on a node
        elif step % 2 == 0:
            from_node = states[step//2][0]
            return color_nodes(self.copy_source, {from_node}, self.color_neutral)
            
        # odd steps we are on an edge
        else:
            to_nodes = set()
            with io.capture_output() as captured:  # suppress run_tm print statements
                step_result = step_tm(self.machine, states[step//2], [], [])[0]
                for r in step_result:
                    to_nodes.add(r[0][0])
            tape_content = states[step//2][2]
            header_pos = states[step//2][1]
            while len(tape_content) <= header_pos:
                tape_content += '.'
            inspecting = tape_content[header_pos]
            return self.set_choice_display(step//2, states, self.copy_source, states[step//2][0], states[step//2+1][0], to_nodes, inspecting,self.color_neutral)

    def set_choice_display(self, step, states, m_state, src_node, dest_node, node_set, inspecting, color):
        inspecting_pos = states[step][1]
        current_tape = states[step][2]
        while inspecting_pos > len(current_tape):
            current_tape += '.'
            
        for n in node_set:
            # recreate the edge label
            transitions = []
            future_tapes = []            
            delta = self.machine['Delta'][(src_node, inspecting)]
            for d in delta:
                if d[0] == n:
                    transitions.append(replace_special('{} ; {},{}'.format(inspecting, d[1], d[2])))
                    future_tapes.append(current_tape[:inspecting_pos] + d[1] + current_tape[inspecting_pos+1:])
            
            # style the edge label           
            if self.fuse:
                label_start = m_state.find('=', m_state.find('\t{} -> {}'.format(src_node,n)))
                label_end = m_state.find(']', label_start)
                replacement = m_state[label_start+1:label_end]
                for t in transitions:
                    replacement = replacement.replace(' {}'.format(t), '<font color="{}"> {}</font>'.format(color, t))
                if n != dest_node:
                    replacement += ' color="{}" arrowsize=1 penwidth=1 style=dashed'.format(color)
                else:
                    replacement += ' color="{}" arrowsize=1.5 penwidth=2'.format(color)
                m_state = m_state[:label_start+1] + replacement + m_state[label_end:]
            else:
                for t in range(len(transitions)):
                    label_start = m_state.find('=', m_state.find('\t{} -> {} [label=< {}>'.format(src_node, n, transitions[t])))
                    label_end = m_state.find(']', label_start)
                    label = m_state[label_start+1:label_end]
                    replacement = label.replace(' {}'.format(transitions[t]),
                                                '<font color="{}"> {}</font>'.format(color, transitions[t]))
                    if n != dest_node or future_tapes[t] not in states[step+1][2]:
                        replacement += ' color="{}" arrowsize=1 penwidth=1 style=dashed'.format(color)
                    else:
                        replacement += ' color="{}" arrowsize=1.5 penwidth=2'.format(color)
                    m_state = m_state[:label_start+1] + replacement + m_state[label_end:]
                    
            # style the ending node
            if n != dest_node:
                # style the ending node
                place = m_state.find(']', m_state.find('{} ['.format(n)))
                m_state = m_state[:place] \
                          + ' fontcolor="{}" fillcolor=white color="{}" style=dashed penwidth=1'.format(color, color) \
                          + m_state[place:]
            else:
                # style the ending node
                place = m_state.find(']', m_state.find('{} ['.format(n)))
                m_state = m_state[:place] \
                          + ' fontcolor="{}" color="{}" fillcolor=white style=filled penwidth=2'.format(color, color) \
                          + m_state[place:]
        return m_state

    def generate_tape(self, tape_contents, head_loc, head_msg, fuel):
        # make the graph for the tape
        tape_length = len(tape_contents)
        tape_display = 'digraph {{\n\tgraph [rankdir=TB ranksep=0.0 size={}];'.format(self.max_width)
        tape_display += '\n\tnode [fontsize=12 width=0.4 shape=plaintext];'
        tape_display += '\n\ttape [label=< <table border="0" cellborder="1" cellspacing="0" cellpadding="8"><tr>'
        # write the tape
        tape_string = ''
        for i in range(tape_length):

            if i == head_loc:
                tape_string += '<td width="28" port="pos">'
            else:
                tape_string += '<td width="28">'
            tape_string += '{}</td>'.format(replace_special(tape_contents[i]))
        tape_display += tape_string + '</tr></table>>]'
        # draw the header
        tape_display += '\n\thead [shape=invhouse width=1.0 height=0.7 fixedsize=true label=< {}<br></br>Fuel: {}>]'.format(replace_special(head_msg),fuel)
        tape_display += '\n\thead -> tape:pos [arrowsize=0.8]\n}'
        return tape_display

print(''' "help(AnimateTM)" gives you info on how to use animations with TM ''')
