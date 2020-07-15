import sys
sys.path[0:0] = ['../..','../../3rdparty'] # Put these at the head of the search path

import os
import contextlib
import ast
import pprint
import time
import threading
from _io import StringIO
from contextlib import redirect_stdout

with open(os.devnull, 'w') as devnull:
    with contextlib.redirect_stdout(devnull):
        from jove.DotBashers     import *
        from jove.Def_md2mc      import *
        from jove.Def_DFA        import *
        from jove.AnimateDFA     import *
        from jove.Def_NFA        import *
        from jove.AnimateNFA     import *
        from jove.Def_PDA        import *
        from jove.AnimatePDA     import *
        from jove.Def_TM         import *
        from jove.AnimateTM      import *
        from jove.AnimationUtils import *
        from jove.Translate_JFlap import *

import ipywidgets as widgets
from ipywidgets import Layout
from ipywidgets import GridspecLayout
from IPython.display import display, clear_output, Javascript, HTML
from traitlets import Unicode, validate, List, observe, Instance

dfa_placeholder = '''
<from state> : <input symbol> -> <to state>  !! comment
ex: I : 0 -> A
'''
nfa_placeholder = '''
<from state> : <input symbol or ''> -> <to state>  !! comment
ex: I : 0 -> A
'''
pda_placeholder = '''
<from state> : <consume input symbol or ''> , <pop stack symbol or ''> ; <push stack symbol(s) or ''> -> <to state>  !! comment
ex: I : 0 , # ; 0# -> A
'''
tm_placeholder = '''
<from state> : <read from tape> ; <write to tape> , <head move (L,R,S)> -> <to state>  !! comment
ex: I : 0 ; B , R -> A
'''
translate_placeholder = '''
Load a JFlap (.jff) file using the 'Save/Load' menu.
The translated machine with be displayed here but any changes made to this machine will not be saved.
'''

translate_result_placeholder = '''
Translated rules with be displayed here.
These rules are used for animation and saving, so edit them and add comments.
'''

dfa_example = '''
!!---------------------------------------------------------------------------
!! This DFA looks for patterns of the form ..0101
!! i.e., ends in 0101.
!!---------------------------------------------------------------------------

I       : 0  -> S0      !! Go to S0, in anticipation of seeing a 0101
I       : 1  -> I       !! Seeing a 1 does not help, stay in I

S0      : 0  -> S0      !! Punt on 0, hoping that a 1 will come
S0      : 1  -> S01     !! Advance to state S01

S01     : 0  -> S010    !! A 0 advances to S010
S01     : 1  -> I       !! Seeing a 1 breaks the pattern, go back to I

S010    : 0  -> S0      !! A 0 breaks the pattern but may be the start of 0101
S010    : 1  -> F0101   !! Yay, we found 0101, and can accept the string if
                        !! there are no more symbols

F0101   : 0  -> S010    !! Another 0 makes ..01010, salvage the pattern from S010
F0101   : 1  -> I       !! Seeing a 1 breaks the pattern, go back to I
'''
nfa_example = '''
!!---------------------------------------------------------------------------
!! This NFA accepts strings in {0,1}* that contain patterns of the form ....1..
!! i.e., the third-last symbol (counting from the end) is a 1
!!---------------------------------------------------------------------------

I : 0 | 1 -> I  !! On input 0, stay in I.  On input 1, fork two paths. 
                !! One token stays in I (guess: NOT the "third-last 1"),
		        !! the other token goes to state A (guess: "third-last 1").
		
I : 1     -> A  !! Tokens that land in state A must enter the final state
A : 0 | 1 -> B  !! in two more steps, since a third step kills the token.
B : 0 | 1 -> F 
'''
pda_example = '''
!!---------------------------------------------------------------------------
!! This is a PDA that accepts all strings with twice as many b's as a's,
!! i.e. strings that satisfy n_b = 2 * n_a
!!
!! Note: Acceptance is by final state
!!---------------------------------------------------------------------------

I : '', # ; ''  -> Faccept  !! Accept the trivial case of an empty input

I : a, # ; cc#  -> I        !! Push 'cc#' to remember the two 'b's needed
I : a, b ; ''   -> Try      !! Push '' since 1 of 2 'b's matched
I : a, c ; ccc  -> I        !! Push 'ccc' for the two 'b's needed
       	   	   	        
I : b, # ; b#   -> I	    !! Push 'b#', now another 'b' and an 'a' needed
I : b, b ; bb   -> I        !! Push 'bb', waiting for matching 'a'
I : b, c ; ''   -> I        !! Push '', 'b' has matched half an 'a'
       	   	   	               	   	   	        
Try : '', b ; ''  -> I      !! Push '', 1 'a' matched 2 'b's, go back to I			
Try : '', c ; cc  -> I      !! Push 'cc', only half the 'a' was matched so 
                            !! remember the deficit			
Try : '', # ; c#  -> I      !! Push 'c#' only half the 'a' was matched so 
                            !! remember the deficit		
'''
tm_example = '''
!!---------------------------------------------------------------------------
!! This is a Turing Machine that accepts strings in {0,1}* that contain the
!! substring '101'
!!
!! Note: 'A', 'B', 'Q' and 'R' are useful to help visualize the Turing Machine's
!!       path's when looking for '101'
!!---------------------------------------------------------------------------

I : 0; A, R | 1; B, R -> I          !! Guess this position is NOT the start of '101'
                                    !! mark tape to indicate it is not part of a guess
I : 0; 0, S | 1; 1, S -> TryMyLuck  !! Guess this position IS the start of '101'

TryMyLuck : 1; Q, R -> Got1Sk0      !! Reading a 1 starts the pattern
Got1Sk0   : 0; P, R -> Got10Sk1     !! Reading a 0 advances the pattern
Got10Sk1  : 1; Q, R -> Found101     !! Reading a 1 completes the pattern

I : .; ., R -> Reject               !! Reached a blank space but did not find '101'
'''
translate_example = '''

'''

