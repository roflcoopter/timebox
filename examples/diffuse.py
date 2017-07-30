"""A visual animation of colors diffusing."""
from math import exp
from time import sleep
from random import randrange, random
from operator import add
from timebox import TimeBox
from timeboximage import TimeBoxImage

TIMEBOX = TimeBox()
TIMEBOX.connect()

class Diffuse:
    """Class implementing the animation of colors diffusing."""

    image = [[[0.0 for color in range(3)] for column in range(11)] for row in range(11)]

    # the intensity of the new colored spots
    delta_value = 45.0

    # apply gamma correction to the timebox images
    gamma = 0.4

    kernel_size = None
    kernel = None

    def __init__(self):
        """Constructor. Sets the convolution kernel for diffusion"""
        # set the kernel. One can play with the parameters.
        self.set_kernel(1, 2.0, 0.98)

    def add_delta(self, row, column, color):
        """Add a new color spot (delta function) at (row, column) and with the designated
           color (RGB values between 0 and 1)."""
        delta_color = [self.delta_value * c for c in color]
        self.image[row][column] = list(map(add, delta_color, self.image[row][column]))

    def add_random_dot(self):
        """Add a random color spot."""
        self.add_delta(randrange(11), randrange(11), [random(), random(), random()])

    def set_kernel(self, size, radius, weight):
        """Set a square convolution kernel of 2size+1 with a Guassian curve with radius
           and a total weight between 0 and 1."""
        self.kernel_size = size
        self.kernel = [[0.0 for c in range(2*size+1)] for r in range(2*size+1)]
        total = 0.0

        for rix in range(-size, size+1):
            for cix in range(-size, size+1):
                relrad_squared = (rix*rix+cix*cix)/(radius*radius)
                self.kernel[rix+size][cix+size] = exp(- relrad_squared)
                total += self.kernel[rix+size][cix+size]
        for rix in range(-size, size+1):
            for cix in range(-size, size+1):
                self.kernel[rix+size][cix+size] *= weight / total

    def get_image_padded(self, row, colum, color):
        """Get a value from the image, applying padding with 0 if the indices are
           outside the image."""
        return 0.0 if not (row in range(11) and colum in range(11)) else \
                        self.image[row][colum][color]

    def get_kernel(self, row, column):
        """Get kernel value allowing negative indices with (0,0) the center of the kernel"""
        return self.kernel[row+self.kernel_size][column+self.kernel_size]

    def apply_kernel(self):
        """Apply the concolution kernel to the image to compute a new image."""
        new_image = [[[0.0 for c in range(3)] for r in range(11)] for c in range(11)]
        for rix in range(11):
            for cix in range(11):
                for colx in range(3):
                    for krix in range(-self.kernel_size, self.kernel_size+1):
                        for kcix in range(-self.kernel_size, self.kernel_size+1):
                            new_image[rix][cix][colx] += self.get_image_padded(rix+krix, cix+kcix, \
                                                colx) * self.get_kernel(krix, kcix)
        self.image = new_image

    def get_image_color(self, row, column):
        """Get color for the image indices. Applying saturation above the value 1.0"""
        return [min(int(round(255.0 * self.image[row][column][cix])), 255) for cix in range(3)]

    def as_image(self):
        """Return a TimeBox image for the current state."""
        img = TimeBoxImage()
        img.set_gamma(self.gamma)
        for rix in range(11):
            for cix in range(11):
                col = self.get_image_color(rix, cix)
                img.put_pixel_gamma(cix, rix, col[0], col[1], col[2])
        return img



DIFFUSE = Diffuse()

while True:
    TIMEBOX.set_static_image(DIFFUSE.as_image())
    sleep(0.05)
    DIFFUSE.apply_kernel()
    if random() < 0.20:
        DIFFUSE.add_random_dot()
    TIMEBOX.clear_input_buffer_quick()

TIMEBOX.close()
