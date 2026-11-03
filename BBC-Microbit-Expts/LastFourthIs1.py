"""Run the "fourth-last symbol is 1" DFA on a BBC micro:bit V2.

Button A supplies the symbol "0"; Button B supplies "1".

Unlike abab_dfa_run_on_bbc_microbit.py, this DFA is never "ended": it runs
online. After every key press the last four symbols read so far scroll by,
followed by "|", and the device plays the happy sound when the DFA is in an
accepting state at that moment, else the sad sound.

The DFA is the 16-state minimal DFA for the regular expression

    (0+1)* 1 (0+1)(0+1)(0+1)

i.e. words whose fourth-last symbol is "1" ("1..." read right to left).
It is the machine called dfaFourthLast in the Jove playground notebook, where
langeq_dfa(remindfa, min_dfa(dfaFourthLast)) checks it against the DFA that
Jove derives from the regular expression itself.

Each state name records the last four symbols read, with the initial state I
standing for "0000" (which is also how a word of fewer than four symbols
behaves: the missing symbols can only be absent, never a 1). A state accepts
exactly when the first of those four recorded symbols is a 1, so the eight
accepting states are the ones named F1xxx.

Shaking the device starts a fresh word.
"""

from microbit import *
import audio


DELTA = {
    #            state   symbol      next state
    ("I", "0"): "I",  # I = 0000
    ("I", "1"): "S1",
    ("S1", "0"): "S10",  # S1 = 0001
    ("S1", "1"): "S11",
    ("S10", "0"): "S100",  # S10 = 0010
    ("S10", "1"): "S101",
    ("S11", "0"): "S110",  # S11 = 0011
    ("S11", "1"): "S111",
    ("S100", "0"): "F1000",  # S100 = 0100
    ("S100", "1"): "F1001",
    ("S101", "0"): "F1010",  # S101 = 0101
    ("S101", "1"): "F1011",
    ("S110", "0"): "F1100",  # S110 = 0110
    ("S110", "1"): "F1101",
    ("S111", "0"): "F1110",  # S111 = 0111
    ("S111", "1"): "F1111",
    ("F1000", "0"): "I",  # F1000 = 1000, and 0000 is I
    ("F1000", "1"): "S1",
    ("F1001", "0"): "S10",  # F1001 = 1001
    ("F1001", "1"): "S11",
    ("F1010", "0"): "S100",  # F1010 = 1010
    ("F1010", "1"): "S101",
    ("F1011", "0"): "S110",  # F1011 = 1011
    ("F1011", "1"): "S111",
    ("F1100", "0"): "F1000",  # F1100 = 1100
    ("F1100", "1"): "F1001",
    ("F1101", "0"): "F1010",  # F1101 = 1101
    ("F1101", "1"): "F1011",
    ("F1110", "0"): "F1100",  # F1110 = 1110
    ("F1110", "1"): "F1101",
    ("F1111", "0"): "F1110",  # F1111 = 1111
    ("F1111", "1"): "F1111",
}

Q0 = "I"

# The fourth-last symbol is the first symbol of the four a state name records,
# so every state whose name begins with "F" is accepting.
ACCEPTING_STATES = (
    "F1000",
    "F1001",
    "F1010",
    "F1011",
    "F1100",
    "F1101",
    "F1110",
    "F1111",
)

WINDOW = 4  # How many trailing symbols of the word are shown.


def get_input():
    """Wait for one input symbol, or return None when the user shakes."""
    while True:
        if button_a.was_pressed():
            return "0"
        if button_b.was_pressed():
            return "1"
        if accelerometer.was_gesture("shake"):
            return None
        sleep(10)  # Yield briefly instead of busy-waiting continuously.


def report(window, accepted):
    """Scroll the trailing symbols and sound the verdict for them.

    Neither call waits, so a press arriving during the scroll is still seen by
    the next get_input(): the device stays responsive and simply moves on to
    the newer verdict.
    """
    display.scroll(window + "|", wait=False, loop=False)
    audio.play(Sound.HAPPY if accepted else Sound.SAD, wait=False)


def do_dfa(delta, q0=Q0, accepting_states=ACCEPTING_STATES):
    """Run delta from q0 forever, reporting acceptance after every symbol.

    The state is always a string naming a DFA state. Only get_input() returns
    None, and that value means "start a fresh word", not a DFA state.
    """
    state = q0
    window = ""

    while True:
        symbol = get_input()

        # A shake abandons the word read so far and starts over.
        if symbol is None:
            state = q0
            window = ""
            display.scroll("|", wait=False, loop=False)
            continue

        key = (state, symbol)
        if key not in delta:
            # Cannot happen for this total DFA; guard the lookup regardless.
            display.show(Image.NO)
            return

        state = delta[key]
        window = (window + symbol)[-WINDOW:]
        report(window, state in accepting_states)


def main():
    do_dfa(DELTA)


# "builtins" supports the Device Simulator Express environment used here.
if __name__ == "__main__" or __name__ == "builtins":
    main()
