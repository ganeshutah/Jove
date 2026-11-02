"""
To get started, check out the "Device Simulator Express: Getting Started" command in the command pallete, which you can access with `CMD + SHIFT + P` For Mac and `CTRL + SHIFT + P` for Windows and Linux.

Get started with micro:bit and MicroPython on:
https://microbit-micropython.readthedocs.io/en/latest/.
"""

from microbit import *

delta = {
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


def doDFA(delta:dict, q0 = "I", F = ["F"]) -> bool:
    """execute a DFA with a delta function as specified, on the BBC micro:bit"""
    state = q0
    u_input = ""
    prev = ""
    while u_input is not None:
        u_input = getInput()
        # audio.play(Sound.SPRING)
        if u_input is not None:
            prev += u_input
            display.scroll(prev + "|", wait=False, loop=True)
            tmp = tuple([state, u_input])
            # print(tmp)
            # print(delta.keys())
            if tmp in delta.keys():
                state = delta[tmp]
            else:
                state = None
                return False
        else:
            return state in F
        u_input = ""


def getInput():
    """return a `str`/char corresponding to the input that has been triggered"""
    while True:
        if button_a.was_pressed():
            return "a"
        if button_b.was_pressed():
            return "b"
        # if pin0.is_touched():
        #     return '0'
        # if pin1.is_touched():
        #     return "1"
        # if pin2.is_touched():
        #     return "2"
        # if pin_logo.is_touched():
        #     return None
        if accelerometer.was_gesture('shake'):
            return None


def main():
    # audio.play(Sound.HELLO, wait=True)
    if doDFA(delta):
        display.show(Image.YES, wait=False, loop=True)
        while True:
            # audio.play(Sound.HAPPY)
            sleep(5000)
    else:
        display.show(Image.NO, wait=False, loop=True)
        while True:
            # audio.play(Sound.SAD)
            sleep(5000)


if __name__ == "__main__" or __name__ == "builtins":
    main()
