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
        Gamma.add(r.text)
    for r in root.iter('pop'):
        Gamma.add(r.text)
    for r in root.iter('push'):
        Gamma.add(r.text)
    if (Gamma.__contains__(None)):
        Gamma.remove(None)
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
