"""Run a DFA on a BBC micro:bit V2.

Button A supplies the symbol "a"; Button B supplies "b".
Shake the device to end the word and decide whether its final DFA state accepts.
"""

from microbit import *
import audio


# This DFA accepts words over {a, b} whose final four symbols are "abab".
DELTA = {
    ("I", "a"): "S1",
    ("I", "b"): "I",
    ("S1", "a"): "S1",
    ("S1", "b"): "S2",
    ("S2", "a"): "S3",
    ("S2", "b"): "I",
    ("S3", "a"): "S1",
    ("S3", "b"): "F",
    ("F", "a"): "S2",
    ("F", "b"): "I",
}


def get_input():
    """Wait for one input symbol, or return None when the user shakes."""
    while True:
        if button_a.was_pressed():
            return "a"
        if button_b.was_pressed():
            return "b"
        if accelerometer.was_gesture("shake"):
            return None
        sleep(10)  # Yield briefly instead of busy-waiting continuously.


def do_dfa(delta, q0="I", accepting_states=("F",)):
    """Execute delta from q0 and return True exactly when the final state accepts.

    The state is always a string naming a DFA state. Only get_input() returns
    None, and that value means "the word is finished", not a DFA state.
    """
    state = q0
    word = ""

    while True:
        symbol = get_input()

        # A shake terminates the input word. Membership always evaluates to bool.
        if symbol is None:
            return state in accepting_states

        key = (state, symbol)
        if key not in delta:
            # No defined transition: reject, while leaving state well-typed.
            return False

        state = delta[key]
        word += symbol
        audio.play(Sound.SPRING)
        display.scroll(word + "|", wait=False, loop=False)


def show_result(accepted):
    """Show and periodically sound the accepting or rejecting outcome."""
    if accepted:
        display.show(Image.YES)
        sound = Sound.HAPPY
    else:
        display.show(Image.NO)
        sound = Sound.SAD

    while True:
        audio.play(sound)
        sleep(5000)


def main():
    accepted = do_dfa(DELTA)
    show_result(accepted)


# "builtins" supports the Device Simulator Express environment used here.
if __name__ == "__main__" or __name__ == "builtins":
    main()