play_help_text = '''
You can enter a string for the machine to consume in the 'Input:' text box at the top of the widget. The string must be 
composed of symbols in the machine's alphabet which is displayed in input box by default. If the string contains unknown 
symbols the 'Animate' button will turn red with the message 'Invalid Input' until the string is updated. 
</br></br>
Click the 'Animate' button when you are ready for the machine to animate using your input. This disables the input 
textbox and enables the play controls at the bottom of the widget. When you are done exploring the current input click 
the 'Change Input' button to disable the play controls and re-enable the input textbox.
</br></br>
The play controls at the bottom of the widget (from left to right) consist of: </br>
<ul>
    <li><b>Play :</b> play/resume the animation</li>
    <li><b>Pause :</b> pause the animation</li>
    <li><b>Stop :</b> stop the animation, play will start from the beginning</li>
    <li><b>Loop :</b> loop when the end of the animation is reached and continue playing from the beginning</li>
    <li><b>Step Backward :</b> take one 'step' backward in the animation</li>
    <li><b>Step Forward :</b> take one 'step' forward in the animation</li>
    <li><b>Speed :</b> this slider lets you increase the animation playback speed</li>
</ul>
'''
animation_help_text = '''
<H4>General</H4>
You can enter a string for the machine to consume in the 'Input:' text box at the top of the widget. The string must be 
composed of symbols in the machine's alphabet which is displayed in input box by default. If the string contains 
unknown symbols the 'Animate' button will turn red with the message 'Invalid Input' until the string is updated.
</br></br>
Click the 'Animate' button when you are ready for the machine to animate using your input. This disables the input 
textbox and enables the play controls at the bottom of the widget. When you are done exploring the current input click 
the 'Change Input' button to disable the play controls and re-enable the input textbox.
</br>

<H4>Deterministic Finite Automata (DFA)</H4>
If the 'Alternate Start' option is selected, a dropdown box is added to the controls at the top of the widget that 
allows you to pick which state the DFA starts in when consuming the input.
</br>
<H4>Non-Deterministic Finite Automata (NFA)</H4>
If the 'Alternate Start' option is selected, a multiselect box is added to the controls at the top of the widget that 
allows you to pick which set of states the NFA starts in when consuming the input. Select multiple state names using 
<code>Ctrl + Click</code> (Windows) or <code>Shift + Click</code> (Mac).
</br>
<H4>Pushdown Automata (PDA)</H4>
This widget has two additional controls at the top. The 'Acceptance' dropdown lets you choose the acceptance 
criteria used when animating the PDA. 'State' will accept paths where the machine is in a final state when the input 
has been consumed. 'Stack' will accept paths where the stack is empty when the input has been consumed. Use the 'Stack 
Size' slider to changes the stack size used when looking for accepting paths.
</br></br>
The 'Path' dropdown box at the bottom of the widget will be populated with one option for each accepting path found for 
the provided input. If no accepting path is found the graph will highlight red and a message displays confirming the 
input was rejected.
</br>
<H4>Turing Machines (TM)</H4>
The 'Fuel' spinner box at the top of this widget can be used to increase the number of steps the machine is allowed to 
take while searching for an accepting path. This forces the machine to stop in a finite amount of time. 
</br></br>
The dropdown box at the bottom of the widget is populated with all accepting paths found for the provided input. If 
the 'Show Rejected' option is selected the dropdown will also include animations for the rejected paths that the TM 
searched.
'''
options_help_text = '''
There are three color pickers to let you control the colors used in the animations: </br>
<ul>
    <li><b>Acceptance:</b> Indicates the machine stopped in an accepting state</li>
    <li><b>Rejection:</b> Indicates the machine stopped in a rejecting state</li>
    <li><b>Transition:</b> This color is used to highlight the edges and nodes that are visited while the input string is 
    consumed</li>
</ul>
</br>
<b>Fuse Edges:</b> Controls whether edges between states are drawn individually. If selected, only one directed edge is 
drawn between state pairs and the transition labels are stacked above. This often helps simplify machine visualization. 
</br>
<b>Max Draw Size:</b> The maximum width of the animation widget in inches. The purpose of this control is to prevent 
large visualizations from extending outside the area that the animation widget can draw, which forces the area to become 
scrollable. 
</br>
<b>Alternate Start (DFA and NFA):</b> If selected, an additionaly control is added at the top of the animation that 
allows you to select the state (DFA) or set of states (NFA) that the machine starts in. For DFA the control is a 
dropdown box. For NFA the control is a multiselct box, select multiple state names using <code>Ctrl + Click</code> 
(Windows) or <code>Shift + Click</code> (Mac).
</br>
<b>Show Rejected (TM):</b> If selected, the path dropdown box will also include rejected paths that were explored by 
the TM.
</br>
<b>Max Stack Size (PDA):</b> Controls the maximum stack size that can be picked using the 'Stack Size' slider. The 
slider default value is always 6.
'''
machine_markdown_help_text = '''
<H4>General</H4>
The markdown for specifying a machine using Jove is similar for all machine types. You just need to write a series of
rules that define the transitions between the states in the machine. These rules all share the same base pattern: </br>
<code>&lt;From State&gt; : &lt;Transition Condition&gt; &minus;&gt; &lt;To State&gt;</code> </br>
With the additional constraints: </br>
<ul>
  <li>Initial state names must start with an <code>I</code> </li>
  <li>Final state names must start with a <code>F</code> </li>
  <li>States that are both initial and final must have a name that starts with <code>IF</code> </li>
  <li><code>!!</code> start a line comment, anything after the <code>!!</code> will be ignored by the parser </li>
  <li><code>''</code> stands for 'epsilon', a zero-length string and can be used in NFA and PDA as noted below </li>
</ul>
As an example, if we wanted to create a rule for a DFA that starts in initial state <code>I_start</code> and goes to 
final state <code>F_end</code> when a <code>0</code> is consumed the rule would be: </br>
<code>I_start : 0 &minus;&gt; F_end</code> </br>
If there is more than one transition condition between the same From and To states you can combine rules using a 
<code>&vert;</code> separated list of transitions. For two transitions the pattern is: </br>
<code>&lt;From State&gt; : &lt;Transition Condition 1&gt; &vert; &lt;Transition Condition 2&gt; &minus;&gt; &lt;To State&gt;</code> 
</br>
So, if we added a second rule that starts in initial state <code>I_start</code> and goes to final state 
<code>F_end</code> when a <code>1</code> is consumed &lpar;<code>I_start : 1 &minus;&gt; F_end</code>&rpar; then the 
combined rule would be: </br>
<code>I_start : 0 &vert; 1 &minus;&gt; F_end</code> </br>
<b>Note:</b> Whitespace in a line &lpar;space and tab&rpar; is ignored by the parser, so format your rules in a way 
that makes them easy to read and add plenty of comments </br>

<H4>Deterministic Finite Automata (DFA)</H4>
<code>&lt;from state&gt; : &lt;input symbol&gt; &minus;&gt; &lt;to state&gt;  !! comment </code></br>
ex: <code>I : 0 &minus;&gt; A</code> </br>

<H4>Non-Deterministic Finite Automata (NFA)</H4>
NFA can have <code>''</code> transitions in addition to transitions that consume input symbols. 
<code>&lt;from state&gt; : &lt;input symbol or ''&gt; &minus;&gt; &lt;to state&gt;  !! comment</code> </br>
ex: <code>I : 0 &minus;&gt; A</code> </br>
NFA are the only machine type in Jove that can have multiple initial states, remember that each of the initial state 
names must start with an <code>I</code>. </br>

<H4>Pushdown Automata (PDA)</H4>
PDA transitions have three parts:
<ol>
  <li>Input symbol to consume</li>
  <li>Symbol popped from the stack</li>
  <li>Symbol&lpar;s&rpar; to push onto the stack</li>  
</ol>
By default, PDA have a <code>#</code> marker at the bottom of the stack so that it is easy to check if the stack is 
empty. You are not <i>required</i> to replace the <code>#</code> marker when it is popped off the stack but it is best 
practice to make sure it is always on the stack. </br>
PDA can have <code>''</code> transitions that: do not consume an input symbol, do not pop from the stack, do not push 
to the stack, or any combination of the the three.
<code>&lt;from state&gt; : &lt;consume input symbol or ''&gt; , &lt;pop stack symbol or ''&gt; ; &lt;push stack symbol&lpar;s&rpar; or ''&gt; &minus;&gt; &lt;to state&gt;  !! comment</code> </br>
ex: <code>I : 0 , # ; 0# &minus;&gt; A</code> </br>

<H4>Turing Machines (TM)</H4>
Turing Machine transitions have three parts:
<ol>
  <li>Symbol to read from the tape</li>
  <li>Symbol to write on the tape</li>
  <li>Head movement &lpar;L - move left, R - move right, S - stay put&rpar;</li>  
</ol>
Jove Turing Machines use <code>.</code> to denote a blank position on the tape and all positions to the left and right 
of the initial input contain <code>.</code>. </br>
<code>&lt;from state&gt; : &ltread from tape&gt; ; &lt;write to tape&gt; , &lt;head move &lpar;L,R,S&rpar;&gt; &minus;&gt; &lt;to state&gt;  !! comment</code> </br>
ex: <code>I : 0 ; B , R &minus;&gt; A</code> </br>
'''

