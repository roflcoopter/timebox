""" Sprite based fonts upport """
from utils.gifreader import GIFReader

class Fonts:
    """ Implements the code table for LZW decompression."""
    gamma_value = None
    gamma_table = None
    gif_reader = None
    font_height = None
    font_spacing = None

    def __init__(self, font_sprite_file, font_height, font_width, font_spacing, gamma=1.0):
        """Initialize as reader on dat"""
        self.set_gamma(gamma)
        self.font_height = font_height
        self.font_width = font_width
        self.font_spacing = font_spacing
        self.gif_reader = GIFReader()
        self.gif_reader.read(font_sprite_file)


    def set_gamma(self, new_gamma):
        """ Change the gamma value. Reocomputa the table."""
        self.gamma_value = new_gamma
        self.gamma_table = dict()
        for k in range(256):
            self.gamma_table[k] = self._pixelvalue(k)

    def _pixelvalue(self, k):
        """ Determine the pixel value for pixel with brightness k, 0<=k<256, considering gamma."""
        return int(255.0*pow((k/256.0), 1.0 / self.gamma_value)) >> 4

    def get_pixel(self, char, xix, yix):
        """Get pixel from char with coordinates (xix, yix)."""
        charnum = ord(char.upper()) - 65
        if not charnum in range(0, 26):
            raise Exception("Illegal character")
        if not (xix in range(0, self.font_width) and yix in range(0, self.font_height)):
            raise Exception("Illegal coordinates")
        glob_xix = xix + charnum * self.font_spacing
        color = self.gif_reader.output_image[glob_xix][yix]
        return [self.gamma_table[color[0]], self.gamma_table[color[1]], self.gamma_table[color[2]]]
