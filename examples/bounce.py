""" Test TimeBox interface"""
import random
from time import sleep
from timebox import TimeBox
from timeboximage import TimeBoxImage



DELAY = 0.05

class Ball:
    """Simulate a bouncing ball"""
    pos_x = 5
    pos_y = 9
    vel_x = 5
    vel_y = 0

    col_r = 0
    col_g = 0
    col_b = 0

    gravity = 15

    def __init__(self, r, g, b):
        self.col_r = r
        self.col_g = g
        self.col_b = b

    def _rand(self):
        """Create a random distribution with a bias """
        randnr = random.random()
        if random.random() > 0.4:
            return randnr*randnr
        else:
            return -randnr*randnr

    def update(self, deltat):
        """update the positions"""
        # gravity
        self.vel_x *= 0.9997
        self.vel_y *= 0.9997
        self.vel_y -= self.gravity * deltat

        # update pos
        self.pos_x += self.vel_x * deltat
        self.pos_y += self.vel_y * deltat

        # bounce
        if self.pos_x > 10:
            self.vel_x = -self.vel_x - self._rand()
            self.pos_x = 20 - self.pos_x
        if self.pos_x < 0:
            self.vel_x = -self.vel_x + self._rand()
            self.pos_x = - self.pos_x
        if self.pos_y > 10:
            self.vel_y = -self.vel_y - self._rand()
            self.pos_y = 20 - self.pos_y
        if self.pos_y < 0:
            self.vel_y = -self.vel_y + self._rand()
            self.pos_y = - self.pos_y

    def image_add(self, imag):
        """Add the ball to an existing timebox image."""
        imag.put_pixel(round(self.pos_x), 10-round(self.pos_y), self.col_r, self.col_g, self.col_b)
        return imag


TIMEBOX = TimeBox()
TIMEBOX.connect()

BALLS = [Ball(0xf, 0x0, 0x0), Ball(0x0, 0xf, 0x0), Ball(0x0, 0x0, 0xf)]
BALLS.extend([Ball(0xf, 0xf, 0x0), Ball(0x0, 0xf, 0xf), Ball(0xf, 0x0, 0xf)])

while True:
    IMAGE = TimeBoxImage()
    for b in BALLS:
        b.image_add(IMAGE)
    TIMEBOX.set_static_image(IMAGE)
    for b in BALLS:
        b.update(DELAY)
    sleep(DELAY)

TIMEBOX.close()
