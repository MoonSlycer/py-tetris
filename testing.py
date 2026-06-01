# ┌──────────────────────────────────────────────────────────────────┐
# │ Title:    testing                                                │
# │ Author:   Charlie Wensink                                        │
# │ Date:     May 31, 2026                                           │
# │ Purpose:  test main gameplay logic without curses.               │
# └──────────────────────────────────────────────────────────────────┘

# 2D array of strings. used a lot in this game's logic.
Matrix = list[list]

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
    return copyStringMatrix(tetrominos[tetromino_name])

class Board:
    """represents current state of the board."""
    def __init__(self, height:int, width:int, active_tetromino:ActiveTetromino=None):
        self.height = height
        self.width = width
        self.data = emptyStringMatrix(height, width)
        self.active_tetromino = active_tetromino

    def getData(self):
        return copyStringMatrix(self.data)

    def getOccupiedPositions(self):
        """get all occupied positions on the board."""
        occupied_positions = []
        for y, row in enumerate(self.getData()):
            for x, cell in enumerate(row):
                if cell:
                    occupied_positions.append((y,x))
        return occupied_positions

    def detectCollisions(self, active_tetromino:ActiveTetromino):
        """given an active tetromino, return all points of collision."""
        block_positions = active_tetromino.getBlockPositions()
        occupied_positions = self.getOccupiedPositions()
        collisions = []
        for (y,x) in block_positions:
            test_position = (y,x)
            is_out_of_bounds = bool(
                y >= self.height or y < 0
                or x >= self.width or x < 0
            )
            is_colliding = bool(test_position in occupied_positions)
            if is_out_of_bounds or is_colliding:
                collisions.append(test_position)

        return collisions


class ActiveTetromino:
    """class to represent the falling tetromino"""
    def __init__(self, name:str, init_y:int, init_x:int):
        self.name = name
        self.y = init_y
        self.x = init_x
        self.shape = getTetrominoShape(name)
        self.height = len(self.shape)
        self.width = len(self.shape[0])

    def getName(self):
        return self.name

    def getShape(self):
        return copyStringMatrix(self.shape)

    def setShape(self, new_shape:Matrix):
        self.shape = new_shape

    def getY(self):
        return self.y

    def getX(self):
        return self.x

    def getBlockPositions(self):
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
            new_shape = emptyStringMatrix(self.height, self.width)
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

    def getDesiredState(self, move_y:int, move_x:int,
                        rotate_dir:int):
        """return a copy of self with the given transformations applied."""
        transformed_copy = ActiveTetromino(
            self.name, self.getY(), self.getX())
        transformed_copy.setShape(self.getShape())

        # perform transformations.
        transformed_copy.move(move_y, move_x)
        transformed_copy.rotate(rotate_dir)
        return transformed_copy


def emptyStringMatrix(height:int, width:int):
    """return a string matrix of empty strings ('') from given height and
     width.
     """
    matrix = [
        [''] * width for _ in range(height)
    ]
    return matrix


def copyStringMatrix(matrix:Matrix):
    """copy the String Matrix smoothly."""
    new_matrix = [row.copy() for row in matrix]
    return new_matrix


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
    active_tetromino = ActiveTetromino('T', 0, 2)
    while keyboard_input != 'q':
        # Input ──────────────────────────────────────────────────────────
        # get user input.
        keyboard_input = input()

        # Process ────────────────────────────────────────────────────────
        #interpret key presses as velocities applied to tetromino.
        y_velocity = 0 # always falling.
        x_velocity = 0
        rotation = 0
        # initialize keyboard controls.
        RIGHT = 'l'
        LEFT = 'j'
        DOWN = 'k'
        CLOCKWISE = 'x'
        COUNTER_CLOCKWISE = 'z'
        controls = {RIGHT, LEFT, DOWN,
                    CLOCKWISE, COUNTER_CLOCKWISE}

        match keyboard_input:
            case 'l' : x_velocity = 1
            case 'j' : x_velocity = -1
            case 'x' :  rotation = 1

        # apply player movements.
        # attempt to transform tetromino, cancel move if there is a collision.
        desired_state = (
            active_tetromino.getDesiredState(
                y_velocity, x_velocity, rotation))
        if not board.detectCollisions(desired_state):
            active_tetromino = desired_state

        # make tetromino fall, if possible.
        desired_state = active_tetromino.getDesiredState(1,0,0)
        if not board.detectCollisions(desired_state):
            active_tetromino = desired_state

        # Output ─────────────────────────────────────────────────────────
        # display falling block.
        display_data = copyStringMatrix(board.getData())
        for (block_y, block_x) in active_tetromino.getBlockPositions():
            display_data[block_y][block_x] = active_tetromino.getName()

        # display board.
        for row in display_data:
            for data in row:
                if data:
                    print(data*2, end='')
                else:
                    print('..', end='')
            print()
        # display controls.
        print('controls:')
        print(f'{RIGHT} - RIGHT')
        print(f'{LEFT} - LEFT')
        print(f'{CLOCKWISE} - CLOCKWISE')
        print('Q - QUIT')

# Terminate ──────────────────────────────────────────────────────

    return 0  # Return 0 indicates a successful completion


# Program entry point
if __name__ == "__main__":
    main()
# ────────────────────────────────────────────────────────────────
