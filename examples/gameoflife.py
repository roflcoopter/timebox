""" Test TimeBox interface"""
from time import sleep
from timebox import TimeBox
from life import GameOfLife

TIMEBOX = TimeBox()
TIMEBOX.connect()

GOL = GameOfLife()
GOL.randomize_board()

while True:
    GOL.randomize_board()
    for i in range(100):
        for j in range(GOL.animationSteps):
            TIMEBOX.set_static_image(GOL.as_image(j))
            sleep(0.04)
        old_board = GOL.board
        GOL.iterate()
        TIMEBOX.clear_input_buffer_quick()
        if old_board == GOL.board:
            sleep(4.0)
            break

TIMEBOX.close()
