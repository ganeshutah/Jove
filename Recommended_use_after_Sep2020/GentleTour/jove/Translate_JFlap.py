import xml.etree.ElementTree as ET


def translate_type(raw_xml):
    root = ET.fromstring(raw_xml)
    # Try finite automata first
    translated_machine = {}
    machine_type = 'UNKNOWN'
    error_msg = ''

    if root[0].text == 'fa':
        if len(root.find('automaton').findall('state/initial')) == 1:
            try:
                translated_machine = translate_DFA(raw_xml)
                machine_type = 'DFA'
            except:
                try:
                    translated_machine = translate_NFA(raw_xml)
                    machine_type = 'NFA'
                except Exception as e:
                    error_msg = str(e)
        else:
            try:
                translated_machine = translate_NFA(raw_xml)
                machine_type = 'NFA'
            except Exception as e:
                error_msg = str(e)
    elif root[0].text == 'pda':
        try:
            translated_machine = translate_PDA(raw_xml)
            machine_type = 'PDA'
        except Exception as e:
            error_msg = str(e)
    elif root[0].text == 'turing':
        try:
            translated_machine = translate_TM(raw_xml)
            machine_type = 'TM'
        except Exception as e:
            error_msg = str(e)
    else:
        error_msg = 'Error translating, unknown machine type.'

    return machine_type, translated_machine, error_msg


def translate_DFA (raw_xml):
     root = ET.fromstring(raw_xml)
     names = set()
     Sigma = set()
     Delta = {}
     Q0 = set()
     Final = set()
     for state in root.iter('state'):
         names.add(state.get('name'))
         for final in state.iter('final'):
             Final.add(state.get('name'))
         for initial in state.iter('initial'):
             Q0.add(state.get('name'))
             q0 = state.get('name')
     for r in root.iter('read'):
         Sigma.add(r.text)
     for t in root.iter('transition'):
         snum = t.find('from').text
         fromName = root.find('.//state[@id=\'' + snum + '\']').get('name')
         snum = t.find('to').text
         toName = root.find('.//state[@id=\'' + snum + '\']').get('name')
         letter = t.find('read').text
         # check that the transition doesn't already exist first
         if (fromName, letter) in Delta.keys():
             raise ValueError('Found duplicate transitions')
         Delta[(fromName, letter)] = toName
         if letter == None:
             raise ValueError('Found and epsilon transition while trying to translate to DFA')
     for q in Q0:
          q0 = q
     dfa = {'Q': names, 'Sigma': Sigma, 'Delta': Delta, 'q0': q0, 'F': Final}
     return dfa


def translate_NFA(raw_xml):
    root = ET.fromstring(raw_xml)
    names = set()
    Sigma = set()
    Delta = {}
    Q0 = set()
    Final = set()
    for state in root.iter('state'):
        names.add(state.get('name'))
        for final in state.iter('final'):
            Final.add(state.get('name'))
        for initial in state.iter('initial'):
            Q0.add(state.get('name'))
            q0 = state.get('name')
    for r in root.iter('read'):
        Sigma.add(r.text)
    if( Sigma.__contains__(None) ):
        Sigma.remove(None)
    for t in root.iter('transition'):
        snum = t.find('from').text
        fromName = root.find('.//state[@id=\'' + snum + '\']').get('name')
        snum = t.find('to').text
        toName = root.find('.//state[@id=\'' + snum + '\']').get('name')
        letter = t.find('read').text
        if letter == None:
            letter = ''
        # add a new set if the key doesn't already exist
        if (fromName, letter) not in Delta.keys():
            Delta[(fromName, letter)] = set()
        Delta[(fromName, letter)].add(toName)
    nfa = {'Q': names, 'Sigma': Sigma, 'Delta': Delta, 'Q0': Q0, 'F': Final}
    return nfa


