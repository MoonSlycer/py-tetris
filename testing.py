# ┌──────────────────────────────────────────────────────────────────┐
# │ Title:    testing                                                │
# │ Author:   Charlie Wensink                                        │
# │ Date:     May 31, 2026                                           │
# │ Purpose:  test main gameplay logic without curses.               │
# └──────────────────────────────────────────────────────────────────┘

class FallingTetromino:
    """class to represent the falling tetromino"""
    def __init__(self, tetromino, init_y, init_x):
        self.tetromino = copy2DArray(tetromino)
        self.y = init_y
        self.x = init_x
        self.height = len(tetromino)
        self.width = len(tetromino[0])


    def getTetromino(self):
        return self.tetromino


    def getY(self):
        return self.y


    def getX(self):
        return self.x


    def getBlockPositions(self):
        """Return the board position of each block in the tetromino."""
        positions = []
        for y in range(self.height):
            for x in range(self.width):
                # check if there is data at current position.
                if self.tetromino[y][x] != '':
                    # append the board position of each block in
                    # tetromino.
                    positions.append(
                        (self.y + y, self.x + x)
                    )
        return positions


    def rotateRight(self):
        """update self.tetromino to be itself but rotated right 90
         degrees.
        """
        old_tetromino = copy2DArray(self.tetromino)
        new_tetromino = empty2DArray(self.height, self.width)

        for y in range(self.height):
            for x in range(self.width):
                new_tetromino[x][(self.width-1)-y] = old_tetromino[y][x]

        self.tetromino = new_tetromino


def empty2DArray(height, width):
    """return a 2d array of empty strings ('') from given height and
     width.
     """
    array_out = [
        [''] * width for _ in range(height)
    ]

    return array_out


def copy2DArray(array_in):
    """copy the 2D array smoothly."""
    array_out = [row.copy() for row in array_in]
    return array_out


def main():
    # Initialize ─────────────────────────────────────────────────────
    # Define the shapes of all Tetrominoes.
    I_TETROMINO = [
        ['', '', '', ''],
        ['I', 'I', 'I', 'I'],
        ['', '', '', ''],
        ['', '', '', ''],
    ]

    J_TETROMINO = [
        ['J', '', ''],
        ['J', 'J', 'J'],
        ['', '', ''],
    ]

    L_TETROMINO = [
        ['', '', 'L'],
        ['L', 'L', 'L'],
        ['', '', ''],
    ]

    O_TETROMINO = [
        ['', '', '', ''],
        ['', 'O', 'O', ''],
        ['', 'O', 'O', ''],
        ['', '', '', ''],
    ]

    S_TETROMINO = [
        ['', 'S', 'S'],
        ['S', 'S', ''],
        ['', '', ''],
    ]

    T_TETROMINO = [
        ['', 'T', ''],
        ['T', 'T', 'T'],
        ['', '', ''],
    ]

    Z_TETROMINO = [
        ['Z', 'Z', ''],
        ['', 'Z', 'Z'],
        ['', '', ''],
    ]

    # FOR DEBUGGING PURPOSES ONLY.
    DEBUG_TETROMINO = [
        ['1', '2', '3'],
        ['4', '5', '6'],
        ['7', '8', '9'],
    ]

    # board setup.
    BOARD_HEIGHT = 20
    BOARD_WIDTH = 10
    board_data = empty2DArray(BOARD_HEIGHT, BOARD_WIDTH)

    # set up board with blocks already on there.
    board_data = [
        ['', '', '', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', '', '', ''],
        ['L', 'L', 'L', '', '', '', '', '', '', ''],
        ['L', 'S', 'S', 'T', '', '', 'Z', 'Z', '', ''],
        ['S', 'S', 'T', 'T', 'T', '', '', 'Z', 'Z', '']]

    keyboard_input = ''
    new_tetromino = FallingTetromino(I_TETROMINO, 0, 2)
    while keyboard_input != 'q':
        # Input ──────────────────────────────────────────────────────────
        # get user input.
        keyboard_input = input()

        # Process ────────────────────────────────────────────────────────
        new_tetromino.rotateRight()
        new_tetromino.y += 1

        # Output ─────────────────────────────────────────────────────────
        # display falling block.
        display_data = copy2DArray(board_data)
        for (block_y, block_x) in new_tetromino.getBlockPositions():
            display_data[block_y][block_x] = 'T'

        # display board.
        for row in display_data:
            for data in row:
                if data:
                    print('[]', end='')
                else:
                    print('..', end='')
            print()

 # Terminate ──────────────────────────────────────────────────────

    return 0  # Return 0 indicates a successful completion


# Program entry point
if __name__ == "__main__":
    main()
# ────────────────────────────────────────────────────────────────
