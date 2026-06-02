# ┌──────────────────────────────────────────────────────────────────┐
# │ Title:    testing                                                │
# │ Author:   Charlie Wensink                                        │
# │ Date:     May 31, 2026                                           │
# │ Purpose:  test main gameplay logic without curses.               │
# └──────────────────────────────────────────────────────────────────┘

# 2D array of strings. used a lot in this game's logic.
Matrix = list[list]


def emptyMatrix(height:int, width:int):
    """return a string matrix of empty strings ('') from given height and
     width.
     """
    matrix = [
        [''] * width for _ in range(height)
    ]
    return matrix


def copyMatrix(matrix:Matrix):
    """copy the String Matrix smoothly."""
    new_matrix = [row.copy() for row in matrix]
    return new_matrix


def getTetrominoShape(tetromino_name):
    """return the shape of the tetromino, given its name"""
    tetrominos = {
        'I': [[0, 0, 0, 0],
              [1, 1, 1, 1],
              [0, 0, 0, 0],
              [0, 0, 0, 0]],

        'J': [[1, 0, 0],
              [1, 1, 1],
              [0, 0, 0]],

        'L': [[0, 0, 1],
              [1, 1, 1],
              [0, 0, 0]],

        'O': [[0, 0, 0, 0],
              [0, 1, 1, 0],
              [0, 1, 1, 0],
              [0, 0, 0, 0]],

        'S': [[0, 1, 1],
              [1, 1, 0],
              [0, 0, 0]],

        'T': [[0, 1, 0],
              [1, 1, 1],
              [0, 0, 0]],

        'Z': [[1, 1, 0],
              [0, 1, 1],
              [0, 0, 0]],
    }
    return copyMatrix(tetrominos[tetromino_name])


class Board:
    """represents current state of the board."""
    def __init__(self, height:int, width:int):
        self.height = height
        self.width = width
        self.data = emptyMatrix(height, width)

    def getData(self):
        return copyMatrix(self.data)

    def getOccupiedCells(self):
        """get all occupied positions on the board."""
        occupied_cells = []
        for y, row in enumerate(self.getData()):
            for x, cell in enumerate(row):
                if cell:
                    occupied_cells.append((y,x))
        return occupied_cells


class ActiveTetromino:
    """class to represent the falling tetromino"""
    def __init__(self, name:str, board:Board, init_y:int=0, init_x:int=2):
        self.name = name
        self.board = board
        self.y = init_y
        self.x = init_x

        self.shape = getTetrominoShape(name)
        self.height = len(self.shape)
        self.width = len(self.shape[0])

    def getState(self):
        """returns all data needed to recreate the active piece."""
        state = (self.getName(), self.getY(),
                 self.getX(), self.getShape())
        return state

    def setState(self, state:tuple):
        """accepts the output of the getState method to revert back to an old
        state.
        """
        self.name = state[0]
        self.y = state[1]
        self.x = state[2]
        self.shape = state[3]

    def getName(self):
        return self.name

    def getShape(self):
        return copyMatrix(self.shape)

    def setShape(self, new_shape:Matrix):
        self.shape = new_shape

    def getY(self):
        return self.y

    def getX(self):
        return self.x

    def getOccupiedCells(self):
        """Return the board position of each occupied cell in the
        tetromino's shape.
        """
        positions = []
        for cell_y, row in enumerate(self.shape):
            for cell_x, cell in enumerate(row):
                if cell:
                    # append the global board position of each occupied cell in
                    # tetromino.
                    positions.append(
                        (self.y + cell_y, self.x + cell_x)
                    )
        return positions

    def rotate(self, direction:int):
        """rotate self.shape 90 degrees in specified direction."""
        if not (direction in {-1, 1}):
            new_shape = self.getShape()
        else:
            new_shape = emptyMatrix(self.height, self.width)
            max_y = self.height - 1
            max_x = self.width - 1
            for y, row in enumerate(self.shape):
                for x, cell in enumerate(row):
                    if direction > 0:  # clockwise rotation, 90 degrees.
                        new_shape[x][max_x - y] = cell
                    elif direction < 0:  # counter-clockwise rotation, 90 degrees.
                        new_shape[max_y - x][y] = cell
        self.setShape(new_shape)
        return new_shape

    def move(self, move_y:int, move_x:int):
        """move self in specified direction."""
        self.y += move_y
        self.x += move_x

    def tryTransform(self, move_y:int, move_x:int,
                        rotate_dir:int):
        """attempt to transform the active tetromino."""
        # make a copy of active tetromino's state.
        previous_state = self.getState()

        # perform transformations.
        self.move(move_y, move_x)
        self.rotate(rotate_dir)

        # check collisions.
        colliding_cells =  getCollidingCells(self, self.board)

        # undo transformation if collisions occur.
        if colliding_cells:
            self.setState(previous_state)
            return colliding_cells
        else: return None


def getCollidingCells(tetromino: ActiveTetromino, board: Board):
    """given an active tetromino and the board, return all points
    of overlap."""
    # get every space occupied by the active tetromino.
    tetromino_cells = tetromino.getOccupiedCells()
    occupied_cells = board.getOccupiedCells()

    colliding_cells = []
    for (y, x) in tetromino_cells:
        cell = (y, x)
        # check if tetromino is out of bounds or
        # overlapping other blocks.
        is_out_of_bounds = bool(
            y >= board.height or y < 0
            or x >= board.width or x < 0
        )  # border counts as collision.
        is_overlapping = bool(cell in occupied_cells)

        # add each collision to list.
        if is_out_of_bounds or is_overlapping:
            colliding_cells.append(cell)

    return colliding_cells


def main():
    # Initialize ─────────────────────────────────────────────────────
    # board setup.
    BOARD_HEIGHT = 20
    BOARD_WIDTH = 10
    board = Board(BOARD_HEIGHT, BOARD_WIDTH)

    # DEBUGGING ONLY -- place blocks on board already.
    board.data[17:] = [
        ['L', 'L', 'L', '', '', '', '', '', '', ''],
        ['L', 'S', 'S', 'T', '', '', 'Z', 'Z', '', ''],
        ['S', 'S', 'T', 'T', 'T', '', '', 'Z', 'Z', '']]

    keyboard_input = ''
    active_tetromino = ActiveTetromino('T', board)
    gravity = 1
    while keyboard_input != 'q':
        # Input ──────────────────────────────────────────────────────────
        # get user input.
        keyboard_input = input()

        # Process ────────────────────────────────────────────────────────
        # Apply user's movement to active tetromino.
        move_y = 0
        move_x = 0
        rotation = 0
        match keyboard_input:
            case 'l' : move_x += 1
            case 'j' : move_x += -1
            case 'x' :  rotation += 1
        active_tetromino.tryTransform(move_y, move_x, rotation)

        # apply gravity to active tetromino.
        active_tetromino.tryTransform(gravity, 0, 0)

        # prepare to draw all board data and the active tetromino to the
        # screen.
        screen_data = copyMatrix(board.getData())
        for (y, x) in active_tetromino.getOccupiedCells():
            screen_data[y][x] = active_tetromino.getName()
        # Output ─────────────────────────────────────────────────────────
        # display screen data.
        for row in screen_data:
            for cell in row:
                if cell:
                    print([]*2, end='')
                else:
                    print('..', end='')
            print()

# Terminate ──────────────────────────────────────────────────────

    return 0  # Return 0 indicates a successful completion


# Program entry point
if __name__ == "__main__":
    main()
# ────────────────────────────────────────────────────────────────
