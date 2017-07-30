"""Module defines the TimeBoxImage class. """


class TimeBoxImage:
    """ An image to be displayed on the TimeBox """
    width = 11
    height = 11
    image = None

    gamma_value = None
    gamma_table = None

    def __init__(self, height=11, width=11):
        self.height = height
        self.width = width
        self.image = \
            [[[0 for c in range(3)] for x in range(self.width)] for y in range(self.height)]

    def _gamma_correction(self, k):
        """ Determine the pixel value (0-15) for pixel with brightness k,
        0<=k<256, considering gamma."""

        return int(256.0*pow((k/256.0), 1.0 / self.gamma_value)) >> 4

    def set_gamma(self, new_gamma):
        """ Change the gamma value. Recompute the table."""
        if self.gamma_value != new_gamma:
            self.gamma_value = new_gamma
            self.gamma_table = [self._gamma_correction(k) for k in range(256)]

    def get_pixel_data(self, xix, yix, cix):
        """ return value of pixel (xix, yix) nd color c (0..2) """
        return self.image[yix][xix][cix]

    def put_pixel(self, xix, yix, rval, gval, bval):
        """Set a pixel in the image."""
        self.image[yix][xix] = [rval, gval, bval]

    def put_pixel_gamma(self, xix, yix, rval, gval, bval):
        """Set a pixel in the image, applying gamma correction.
        Values between 0 and 255."""
        self.image[yix][xix] = [self.gamma_table[v] for v in [rval, gval, bval]]
