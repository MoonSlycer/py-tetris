# ┌──────────────────────────────────────────────────────────────────┐
# │ Title:    TETRIS                                                 │
# │ Author:   Charlie Wensink                                        │
# │ Date:     May 25, 2026                                           │
# │ Purpose:  Remake Tetris using the curses library for coding      │
# │           practice.                                              │
# └──────────────────────────────────────────────────────────────────┘

import curses
from curses import wrapper
import time
from random import randrange

# initialize curses.
stdscr = curses.initscr()
stdscr.nodelay(True)
stdscr.keypad(True)
curses.cbreak()
curses.noecho()
curses.curs_set(0)


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


def getGravity(current_level):
    """calculate how fast pieces should fall, given the current level."""
    # source: https://tetris.wiki/Marathon
    speed_curve = {
        1 : 0.01667,
        2 : 0.021017,
        3 : 0.026977,
        4 : 0.035256,
        5 : 0.04693,
        6 : 0.06361,
        7 : 0.0879,
        8 : 0.1236,
        9 : 0.1775,
        10 : 0.2598,
        11 : 0.388,
        12 : 0.59,
        13 : 0.92,
        14 : 1.46,
        15 : 2.36,
        16 : 3.91,
        17 : 6.61,
        18 : 11.43,
        19 : 20.23,
        20 : 36.6
    }
    return speed_curve[current_level]


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

    def addTetromino(self, piece:ActiveTetromino):
        """add locked tetromino to board data."""
        for (y, x) in piece.getOccupiedCells():
            self.data[y][x] = piece.getName()


