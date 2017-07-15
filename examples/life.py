"""Conwell's Game of Life simulation"""
import random
from timeboximage import TimeBoxImage

ALIVE = 2
DEAD = 0
DYING = -1
GROWING = 1

class GameOfLife:
    """Conwell's Game of Life simulation"""

    size = 11
    animationSteps = 16

    def __init__(self):
        self.board = self.empty_board()

    def empty_board(self):
        """Return an empty board"""
        return [[0 for y in range(self.size)] for x in range(self.size)]

    def _get_status(self, xix, yix):
        """Returns the status of the cell (xix, yix) on the board."""
        return self.board[xix][yix]

    def as_image(self, aix):
        """Return the board as an image with animation phase 0<=aix<animationSteps."""
        image = TimeBoxImage()
        if aix < (self.animationSteps >> 1):
            aval = int(((0xf * aix)<<1) / self.animationSteps)
            bval = 0x0
        else:
            aval = 0xf
            bval = int(0xf * (aix-(self.animationSteps>>1)<<1) / self.animationSteps)
        for xix in range(self.size):
            for yix in range(self.size):
                if self._get_status(xix, yix) == DYING:
                    image.put_pixel(xix, yix, 0xf-bval, 0xf - aval, 0xf - aval)
                if self._get_status(xix, yix) == GROWING:
                    image.put_pixel(xix, yix, bval, aval, bval)
                if self._get_status(xix, yix) == ALIVE:
                    image.put_pixel(xix, yix, 0xf, 0xf, 0xf)
        return image

    def is_alive(self, xix, yix):
        """Test if the cell at position xix, yix is alive in the current board"""
        return self.board[xix][yix] == ALIVE or self.board[xix][yix] == GROWING

    def _count_neighbors(self, xix, yix):
        lix = (xix-1) % self.size
        rix = (xix+1) % self.size
        tix = (yix-1) % self.size
        bix = (yix+1) % self.size
        return \
            self.is_alive(lix, tix) + \
            self.is_alive(xix, tix) + \
            self.is_alive(rix, tix) + \
            self.is_alive(lix, yix) + \
            self.is_alive(rix, yix) + \
            self.is_alive(lix, bix) + \
            self.is_alive(xix, bix) + \
            self.is_alive(rix, bix)

    def iterate(self):
        """Play one iteration of the game"""
        # Overpopulation: if a living cell is surrounded by more than three living cells, it dies.
        # Stasis: if a living cell is surrounded by two or three living cells, it survives.
        # Underpopulation: if a living cell is surrounded by fewer than two living cells, it dies.
        # Reproduction: if a dead cell is surrounded by exactly three cells, it becomes a live cell.

        new_board = self.empty_board()

        for xix in range(self.size):
            for yix in range(self.size):
                neighbors = self._count_neighbors(xix, yix)
                if self.is_alive(xix, yix):
                    if neighbors > 3 or neighbors < 2:
                        new_board[xix][yix] = DYING
                    if neighbors > 1 and neighbors <= 3:
                        new_board[xix][yix] = ALIVE
                else:
                    if neighbors == 3:
                        new_board[xix][yix] = GROWING
                    else:
                        new_board[xix][yix] = DEAD

        self.board = new_board

    def randomize_board(self):
        """Initialize the board with random setting."""
        for xix in range(self.size):
            for yix in range(self.size):
                if random.randrange(3) < 2:
                    self.board[xix][yix] = DEAD
                else:
                    self.board[xix][yix] = ALIVE
