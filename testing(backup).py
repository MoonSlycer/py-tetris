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
        self.height = len(self.tetromino)-1
        self.width = len(self.tetromino[0])-1


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
                new_tetromino[x][self.width-y] = old_tetromino[y][x]

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

    # show board.
    for row in board_data: print(row)

    keyboard_input = ''
    posY = 0
    posX = 0
    new_piece = copy2DArray(T_TETROMINO)
    new_tetromino = FallingTetromino(T_TETROMINO)
    while keyboard_input != 'q':
        # Input ──────────────────────────────────────────────────────────
        # get user input.
        keyboard_input = input()

        # Process ────────────────────────────────────────────────────────
        # increment debug tetromino's x and y position.
        posY = (posY + 1) % (BOARD_HEIGHT-3)
        posX = (posX + 1) % (BOARD_WIDTH-3)

        # rotate new_piece.

        # create a new blank board just for the falling piece.
        # NOTE: should do this every frame to clear old falling piece
        #   position.
        blank_board = empty2DArray(BOARD_HEIGHT, BOARD_WIDTH)
        display_data = empty2DArray(BOARD_HEIGHT, BOARD_WIDTH)

        # add new_piece to blank board
        for y, row in enumerate(new_piece):
           for x, data in enumerate(row):
               blank_board[posY + y][posX + x] = data


        # Output ─────────────────────────────────────────────────────────
        display_data = copy2DArray(board_data)
        # combine blank_board with board_data.
        for y, row in enumerate(display_data):
            for x, data in enumerate(row):
                if not display_data[y][x]:
                    display_data[y][x] = blank_board[y][x]
        # display board.
        for row in display_data:
            for data in row:
                if data:
                    print(data*2, end='')
                else:
                    print('..', end='')
            print()

 # Terminate ──────────────────────────────────────────────────────

    return 0  # Return 0 indicates a successful completion


# Program entry point
if __name__ == "__main__":
    main()
# ────────────────────────────────────────────────────────────────
