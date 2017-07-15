"""Module defines the TimeBoxImage class. """


class TimeBoxImage:
    """ An image to be display on the TimeBox """
    width = 11
    height = 11
    image = 0

    def __init__(self):
        self.image = \
            [[[0 for c in range(3)] for x in range(self.width)] for y in range(self.height)]

    def get_pixel_data(self, xix, yix, cix):
        """ return value of pixel (xix, yix) nd color c (0..2) """
        return self.image[yix][xix][cix]

    def put_pixel(self, xix, yix, rval, gval, bval):
        """Set a pixel in the image."""
        self.image[yix][xix][0] = rval
        self.image[yix][xix][1] = gval
        self.image[yix][xix][2] = bval
