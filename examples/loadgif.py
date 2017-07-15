"""Load a gif file and display it on TimeBox."""

import sys
from timeboximage import TimeBoxImage
from timebox import TimeBox
from gifreader import GIFReader

if len(sys.argv) < 2:
    print('Please provide name of a GIF file to display.')
    exit()

FILENAME = sys.argv[1]

GIFREADER = GIFReader()
GIFREADER.read(FILENAME)

IMAGE = TimeBoxImage()
for xix in range(11):
    for yix in range(11):
        IMAGE.put_pixel(xix, yix, GIFREADER.output_image[xix][yix][0] >> 4, \
                            GIFREADER.output_image[xix][yix][1] >>4, \
                            GIFREADER.output_image[xix][yix][2]>>4)

TIMEBOX = TimeBox()
TIMEBOX.connect()
TIMEBOX.set_static_image(IMAGE)
TIMEBOX.close()