def translate_PDA(raw_xml):
    root = ET.fromstring(raw_xml)
    names = set()
    Sigma = set()
    Gamma = set()
    Delta = {}
    Q0 = set()
    Final = set()
    for state in root.iter('state'):
        names.add(state.get('name'))
        for final in state.iter('final'):
            Final.add(state.get('name'))
        for initial in state.iter('initial'):
            Q0.add(state.get('name'))
            q0 = state.get('name')
    for r in root.iter('read'):
        Sigma.add(r.text)
    if (Sigma.__contains__(None)):
        Sigma.remove(None)

    for r in root.iter('read'):
        if r.text is not None:
            Gamma.update(set(r.text))
    for r in root.iter('pop'):
        if r.text is not None:
            Gamma.update(set(r.text))
    for r in root.iter('push'):
        if r.text is not None:
            Gamma.update(set(r.text))

    for t in root.iter('transition'):
        snum = t.find('from').text
        fromName = root.find('.//state[@id=\'' + snum + '\']').get('name')
        snum = t.find('to').text
        toName = root.find('.//state[@id=\'' + snum + '\']').get('name')
        letter = t.find('read').text
        pop = t.find('pop').text
        push = t.find('push').text
        if letter == None:
            letter = ''
        if pop == None:
            pop = ''
        if push == None:
            push = ''
        if (fromName, letter, pop) in Delta.keys():
            Delta[(fromName, letter, pop)].add( (toName, push) )
        else:
            Delta[(fromName, letter, pop)] = {(toName, push)}
    for q in Q0:
        q0 = q
    z0 = '#'
    pda = {'Q': names, 'Sigma': Sigma, 'Gamma': Gamma, 'Delta': Delta, 'q0': q0, 'z0': z0, 'F': Final}
    return pda


def translate_TM(raw_xml):
    root = ET.fromstring(raw_xml)
    names = set()
    Sigma = set()
    Gamma = set()
    Delta = {}
    Q0 = set()
    Final = set()
    if len(root.find('automaton').findall('state')) != 0:
        for state in root.iter('state'):
            names.add(state.get('name'))
            for final in state.iter('final'):
                Final.add(state.get('name'))
            for initial in state.iter('initial'):
                Q0.add(state.get('name'))
                q0 = state.get('name')
    else:
        for state in root.iter('block'):
            names.add(state.get('name'))
            for final in state.iter('final'):
                Final.add(state.get('name'))
            for initial in state.iter('initial'):
                Q0.add(state.get('name'))
                q0 = state.get('name')
    for r in root.iter('read'):
        Sigma.add(r.text)
    if (Sigma.__contains__(None)):
        Sigma.remove(None)
    for r in root.iter('write'):
        Gamma.add(r.text)
    Gamma.add('.')
    if (Gamma.__contains__(None)):
        Gamma.remove(None)
    for t in root.iter('transition'):
        snum = t.find('from').text
        if root.find('.//block[@id=\'' + snum + '\']') != None:
            fromName = root.find('.//block[@id=\'' + snum + '\']').get('name')
        elif root.find('.//state[@id=\'' + snum + '\']') != None:
            fromName = root.find('.//state[@id=\'' + snum + '\']').get('name')
        else: fromName = root.find('.//state[@id=\'' + snum + '\']').get('name')
        snum = t.find('to').text
        if root.find('.//block[@id=\'' + snum + '\']') != None:
            toName = root.find('.//block[@id=\'' + snum + '\']').get('name')
        elif root.find('.//state[@id=\'' + snum + '\']') != None:
            toName = root.find('.//state[@id=\'' + snum + '\']').get('name')
        else: toName = root.find('.//state[@id=\'' + snum + '\']').get('name')
        letter = t.find('read').text
        write = t.find('write').text
        move = t.find('move').text
        if letter == None:
            letter = '.'
        if write == None:
            write = '.'
        if move == None:
            move = '.'
        if (fromName, letter) in Delta.keys():
            Delta[(fromName, letter)].add( (toName, write, move) )
        else:
            Delta[(fromName, letter)] = {(toName, write, move)}
    q0 = ''
    for q in Q0:
        q0 = q
    B = '.'
    tm = {'Q': names, 'Sigma': Sigma, 'Gamma': Gamma, 'Delta': Delta, 'q0': q0, 'B': B, 'F': Final}
    return tm


