"""Jacobu iteration on matrix"""
import random
from time import sleep
from math import atan, sin, cos, pi
from timeboximage import TimeBoxImage
from timebox import TimeBox

class JacobiIteration:
    """Visualize JAcobi Iteration"""

    size = 11
    pivot_row = None
    pivot_column = None
    matrix = None

    gamma = 0.5

    def __init__(self):
        self.matrix = self.randomize_matrix()

    def as_image(self):
        """Return the matrix as an image."""
        image = TimeBoxImage()
        image.set_gamma(self.gamma)
        for row in range(1, self.size+1):
            for column in range(1, self.size+1):
                color = self._color_of_entry(row, column)
                if row == self.pivot_row or column == self.pivot_row or \
                   row == self.pivot_column or column == self.pivot_column:
                    image.put_pixel_gamma(column-1, row-1, color[0], color[1], color[2])
                else:
                    image.put_pixel_gamma(column-1, row-1, color[1], color[0], color[2])
        image.put_pixel(self.pivot_column-1, self.pivot_row-1, 0, 0, 15)
        image.put_pixel(self.pivot_row-1, self.pivot_column-1, 0, 0, 15)
        return image


    def randomize_matrix(self):
        """Initialize the matrix with random numbers."""
        self.matrix = [[0.0 for column in range(1, self.size+1)] for row in range(1, self.size+1)]
        for row in range(1, self.size+1):
            for column in range(1, row+1):
                val = random.normalvariate(0.0, 1.0)
                self.matrix[row-1][column-1] = val
                self.matrix[column-1][row-1] = val

    def _color_of_entry(self, row, column):
        return self._color_map(self.matrix[row-1][column-1])

    def _color_map(self, value):
        """Map a number to a color."""
        compressedval = abs(atan(value) * 2.0 / pi)
        discreteval = int(255.9*compressedval)
        return [discreteval, 0, 0]

    def _select_pivot(self):
        """Select the pivot row and column."""
        # find the element with maximal absolute value on the lower triangle
        maxabs = abs(self.matrix[1][0])
        maxrow = 2
        maxcolumn = 1
        for row in range(3, self.size+1):
            for column in range(1, row):
                if maxabs < abs(self.matrix[row-1][column-1]):
                    maxabs = abs(self.matrix[row-1][column-1])
                    maxrow = row
                    maxcolumn = column
        self.pivot_row = maxrow
        self.pivot_column = maxcolumn

        tan_two_theta = 2 * self.matrix[maxrow-1][maxcolumn-1] / \
            (self.matrix[maxrow-1][maxrow-1]-self.matrix[maxcolumn-1][maxcolumn-1])
        theta = 0.5 * atan(tan_two_theta)
        return maxrow, maxcolumn, theta

    def theta(self):
        """Get the rotation angle for the current matrix."""
        _, _, theta = self._select_pivot()
        return theta

    def _transpose_matrix(self, matrix):
        """transpose the matrix. returns a new object"""
        return [list(i) for i in zip(*matrix)]

    def _copy_matrix(self, matrix):
        """create a copy of the matrix"""
        return [row[:] for row in matrix]

    def _multiply_vector(self, factor, vector):
        """multiply vector with scalar"""
        return [factor*x for x in vector]

    def _vector_sum(self, veca, vecb):
        """Add two vectors."""
        return [veca[n]+vecb[n] for n, _ in enumerate(veca)]

    def _rotate_row(self, rrow, rcolumn, sine, cosine):
        # with k=row, l=col
        # N(l,:) = c .* M(l,:) - s .* M(k,:);
        # N(k,:) = s .* M(l,:) + c .* M(k,:);
        new_matrix = self._copy_matrix(self.matrix)
        new_matrix[rcolumn-1] = self._vector_sum( \
            self._multiply_vector(cosine, self.matrix[rcolumn-1]), \
            self._multiply_vector(-sine, self.matrix[rrow-1]))
        new_matrix[rrow-1] = self._vector_sum(\
            self._multiply_vector(sine, self.matrix[rcolumn-1]), \
            self._multiply_vector(cosine, self.matrix[rrow-1]))
        self.matrix = new_matrix

    def _rotate_column(self, rrow, rcolumn, sine, cosine):
        # with k=row, l=col
        # N(:,l) = c .* M(:,l) - s .* M(:,k);
        # N(:,k) = s .* M(:,l) + c .* M(:,k);
        new_matrix = self._transpose_matrix(self.matrix)
        new_matrix[rcolumn-1] = self._vector_sum( \
            self._multiply_vector(cosine, self.matrix[rcolumn-1]), \
            self._multiply_vector(-sine, self.matrix[rrow-1]))
        new_matrix[rrow-1] = self._vector_sum( \
            self._multiply_vector(sine, self.matrix[rcolumn-1]), \
            self._multiply_vector(cosine, self.matrix[rrow-1]))
        self.matrix = self._transpose_matrix(new_matrix)


    def iterate(self):
        """Perform one iteration of Jacobi's method."""
        (row, column, theta) = self._select_pivot()
        srot = sin(theta)
        crot = cos(theta)
        # update columns according to the rotation
        self._rotate_column(row, column, srot, crot)
        # update rows according to the rotation
        self._rotate_row(row, column, srot, crot)
        return self.theta()


JACOBI = JacobiIteration()

# create the Timebox object
TIMEBOX = TimeBox()
# open the connection to the Timebox
TIMEBOX.connect()

while True:
    JACOBI.randomize_matrix()

    THETA = 1
    while abs(THETA) > 0.01:
        THETA = JACOBI.iterate()
        IMAGE = JACOBI.as_image()
        TIMEBOX.set_static_image(IMAGE)
        sleep(0.33)
