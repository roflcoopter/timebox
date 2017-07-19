"""Load a gif file and display it on TimeBox."""

from time import sleep
from timeboximage import TimeBoxImage
from timebox import TimeBox
from utils.fonts import Fonts


FONTFILE = "../examples/fonts/arcadeclassic.gif"

FONT = Fonts(FONTFILE, 9, 9, 10, 0.6)

TEXT = "HELLOTIMEBOX"
SPACING = 2

# create the Timebox object
TIMEBOX = TimeBox()
# open the connection to the Timebox
TIMEBOX.connect()

# offset determines the location of the first column of the display
# relative to the entire text image
for offset in range(-11, len(TEXT)*(FONT.font_width + SPACING)+11):
    # create a new image for this frame
    IMAGE = TimeBoxImage()
    # range over all columns on the display
    for xix in range(11):
        # compute the corresponding global x value
        gxix = offset + xix
        # compute the relative x value to the current character
        rxix = gxix % (FONT.font_width + SPACING)
        # check if rxix is inside a character or not
        if rxix < FONT.font_width:
            # determine which character it is in
            charnum = gxix // (FONT.font_width + SPACING)
            # if it is inside the range of the text to display
            if charnum in range(len(TEXT)):
                # get the character itself
                char = TEXT[charnum]
                # iterate over the rows on the display
                for yix in range(FONT.font_height):
                    # get the pixel color
                    pix = FONT.get_pixel(char, rxix, yix)
                    # set the Timebox image pixel
                    IMAGE.put_pixel(xix, yix+1, pix[0], pix[1], pix[2])
    # send the new image to the Timebox
    TIMEBOX.set_static_image(IMAGE)
    # sleep for the animation
    sleep(0.1)

# close the connection to the Timebox
TIMEBOX.close()