def machine_to_rules(mtype, machine):
    transitions = machine['Delta']
    machine_string = ''
    if mtype == 'DFA':
        for t in transitions.keys():
            machine_string += f'{t[0]}: {t[1]} -> {transitions[t]}\n'
    elif mtype == 'NFA':
        for t in transitions.keys():
            for dest in transitions[t]:
                t_symbol = '\'\'' if t[1] == '' else t[1]
                machine_string += f'{t[0]}: {t_symbol} -> {dest}\n'
    elif mtype == 'PDA':
        for t in transitions.keys():
            for dest in transitions[t]:
                t1_sym = '\'\'' if t[1] == '' else t[1]
                t2_sym = '\'\'' if t[2] == '' else t[2]
                dest1_sym = '\'\'' if dest[1] == '' else dest[1]
                machine_string += f'{t[0]}: {t1_sym} , {t2_sym} ; {dest1_sym} -> {dest[0]}\n'
    elif mtype == 'TM':
        for t in transitions.keys():
            for dest in transitions[t]:
                t1_sym = '\'\'' if t[1] == '' else t[1]
                dest1_sym = '\'\'' if dest[1] == '' else dest[1]
                dest2_sym = '\'\'' if dest[2] == '' else dest[2]
                machine_string += f'{t[0]}: {t1_sym} ; {dest1_sym} , {dest2_sym} -> {dest[0]}\n'

    return machine_string


def make_machine_jove_compliant(mtype, machine):
    if mtype == 'DFA':
        i_state = machine['q0']
        if i_state in machine['F'] and not i_state.lower().startswith('if'):
            machine = replace_state_name_dfa(machine, i_state, f'IF_{i_state}')
        elif not i_state.lower().startswith('i'):
            machine = replace_state_name_dfa(machine, i_state, f'I_{i_state}')

        for state in machine['F']:
            if state != machine['q0'] and not state.lower().startswith('f'):
                machine = replace_state_name_dfa(machine, state, f'F_{state}')

    elif mtype == 'NFA':
        for i_state in machine['Q0']:
            if i_state in machine['F'] and not i_state.lower().startswith('if'):
                machine = replace_state_name_nfa(machine, i_state, f'IF_{i_state}')
            elif not i_state.lower().startswith('i'):
                machine = replace_state_name_nfa(machine, i_state, f'I_{i_state}')

        for state in machine['F']:
            if state not in machine['Q0'] and not state.lower().startswith('f'):
                machine = replace_state_name_nfa(machine, state, f'F_{state}')

    elif mtype == 'PDA':
        i_state = machine['q0']
        if i_state in machine['F'] and not i_state.lower().startswith('if'):
            machine = replace_state_name_pda(machine, i_state, f'IF_{i_state}')
        elif not i_state.lower().startswith('i'):
            machine = replace_state_name_pda(machine, i_state, f'I_{i_state}')

        for state in machine['F']:
            if state != machine['q0'] and not state.lower().startswith('f'):
                machine = replace_state_name_pda(machine, state, f'F_{state}')

    elif mtype == 'TM':
        i_state = machine['q0']
        if i_state in machine['F'] and not i_state.lower().startswith('if'):
            machine = replace_state_name_tm(machine, i_state, f'IF_{i_state}')
        elif not i_state.lower().startswith('i'):
            machine = replace_state_name_tm(machine, i_state, f'I_{i_state}')

        for state in machine['F']:
            if state != machine['q0'] and not state.lower().startswith('f'):
                machine = replace_state_name_tm(machine, state, f'F_{state}')

    return machine