class ActiveTetromino:
    """class to represent the falling tetromino"""
    def __init__(self, name:str, board:Board,
                 init_y:float=0,
                 init_x:int=2):
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

    def getY_float(self):
        return self.y
    def getY(self):
        return int(self.y.__ceil__())

    def getX(self):
        return self.x

    def getOccupiedCells(self):
        """Return the board position of each occupied cell in the
        tetromino's shape.
        """
        positions = []
        for cell_y, row in enumerate(self.getShape()):
            for cell_x, cell in enumerate(row):
                if cell:
                    # append the global board position of each occupied cell in
                    # tetromino.
                    positions.append(
                        (self.getY() + cell_y, self.getX() + cell_x)
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

    def move(self, move_y:float, move_x:int):
        """move self in specified direction."""
        self.y += move_y
        self.x += move_x

    def tryTransform(self, move_y:float, move_x:int,
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


def getTransformation(keyboard_input):
    """Get the direction of movement and rotation from keyboard input."""
    vertical = 0
    horizontal = 0
    rotation = 0

    if keyboard_input in (curses.KEY_RIGHT, ord('d')):  # MOVE RIGHT
        horizontal = 1

    elif keyboard_input in (curses.KEY_LEFT, ord('a')):  # MOVE LEFT
        horizontal = -1

    elif keyboard_input in (curses.KEY_DOWN, ord('s')):  # MOVE DOWN
        vertical = 1

    elif keyboard_input == ord('x'):  # ROTATE CLOCKWISE
        rotation = 1

    elif keyboard_input == ord('z'):  # ROTATE COUNTER-CLOCKWISE
        rotation = -1
    return vertical, horizontal, rotation


def main(stdscr : curses.window):
    # Initialize ─────────────────────────────────────────────────────
    # set up all curses color pairs.
    curses.start_color()

    # define the colors for each tetromino (256-color terminal).
    COLOR_I = 14
    COLOR_J = 63
    COLOR_L = 214
    COLOR_O = 228
    COLOR_S = 119
    COLOR_T = 207
    COLOR_Z = 196

    # alter colors depending on terminal capabilities.
    if curses.COLORS < 8:
        COLOR_I = curses.COLOR_WHITE
        COLOR_J = curses.COLOR_WHITE
        COLOR_L = curses.COLOR_WHITE
        COLOR_O = curses.COLOR_WHITE
        COLOR_S = curses.COLOR_WHITE
        COLOR_T = curses.COLOR_WHITE
        COLOR_Z = curses.COLOR_WHITE
    elif curses.COLORS < 256:
        COLOR_I = curses.COLOR_CYAN
        COLOR_J = curses.COLOR_BLUE
        COLOR_L = curses.COLOR_RED
        COLOR_O = curses.COLOR_YELLOW
        COLOR_S = curses.COLOR_GREEN
        COLOR_T = curses.COLOR_MAGENTA
        COLOR_Z = curses.COLOR_RED

    # create a dictionary of all tetromino's and their colors.
    TETROMINO_COLORS = {
        'I' : COLOR_I,
        'J' : COLOR_J,
        'L' : COLOR_L,
        'O' : COLOR_O,
        'S' : COLOR_S,
        'T' : COLOR_T,
        'Z' : COLOR_Z
    }

    # initialize color pairs.
    COLOR_PAIRS = {}
    for pair_number, (tetromino, color) in enumerate(
            TETROMINO_COLORS.items(), start=1):
        curses.init_pair(pair_number, color, curses.COLOR_BLACK)
        COLOR_PAIRS[tetromino] = curses.color_pair(pair_number)

    # board setup.
    BLOCK_GLYPH = '[]'
    GLYPH_LENGTH = len(BLOCK_GLYPH)
    EMPTY_GLYPH = '.' * GLYPH_LENGTH

    BOARD_HEIGHT = 20
    BOARD_WIDTH = 10
    BOARD_PADDING = 8

    # create board
    board = Board(BOARD_HEIGHT, BOARD_WIDTH)

    # setup curses board window.
    board_win = curses.newwin(
        BOARD_HEIGHT + BOARD_PADDING//2,
        BOARD_WIDTH * GLYPH_LENGTH + BOARD_PADDING,
        3, 3
    )
    # DEBUGGING ONLY -- place blocks on board already.
    # board.data[17:] = [
    #     ['L', 'L', 'L', '', '', '', '', '', '', ''],
    #     ['L', 'S', 'S', 'T', '', '', 'Z', 'Z', '', ''],
    #     ['S', 'S', 'T', 'T', 'T', '', '', 'Z', 'Z', '']]

    # initialize an active T tetromino.
    active_tetromino = ActiveTetromino('T', board)

    # get gravity.
    gravity = getGravity(1)

    # amount of frames of downward collision or movement before locking.
    locked = False

    old_screen_data = None
    keyboard_input = stdscr.getch()
    while keyboard_input != ord('q'):
        # Input ──────────────────────────────────────────────────────────
        # get keyboard input.
        keyboard_input = stdscr.getch()

        # Process ────────────────────────────────────────────────────────
        if locked:
            # save tetromino to board.
            board.addTetromino(active_tetromino)

            # pick a random new tetromino.
            new_tetromino = ('I','J','L','O','S','T','Z')[randrange(7)]
            active_tetromino = ActiveTetromino(new_tetromino,board)
            locked = False
        else:
            # turn player's input into a movement.
            movement = getTransformation(keyboard_input)

            # apply player movement to tetromino.
            movement_collisions = active_tetromino.tryTransform(*movement)

            # apply gravity to tetromino.
            gravity_collisions = active_tetromino.tryTransform(gravity, 0, 0)

            # lock piece if a collision is detected.
            if gravity_collisions:
                locked = True

        # prepare to draw all board data and the active tetromino to the
        # screen.
        screen_data = copyMatrix(board.getData())
        for (y, x) in active_tetromino.getOccupiedCells():
            screen_data[y][x] = active_tetromino.getName()

        # determine if screen data has changed since last time.
        screen_changed = bool(screen_data != old_screen_data)

        # Output ─────────────────────────────────────────────────────────
        # only refresh the board if the data changed.
        if screen_changed:
            # clear board.
            board_win.clear()

            # draw board.
            board_win.border()
            h_shift = BOARD_PADDING//2
            v_shift = BOARD_PADDING//4

            # draw column markers.
            for i in range(BOARD_WIDTH):
                column_number = str(i).ljust(2)
                i = i*len(BLOCK_GLYPH)
                board_win.addstr(0, i+h_shift, column_number)

            # draw row markers.
            for i in range(BOARD_HEIGHT):
                row_number = str(i).ljust(2)
                board_win.addstr(i+v_shift, 0, row_number)

            # display current game state.
            for y, row in enumerate(screen_data):
                for x, color in enumerate(row):
                    x = x * GLYPH_LENGTH
                    if not color:
                        board_win.addstr(y + v_shift, x + h_shift,
                                         EMPTY_GLYPH)
                    else:
                        board_win.addstr(y + v_shift, x + h_shift,
                                         BLOCK_GLYPH,
                                         COLOR_PAIRS[color])
            board_win.refresh()
        old_screen_data = screen_data
        time.sleep(0.01)
    # Terminate ──────────────────────────────────────────────────────

    return 0  # Return 0 indicates a successful completion


# Program entry point
if __name__ == "__main__":
    wrapper(main)