translate_help_text = '''
You can translate JFlap files to Jove machines using this Jove Editor.
<ul>
  <li><b>Load a JFlap file</b> - Open the 'Save/Load' menu and click 'Load'. Use the file dialog to select a JFlap 
  file with the '.jff' extension. When the file is loaded the text over the two textareas will indicate the machine type 
  of the translated machine. The translated machine will be displayed in the left textarea and the translated rules 
  will be displayed in the right textarea. The required prefixes for initial and final state names are automatically 
  added.</li>
  <li><b>Edit</b> - If you want to make changes to the machine, make your edits to the rules and add comments in the 
  right textarea.</li>
  <li><b>Animate</b> - Switch to the 'Animate' tab to see the animation for the translated machine. Any edits made in 
  the right textarea will also be part of the animation.</li>
  <li><b>Save</b> - Save your translated machine using the 'Save/Load' menu. The changes and comments made in the 
  right textarea will be saved.</li>
</ul>
<p><b><em>Note:</em></b> Jove Editor does not force JFlap state names to conform to Jove Markdown, so initial and 
final states may break the Jove Markdown convention. Animations should still work on these machines.</p>
'''

class JoveEditor:
    def __init__(self, machine=None, examples=False):
        # added to force using font-family monospace for user input Textarea and Text widgets
        display(HTML("<style>textarea, input { font-family: monospace; }</style>"))
        # Editing textboxes and toggle buttons
        text_area_sytle = Layout(width='100%', height='500px')
        self.dfa_editor = widgets.Textarea(value=dfa_example.strip() if examples else '',
                                           placeholder=dfa_placeholder.strip(),
                                           disabled=False,
                                           layout=text_area_sytle
                                           )
        self.nfa_editor = widgets.Textarea(value=nfa_example.strip() if examples else '',
                                           placeholder=nfa_placeholder.strip(),
                                           disabled=False,
                                           layout=text_area_sytle
                                           )
        self.pda_editor = widgets.Textarea(value=pda_example.strip() if examples else '',
                                           placeholder=pda_placeholder.strip(),
                                           disabled=False,
                                           layout=text_area_sytle
                                           )
        self.tm_editor = widgets.Textarea(value=tm_example.strip() if examples else '',
                                          placeholder=tm_placeholder.strip(),
                                          disabled=False,
                                          layout=text_area_sytle
                                          )
        self.translated_to_label = widgets.HTML(value='<p style="font-family:monospace;font-size:16px;text-align:center">Nothing translated yet</p>')
        self.translate_editor = widgets.Textarea(value='',
                                                 placeholder=translate_placeholder.strip(),
                                                 disabled=False,
                                                 layout=text_area_sytle
                                                 )
        self.translate_result = widgets.Textarea(value='',
                                                 placeholder=translate_result_placeholder.strip(),
                                                 disabled=False,
                                                 layout=text_area_sytle
                                                 )
        self.translate_contents = widgets.VBox([self.translated_to_label,
                                                widgets.HBox([self.translate_editor, self.translate_result])
                                                ])
        self.pre_translate_machine = {}
        self.pre_translate_mtype = ''
        self.machine_toggle = widgets.ToggleButtons(options=['DFA', 'NFA', 'PDA', 'TM', 'Translate'],
                                                    value='DFA',
                                                    description='',
                                                    disabled=False,
                                                    style={'button_width': '120px'},
                                                    button_style='info',
                                                    tooltips=['Deterministic Finite Automata',
                                                              'Non-deterministic Finite Automata',
                                                              'Pushdown Automata',
                                                              'Turing Machine',
                                                              'Translation']
                                                    )
        self.machine_toggle.observe(self.on_machine_select, names='value')

        self.text_editor_display = widgets.Output()
        with self.text_editor_display:
            display(self.dfa_editor)

        # save and upload
        self.save_name_text = widgets.Text(value='',
                                           placeholder='filename',
                                           disabled=False)
        self.save_name_text.observe(self.save_text_changed, names='value')
        self.postfix_text = widgets.HTML(value='<p style="font-family:monospace">.dfa</p>')
        self.save_button = widgets.Button(description="Save",
                                          button_style='info',
                                          disabled=True,
                                          icon='download')
        self.save_button.on_click(self.save_machine)
        self.save_load_messages = widgets.HTML(value='<p style="font-size:small"></br></br></p>')
        self.upload_button = widgets.FileUpload(accept='.txt,.jff,.dfa,.nfa,.pda,.tm',
                                                button_style='info',
                                                description='Load',
                                                disabled=False)
        self.upload_button.observe(self.on_file_upload, names='value')

        self.save_load_collapse = widgets.Accordion(children=[widgets.VBox([widgets.HBox([self.save_name_text,
                                                                                          self.postfix_text]),
                                                                            self.save_button,
                                                                            self.save_load_messages,
                                                                            self.upload_button])],
                                                    selected_index=None)
        self.save_load_collapse.set_title(0, 'Save/Load')

        # Options Controls
        self.max_draw_size = widgets.BoundedFloatText(value=9.5,
                                                      min=1.0,
                                                      max=1000.0,
                                                      step=0.1,
                                                      description='Max Draw Size',
                                                      disabled=False,
                                                      style={'description_width': 'initial'},
                                                      layout=Layout(width='200px')
                                                      )
        self.fuse_option = widgets.ToggleButton(value=True,
                                                description='Fuse Edges',
                                                disabled=False,
                                                button_style='info',
                                                tooltip='Fuse machine edges',
                                                )
        self.alt_start_option = widgets.ToggleButton(value=False,
                                                     description='Alternate Start',
                                                     disabled=False,
                                                     button_style='info',
                                                     tooltip='Pick the starting state (DFA and NFA only)',
                                                     )
        self.show_reject_option = widgets.ToggleButton(value=False,
                                                       description='Show Rejected',
                                                       disabled=False,
                                                       button_style='info',
                                                       tooltip='Show rejected paths (TM only)',
                                                       )
        self.max_stack_size = widgets.BoundedIntText(value=30,
                                                     min=0,
                                                     max=1000,
                                                     step=1,
                                                     description='Max Stack Size',
                                                     disabled=False,
                                                     style={'description_width': 'initial'},
                                                     layout=Layout(width='200px')
                                                     )

        # color pickers
        self.accept_colorpicker = widgets.ColorPicker(concise=True,
                                                      description='Acceptance',
                                                      value='#66cd00',
                                                      disabled=False,
                                                      style={'description_width': 'initial'}
                                                      )
        self.reject_colorpicker = widgets.ColorPicker(concise=True,
                                                      description='Rejection',
                                                      value='#ff0000',
                                                      disabled=False,
                                                      style={'description_width': 'initial'}
                                                      )
        self.transit_colorpicker = widgets.ColorPicker(concise=True,
                                                       description='Transition',
                                                       value='#1c86ee',
                                                       disabled=False,
                                                       style={'description_width': 'initial'}
                                                       )
        self.colors = widgets.HBox([self.accept_colorpicker, self.reject_colorpicker, self.transit_colorpicker])
        options_layout = GridspecLayout(4, 3, grid_gap='5px', overflow='scroll hidden')
        options_layout[0, 0] = widgets.Label(value='Animation Colors:')
        options_layout[1, 0] = self.accept_colorpicker
        options_layout[2, 0] = self.reject_colorpicker
        options_layout[3, 0] = self.transit_colorpicker
        options_layout[0, 1] = self.fuse_option
        options_layout[1, 1] = self.max_draw_size
        options_layout[2, 1] = widgets.Label(value='Finite Automata:')
        options_layout[3, 1] = self.alt_start_option
        options_layout[0, 2] = widgets.Label(value='Turing Machine:')
        options_layout[1, 2] = self.show_reject_option
        options_layout[2, 2] = widgets.Label(value='Pushdown Automata:')
        options_layout[3, 2] = self.max_stack_size
        accordion = widgets.Accordion(children=[options_layout],
                                      layout=Layout(overflow='hidden'),
                                      selected_index=None)
        accordion.set_title(0, 'Options')

        # Pack the text editor and options into a VBOX
        self.edit_tab = widgets.VBox([widgets.HBox([self.save_load_collapse, self.machine_toggle],
                                                   layout=Layout(width='100%', align_content='center')),
                                     self.text_editor_display,
                                     accordion])

        # Animated Machine
        self.animated_machine_display = widgets.Output()
        self.machine_failure_display = widgets.Output()
        self.machine_messages_display = widgets.Output()
        self.generating_message = '<p style="font-family:monospace;font-size:24px;text-align:center">Generating animation widget ...'
        self.machine_messages_text = widgets.HTML(value=self.generating_message + ' </p>')
        self.machine_tab = widgets.VBox([self.machine_messages_display,
                                         self.animated_machine_display,
                                         self.machine_failure_display])

        # Help Tab
        help_tab_label = widgets.HTML(value='<H2>Help</H2>')
        markdown_help = widgets.HTML(value=machine_markdown_help_text.strip())
        options_help = widgets.HTML(value=options_help_text.strip())
        animation_help = widgets.HTML(value=animation_help_text.strip())
        play_help = widgets.HTML(value=play_help_text.strip())
        translate_help = widgets.HTML(value=translate_help_text.strip())
        help_topics = widgets.Accordion(children=[markdown_help,
                                                  options_help,
                                                  animation_help,
                                                  play_help,
                                                  translate_help],
                                        selected_index=None)
        help_topics.set_title(0, 'Machine Markdown')
        help_topics.set_title(1, 'Options')
        help_topics.set_title(2, 'Animations')
        help_topics.set_title(3, 'Play Controls')
        help_topics.set_title(4, 'Translation from JFlap')
        help_tab = widgets.VBox([help_tab_label, help_topics])

        # Pack the Tabs
        self.editor_tabs = widgets.Tab(children=[self.edit_tab, self.machine_tab, help_tab])
        self.editor_tabs.set_title(0, 'Edit')
        self.editor_tabs.set_title(1, 'Animate')
        self.editor_tabs.set_title(2, 'Help')
        self.editor_tabs.observe(self.on_tab_switch, names='selected_index')

        # If a machine was passed in handle differently
        if machine is not None:
            editor_string = '{}'.format(pprint.pformat(machine))
            if {'Q', 'Sigma', 'Delta', 'q0', 'F'} == machine.keys():
                self.dfa_editor.value = editor_string
                self.machine_toggle.value = 'DFA'
                self.editor_tabs.selected_index = 1
            elif {'Q', 'Sigma', 'Delta', 'Q0', 'F'} == machine.keys():
                self.nfa_editor.value = editor_string
                self.machine_toggle.value = 'NFA'
                self.editor_tabs.selected_index = 1
            elif {'Q', 'Sigma', 'Gamma', 'Delta', 'q0', 'z0', 'F'} == machine.keys():
                self.pda_editor.value = editor_string
                self.machine_toggle.value = 'PDA'
                self.editor_tabs.selected_index = 1
            elif {'Q', 'Sigma', 'Gamma', 'Delta', 'q0', 'B', 'F'} == machine.keys():
                self.tm_editor.value = editor_string
                self.machine_toggle.value = 'TM'
                self.editor_tabs.selected_index = 1
            else:
                self.translate_editor.value = '!! The provided dictionary does not match any known Jove machine type\n{}'.format(editor_string)
                self.machine_toggle.value = 'Translate'
                self.editor_tabs.selected_index = 0

        display(self.editor_tabs)

    def on_machine_select(self, change):
        # save button
        if self.save_name_text.value == "":
            self.save_button.disabled = True
        else:
            self.save_button.disabled = False

        # display the correct editor and file extension
        with self.text_editor_display:
            clear_output(wait=True)
            if change['new'] is 'DFA':
                display(self.dfa_editor)
                self.postfix_text.value = '<p style="font-family:monospace">.dfa</p>'
            elif change['new'] is 'NFA':
                display(self.nfa_editor)
                self.postfix_text.value = '<p style="font-family:monospace">.nfa</p>'
            elif change['new'] is 'PDA':
                display(self.pda_editor)
                self.postfix_text.value = '<p style="font-family:monospace">.pda</p>'
            elif change['new'] is 'TM':
                display(self.tm_editor)
                self.postfix_text.value = '<p style="font-family:monospace">.tm </p>'
            elif change['new'] is 'Translate':
                display(self.translate_contents)
                if self.pre_translate_mtype == 'DFA':
                    self.postfix_text.value = '<p style="font-family:monospace">.dfa</p>'
                elif self.pre_translate_mtype == 'NFA':
                    self.postfix_text.value = '<p style="font-family:monospace">.nfa</p>'
                elif self.pre_translate_mtype == 'PDA':
                    self.postfix_text.value = '<p style="font-family:monospace">.pda</p>'
                elif self.pre_translate_mtype == 'TM':
                    self.postfix_text.value = '<p style="font-family:monospace">.tm</p>'

    def on_tab_switch(self, change):
        # Clean up any previous messages
        with self.machine_messages_display:
            clear_output()
        with self.machine_failure_display:
            clear_output()

        if self.editor_tabs.get_title(change['new']) is 'Animate':
            with self.machine_messages_display:
                display(self.machine_messages_text)

            # Clear the last displayed machine
            with self.animated_machine_display:
                clear_output()

            # Generate the machine and display it's animator
            jove_error = StringIO()
            machine = None
            if self.machine_toggle.value is 'DFA':
                if len(self.dfa_editor.value.strip()) == 0:
                    self.display_animate_error('DFA', 'No machine description in editor')
                    return
                check_for_dict = self.dfa_editor.value.strip()
                if check_for_dict[0] is '{' and check_for_dict[-1] is '}':
                    try:
                        machine = ast.literal_eval(check_for_dict)
                        if {'Q', 'Sigma', 'Delta', 'q0', 'F'} != machine.keys():
                            self.display_animate_error('DFA', 'Badly formed machine description in editor')
                            return
                    except Exception as e:
                        self.display_animate_error('DFA', str(e))
                        return
                else:
                    try:
                        with redirect_stdout(jove_error):
                            machine = md2mc('DFA\n{}'.format(self.dfa_editor.value))
                    except Exception as e:
                        message = 'Jove error message:\n{}\n\nPython error message: {}'.format(jove_error.getvalue(), str(e))
                        self.display_animate_error('DFA', message)
                        return
                with self.animated_machine_display:
                    display(AnimateDFA(machine,
                                       FuseEdges=self.fuse_option.value,
                                       pick_start=self.alt_start_option.value,
                                       max_width=self.max_draw_size.value,
                                       accept_color=self.accept_colorpicker.value,
                                       reject_color=self.reject_colorpicker.value,
                                       neutral_color=self.transit_colorpicker.value))

            elif self.machine_toggle.value is 'NFA':
                if len(self.nfa_editor.value.strip()) == 0:
                    self.display_animate_error('NFA', 'No machine description in editor')
                    return
                check_for_dict = self.nfa_editor.value.strip()
                if check_for_dict[0] is '{' and check_for_dict[-1] is '}':
                    try:
                        machine = ast.literal_eval(check_for_dict)
                        if {'Q', 'Sigma', 'Delta', 'Q0', 'F'} != machine.keys():
                            self.display_animate_error('NFA', 'Badly formed machine description in editor')
                            return
                    except Exception as e:
                        self.display_animate_error('NFA', str(e))
                        return
                else:
                    try:
                        with redirect_stdout(jove_error):
                            machine = md2mc('NFA\n{}'.format(self.nfa_editor.value))
                    except Exception as e:
                        message = 'Jove error message:\n{}\n\nPython error message: {}'.format(jove_error.getvalue(), str(e))
                        self.display_animate_error('NFA', message)
                        return
                with self.animated_machine_display:
                    display(AnimateNFA(machine,
                                       FuseEdges=self.fuse_option.value,
                                       pick_start=self.alt_start_option.value,
                                       max_width=self.max_draw_size.value,
                                       accept_color=self.accept_colorpicker.value,
                                       reject_color=self.reject_colorpicker.value,
                                       neutral_color=self.transit_colorpicker.value
                                       ))
            elif self.machine_toggle.value is 'PDA':
                if len(self.pda_editor.value.strip()) == 0:
                    self.display_animate_error('PDA', 'No machine description in editor')
                    return
                check_for_dict = self.pda_editor.value.strip()
                if check_for_dict[0] is '{' and check_for_dict[-1] is '}':
                    try:
                        machine = ast.literal_eval(check_for_dict)
                        if {'Q', 'Sigma', 'Gamma', 'Delta', 'q0', 'z0', 'F'} != machine.keys():
                            self.display_animate_error('PDA', 'Badly formed machine description in editor')
                            return
                    except Exception as e:
                        self.display_animate_error('PDA', str(e))
                        return
                else:
                    try:
                        with redirect_stdout(jove_error):
                            machine = md2mc('PDA\n{}'.format(self.pda_editor.value))
                    except Exception as e:
                        message = 'Jove error message:\n{}\n\nPython error message: {}'.format(jove_error.getvalue(), str(e))
                        self.display_animate_error('PDA', message)
                        return
                with self.animated_machine_display:
                    display(AnimatePDA(machine,
                                       FuseEdges=self.fuse_option.value,
                                       max_stack=self.max_stack_size.value,
                                       max_width=self.max_draw_size.value,
                                       accept_color=self.accept_colorpicker.value,
                                       reject_color=self.reject_colorpicker.value,
                                       neutral_color=self.transit_colorpicker.value
                                       ))
            elif self.machine_toggle.value is 'TM':
                if len(self.tm_editor.value.strip()) == 0:
                    self.display_animate_error('TM', 'No machine description in editor')
                    return
                check_for_dict = self.tm_editor.value.strip()
                if check_for_dict[0] is '{' and check_for_dict[-1] is '}':
                    try:
                        machine = ast.literal_eval(check_for_dict)
                        if {'Q', 'Sigma', 'Gamma', 'Delta', 'q0', 'B', 'F'} != machine.keys():
                            self.display_animate_error('TM', 'Badly formed machine description in editor')
                    except Exception as e:
                        self.display_animate_error('TM', str(e))
                        return
                else:
                    try:
                        with redirect_stdout(jove_error):
                            machine = md2mc('TM\n{}'.format(self.tm_editor.value))
                    except Exception as e:
                        message = 'Jove error message:\n{}\n\nPython error message: {}'.format(jove_error.getvalue(), str(e))
                        self.display_animate_error('TM', message)
                        return
                with self.animated_machine_display:
                    display(AnimateTM(machine,
                                      FuseEdges=self.fuse_option.value,
                                      show_rejected=self.show_reject_option.value,
                                      max_width=self.max_draw_size.value,
                                      accept_color=self.accept_colorpicker.value,
                                      reject_color=self.reject_colorpicker.value,
                                      neutral_color=self.transit_colorpicker.value
                                      ))
            # Translation is not implemented yet
            elif self.machine_toggle.value is 'Translate':
                if self.pre_translate_mtype == 'UNKNOWN':
                    self.display_animate_error('Translation', 'Could not translate the JFlap to a recognized machine type')
                elif self.pre_translate_mtype == 'DFA':
                    try:
                        with redirect_stdout(jove_error):
                            machine = md2mc('DFA\n{}'.format(self.translate_result.value))
                    except Exception as e:
                        message = 'Jove error message:\n{}\n\nPython error message: {}'.format(jove_error.getvalue(), str(e))
                        self.display_animate_error('DFA', message)
                        return
                    with self.animated_machine_display:
                        display(AnimateDFA(machine,
                                           FuseEdges=self.fuse_option.value,
                                           pick_start=self.alt_start_option.value,
                                           max_width=self.max_draw_size.value,
                                           accept_color=self.accept_colorpicker.value,
                                           reject_color=self.reject_colorpicker.value,
                                           neutral_color=self.transit_colorpicker.value))
                elif self.pre_translate_mtype == 'NFA':
                    try:
                        with redirect_stdout(jove_error):
                            machine = md2mc('NFA\n{}'.format(self.translate_result.value))
                    except Exception as e:
                        message = 'Jove error message:\n{}\n\nPython error message: {}'.format(jove_error.getvalue(), str(e))
                        self.display_animate_error('NFA', message)
                        return
                    with self.animated_machine_display:
                        display(AnimateNFA(machine,
                                           FuseEdges=self.fuse_option.value,
                                           pick_start=self.alt_start_option.value,
                                           max_width=self.max_draw_size.value,
                                           accept_color=self.accept_colorpicker.value,
                                           reject_color=self.reject_colorpicker.value,
                                           neutral_color=self.transit_colorpicker.value
                                           ))
                elif self.pre_translate_mtype == 'PDA':
                    try:
                        with redirect_stdout(jove_error):
                            machine = md2mc('PDA\n{}'.format(self.translate_result.value))
                    except Exception as e:
                        message = 'Jove error message:\n{}\n\nPython error message: {}'.format(jove_error.getvalue(), str(e))
                        self.display_animate_error('PDA', message)
                        return
                    with self.animated_machine_display:
                        display(AnimatePDA(machine,
                                           FuseEdges=self.fuse_option.value,
                                           max_stack=self.max_stack_size.value,
                                           max_width=self.max_draw_size.value,
                                           accept_color=self.accept_colorpicker.value,
                                           reject_color=self.reject_colorpicker.value,
                                           neutral_color=self.transit_colorpicker.value
                                           ))
                elif self.pre_translate_mtype == 'TM':
                    try:
                        with redirect_stdout(jove_error):
                            machine = md2mc('TM\n{}'.format(self.translate_result.value))
                    except Exception as e:
                        message = 'Jove error message:\n{}\n\nPython error message: {}'.format(jove_error.getvalue(), str(e))
                        self.display_animate_error('TM', message)
                        return
                    with self.animated_machine_display:
                        display(AnimateTM(machine,
                                          FuseEdges=self.fuse_option.value,
                                          show_rejected=self.show_reject_option.value,
                                          max_width=self.max_draw_size.value,
                                          accept_color=self.accept_colorpicker.value,
                                          reject_color=self.reject_colorpicker.value,
                                          neutral_color=self.transit_colorpicker.value
                                          ))

            with self.machine_messages_display:
                clear_output()

        elif self.editor_tabs.get_title(change['new']) is 'Edit':
            with self.animated_machine_display:
                clear_output()
            with self.machine_failure_display:
                clear_output()
            with self.machine_messages_display:
                clear_output()

    def start_generating_message(self):
        self.machine_messages_text.value = '{} ...</p>'.format(self.generating_message)
        for i in range(100):
            time.sleep(0.2)
            message = '{} {}</p>'.format(self.generating_message, '.'*(i%4))
            self.machine_messages_text.value = message
        self.generating_message = '{} ... I may be stuck</p>'.format(self.generating_message)

    def display_animate_error(self, machine_type, message):
        with self.machine_failure_display:
            clear_output()
            error_text = 'Error while generating the {}:\n\n{}'.format(machine_type, message)
            print(error_text)

    def save_text_changed(self, changed):
        if changed['new'] == '':
            self.save_button.disabled = True
        else:
            self.save_button.disabled = False
        self.save_load_messages.value = '<p style="font-size:small"></br></br></p>'

    def save_machine(self, b):
        # Disable save and load buttons
        self.save_button.disabled = True
        self.upload_button.disabled = True
        self.save_name_text.disabled = True
        self.save_load_messages.value = '<p style="font-size:small">saving ...</br></br></p>'

        # Get the filepath
        filepath = self.save_name_text.value
        filepath = filepath.split('.')[0]
        self.save_name_text.value = filepath
        if self.machine_toggle.value is 'DFA' or \
                (self.machine_toggle.value is 'Translate' and self.pre_translate_mtype == 'DFA'):
            filepath = '{}.dfa'.format(filepath)
        if self.machine_toggle.value is 'NFA' or \
                (self.machine_toggle.value is 'Translate' and self.pre_translate_mtype == 'NFA'):
            filepath = '{}.nfa'.format(filepath)
        if self.machine_toggle.value is 'PDA' or \
                (self.machine_toggle.value is 'Translate' and self.pre_translate_mtype == 'PDA'):
            filepath = '{}.pda'.format(filepath)
        if self.machine_toggle.value is 'TM' or \
                (self.machine_toggle.value is 'Translate' and self.pre_translate_mtype == 'TM'):
            filepath = '{}.tm'.format(filepath)

        file_contents = ''
        if self.machine_toggle.value is 'DFA':
            file_contents = 'DFA\n{}'.format(self.dfa_editor.value)
        if self.machine_toggle.value is 'NFA':
            file_contents = 'NFA\n{}'.format(self.nfa_editor.value)
        if self.machine_toggle.value is 'PDA':
            file_contents = 'PDA\n{}'.format(self.pda_editor.value)
        if self.machine_toggle.value is 'TM':
            file_contents = 'TM\n{}'.format(self.tm_editor.value)
        if self.machine_toggle.value is 'Translate':
            file_contents = f'{self.pre_translate_mtype}\n{self.translate_result.value}'

        try:
            with open(filepath, 'w') as filewriter:
                filewriter.writelines(file_contents)
        except Exception as e:
            error_message = '<p style="font-size:small; color:red">saving ... failed</br>'
            error_message += '{}</p>'.format(str(e))
            self.save_load_messages.value = error_message
            self.save_button.disabled = False
            self.upload_button.disabled = False
            self.save_name_text.disabled = False
            return

        self.save_load_messages.value = '<p style="font-size:small">saving ... success</br></br></p>'
        self.save_button.disabled = False
        self.upload_button.disabled = False
        self.save_name_text.disabled = False

    def on_file_upload(self, change):
        self.save_load_messages.value = '<p style="font-size:small"></br>loading ...</p>'
        file_contents = self.upload_button.value
        file_name = file_contents[list(file_contents.keys())[0]]['metadata']['name']
        machine_binary = file_contents[list(file_contents.keys())[0]]['content']
        machine_string = machine_binary.decode().strip()
        machine_string_list = machine_string.splitlines()
        machine_string = '\n'.join(machine_string_list)

        # check for jflap first
        if machine_string.strip().startswith('<?xml version="1.0"'):
            self.machine_toggle.value = 'Translate'
            mtype, machine, error_msg = translate_type(machine_string.strip())
            self.pre_translate_machine = make_machine_jove_compliant(mtype, machine)
            self.pre_translate_mtype = mtype
            if mtype == 'UNKNOWN':
                self.translate_editor.value = '!! Unable to translate jflap {}\n{}'.format(error_msg, machine_string)
                self.translated_to_label.value = '<p style="font-family:monospace;font-size:16px;text-align:center">Translation Failed</p>'
                return
            elif mtype == 'DFA':
                self.save_load_messages.value = '<p style="font-size:small">loading ... success</br>translated to DFA</p>'
                self.translated_to_label.value = '<p style="font-family:monospace;font-size:16px;text-align:center">Translated to DFA</p>'
                self.postfix_text.value = '<p style="font-family:monospace">.dfa</p>'
            elif mtype == 'NFA':
                self.save_load_messages.value = '<p style="font-size:small">loading ... success</br>translated to NFA</p>'
                self.translated_to_label.value = '<p style="font-family:monospace;font-size:16px;text-align:center">Translated to NFA</p>'
                self.postfix_text.value = '<p style="font-family:monospace">.nfa</p>'
            elif mtype == 'PDA':
                self.pre_translate_machine = swap_stack_token(self.pre_translate_machine, 'Z', '#')
                self.save_load_messages.value = '<p style="font-size:small">loading ... success</br>translated to PDA</p>'
                self.translated_to_label.value = '<p style="font-family:monospace;font-size:16px;text-align:center">Translated to PDA</p>'
                self.postfix_text.value = '<p style="font-family:monospace">.pda</p>'
            elif mtype == 'TM':
                self.save_load_messages.value = '<p style="font-size:small">loading ... success</br>translated to TM</p>'
                self.translated_to_label.value = '<p style="font-family:monospace;font-size:16px;text-align:center">Translated to TM</p>'
                self.postfix_text.value = '<p style="font-family:monospace">.tm</p>'

            self.translate_editor.value = '{}'.format(pprint.pformat(self.pre_translate_machine))
            self.translate_result.value = '!! Translated from {}\n{}'.format(file_name, machine_to_rules(mtype, self.pre_translate_machine))
            return

        for i in range(len(machine_string_list)):
            current_line = machine_string_list[i].strip()
            if current_line[:3] == 'DFA':
                del machine_string_list[i]
                machine_string_list.insert(i, current_line[3:].strip())
                self.dfa_editor.value = ('\n'.join(machine_string_list)).strip()
                self.machine_toggle.value = 'DFA'
                self.save_load_messages.value = '<p style="font-size:small"></br>loading ... success</p>'
                return
            elif current_line[:3] == 'NFA':
                del machine_string_list[i]
                machine_string_list.insert(i, current_line[3:].strip())
                self.nfa_editor.value = ('\n'.join(machine_string_list)).strip()
                self.machine_toggle.value = 'NFA'
                self.save_load_messages.value = '<p style="font-size:small"></br>loading ... success</p>'
                return
            elif current_line[:3] == 'PDA':
                del machine_string_list[i]
                machine_string_list.insert(i, current_line[3:].strip())
                self.pda_editor.value = ('\n'.join(machine_string_list)).strip()
                self.machine_toggle.value = 'PDA'
                self.save_load_messages.value = '<p style="font-size:small"></br>loading ... success</p>'
                return
            elif current_line[:2] == 'TM':
                del machine_string_list[i]
                machine_string_list.insert(i, current_line[2:].strip())
                self.tm_editor.value = ('\n'.join(machine_string_list)).strip()
                self.machine_toggle.value = 'TM'
                self.save_load_messages.value = '<p style="font-size:small"></br>loading ... success</p>'
                return
        else:
            machine = None
            editor_string = ''
            if machine_string[0] == '{' and machine_string[-1] == '}':
                try:
                    machine = ast.literal_eval(machine_string)
                    editor_string = '{}'.format(pprint.pformat(machine))
                except:
                    self.translate_editor.value = '!! The file \'{}\' does not contain a well formed dictionary\n{}'.format(
                        list(file_contents.keys())[0], machine_string)
                    self.machine_toggle.value = 'Translate'
                    self.save_load_messages.value = '<p style="font-size:small"></br>loading ... success</p>'
                    return

            if machine is not None:
                if {'Q', 'Sigma', 'Delta', 'q0', 'F'} == machine.keys():
                    self.dfa_editor.value = editor_string
                    self.machine_toggle.value = 'DFA'
                elif {'Q', 'Sigma', 'Delta', 'Q0', 'F'} == machine.keys():
                    self.nfa_editor.value = editor_string
                    self.machine_toggle.value = 'NFA'
                elif {'Q', 'Sigma', 'Gamma', 'Delta', 'q0', 'z0', 'F'} == machine.keys():
                    self.pda_editor.value = editor_string
                    self.machine_toggle.value = 'PDA'
                elif {'Q', 'Sigma', 'Gamma', 'Delta', 'q0', 'B', 'F'} == machine.keys():
                    self.tm_editor.value = editor_string
                    self.machine_toggle.value = 'TM'
                else:
                    self.translate_editor.value = '!! The file \'{}\' does not match any known Jove machine type\n{}'.format(list(file_contents.keys())[0],editor_string)
                    self.machine_toggle.value = 'Translate'

            else:
                self.translate_editor.value = '!! Unable to resolve the file to a known Jove machine type\n{}'.format(
                        machine_string)
                self.machine_toggle.value = 'Translate'

        self.save_load_messages.value = '<p style="font-size:small"></br>loading ... success</p>'
        return