def replace_state_name_dfa(machine, old_name, new_name):
    if machine['q0'] == old_name:
        machine['q0'] = new_name
    if old_name in machine['F']:
        machine['F'].add(new_name)
        machine['F'].remove(old_name)

    for t in machine['Delta'].keys():
        if t[0] == old_name:
            new_t = (new_name, t[1])
            machine['Delta'][new_t] = machine['Delta'][t]
            machine['Delta'].pop(t, None)

    for t in machine['Delta'].keys():
        if machine['Delta'][t] == old_name:
            machine['Delta'][t] = new_name

    machine['Q'].add(new_name)
    machine['Q'].remove(old_name)
    return machine


def replace_state_name_nfa(machine, old_name, new_name):
    if old_name in machine['Q0']:
        machine['Q0'].add(new_name)
        machine['Q0'].remove(old_name)
    if old_name in machine['F']:
        machine['F'].add(new_name)
        machine['F'].remove(old_name)

    for t in machine['Delta'].keys():
        if t[0] == old_name:
            new_t = (new_name, t[1])
            machine['Delta'][new_t] = machine['Delta'][t]
            machine['Delta'].pop(t, None)

    for t in machine['Delta'].keys():
        for dest in machine['Delta'][t]:
            if dest == old_name:
                machine['Delta'][t].add(new_name)
                machine['Delta'][t].remove(old_name)

    machine['Q'].add(new_name)
    machine['Q'].remove(old_name)
    return machine


def replace_state_name_pda(machine, old_name, new_name):
    if machine['q0'] == old_name:
        machine['q0'] = new_name
    if old_name in machine['F']:
        machine['F'].add(new_name)
        machine['F'].remove(old_name)

    for t in machine['Delta'].keys():
        if t[0] == old_name:
            new_t = (new_name, t[1], t[2])
            machine['Delta'][new_t] = machine['Delta'][t]
            machine['Delta'].pop(t, None)

    for t in machine['Delta'].keys():
        for dest in machine['Delta'][t]:
            if dest[0] == old_name:
                new_dest = (new_name, dest[1])
                machine['Delta'][t].add(new_dest)
                machine['Delta'][t].remove(dest)

    machine['Q'].add(new_name)
    machine['Q'].remove(old_name)
    return machine


def replace_state_name_tm(machine, old_name, new_name):
    if machine['q0'] == old_name:
        machine['q0'] = new_name
    if old_name in machine['F']:
        machine['F'].add(new_name)
        machine['F'].remove(old_name)

    for t in machine['Delta'].keys():
        if t[0] == old_name:
            new_t = (new_name, t[1])
            machine['Delta'][new_t] = machine['Delta'][t]
            machine['Delta'].pop(t, None)

    for t in machine['Delta'].keys():
        for dest in machine['Delta'][t]:
            if dest[0] == old_name:
                new_dest = (new_name, dest[1], dest[2])
                machine['Delta'][t].add(new_dest)
                machine['Delta'][t].remove(dest)

    machine['Q'].add(new_name)
    machine['Q'].remove(old_name)
    return machine


def swap_stack_token(machine, old_token, new_token):
    # only swap tokens if the machine is a PDA
    if 'z0' in machine.keys():
        # swap the stack token definition
        machine['z0'] = new_token

        # swap the token in 'Gamma'
        machine['Gamma'].add(new_token)
        machine['Gamma'].remove(old_token)

        # swap all the tokens in the transition keys
        for t in machine['Delta'].keys():
            if old_token in t[2]:
                new_t = (t[0], t[1], t[2].replace(old_token, new_token))
                machine['Delta'][new_t] = machine['Delta'][t]
                machine['Delta'].pop(t, None)

        # swap the tokens in the transition stack writes
        for t in machine['Delta'].keys():
            for dest in machine['Delta'][t]:
                if old_token in dest[1]:
                    new_dest = (dest[0], dest[1].replace(old_token, new_token))
                    machine['Delta'][t].add(new_dest)
                    machine['Delta'][t] -= {dest}
    return machine
