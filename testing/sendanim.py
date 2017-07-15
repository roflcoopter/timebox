""" Test TimeBox interface"""
#import sys
import random
from timeboximage import TimeBoxImage
from timebox import TimeBox

IMAGES = []

TIMEBOX = TimeBox()

# create some image


for i in range(10):
    IMAGE = TimeBoxImage()
    rand_r = random.randrange(0, 16)
    rand_g = random.randrange(0, 16)
    rand_b = random.randrange(0, 16)
    IMAGE.put_pixel(random.randrange(0, 11), random.randrange(0, 11), rand_r, rand_g, rand_b)
    IMAGES.append(IMAGE)

TIMEBOX.connect()
FRAME_DELAY = 5
TIMEBOX.set_dynamic_images(IMAGES, FRAME_DELAY)
TIMEBOX.close()
