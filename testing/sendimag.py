""" Test TimeBox interface"""
#import sys
import random
from time import sleep
from timeboximage import TimeBoxImage
from timebox import TimeBox

IMAGE = TimeBoxImage()
TIMEBOX = TimeBox()

# create some image

TIMEBOX.connect()

for i in range(1000):
    rand_r = random.randrange(0, 16)
    rand_g = random.randrange(0, 16)
    rand_b = random.randrange(0, 16)
    IMAGE.put_pixel(random.randrange(0, 11), random.randrange(0, 11), rand_r, rand_g, rand_b)
    TIMEBOX.set_static_image(IMAGE)
    sleep(1.0)

TIMEBOX.close()
