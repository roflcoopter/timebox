""" Test TimeBox interface"""
from time import sleep
from timebox import TimeBox


def receive_timebox():
    """Receive any queued messaged from the timebox."""
    TIMEBOX.receive()
    while TIMEBOX.has_message():
        if TIMEBOX.buffer_starts_with_garbage():
            print('Garbage: ', TIMEBOX.remove_garbage())
        else:
            rec = TIMEBOX.remove_message()
            dec = TIMEBOX.decode(rec)
            if dec[0:5] == 'error':
                print(dec, rec)
            else:
                decb = [c for c in dec]
                print('Rec: ', ' '.join('{:02X}'.format(k, 'x') for k in decb))
        TIMEBOX.receive()


TRACE = [
    ["set view", [0x01, 0x00, 0x00, 0xff, 0x00]],
    ["switch radio", [0x01]],
    ["set view", [0x00, 0x01, 0x00, 0x00, 0xff]],
    ["switch radio", [0x00]],
]



TIMEBOX = TimeBox()
TIMEBOX.connect()

receive_timebox()

for cmd in TRACE:
    TIMEBOX.send_command(cmd[0], cmd[1])
    sleep(1.5)
    receive_timebox()

TIMEBOX.close()
