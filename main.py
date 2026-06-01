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

# initialize curses.
stdscr = curses.initscr()
stdscr.nodelay(True)
curses.cbreak()
curses.noecho()


def empty2DArray(height, width):
    """return a 2d array of empty strings ('') from given height and
     width.
     """
    array_out = [
        [''] * width for _ in range(height)
    ]

    return array_out


def rotateRight(tetromino_in):
    """Return a 2D array representing the given tetromino, rotated 90
    degrees clockwise.
    """
    # get height and width of tetromino's bounding box.
    height = len(tetromino_in)-1
    width = len(tetromino_in[0])-1

    # initialize tetromino_out (blank 2D array using width and height).
    tetromino_out = [
        [''] * width for _ in range(height)
    ]

    # calculate the rotated tetromino.
    for y in range(height):
        for x in range(width):
            tetromino_out[x][width-y] = tetromino_in[y][x]

    return tetromino_out


def getHorizontalMovement():
    """return integer from -1 to 1 representing left or right keyboard
     direction.
     """
    KEY_LEFT = 260
    KEY_RIGHT = 261
    KEY_D = 100
    KEY_A = 97
    KEY_SPACE = 32 #TODO REMOVE
    KEY_Z = 122 #TODO REMOVE

    keyboard_input = stdscr.getch()
    if keyboard_input in {KEY_RIGHT, KEY_D}:
        movement = 1
    elif keyboard_input in {KEY_LEFT, KEY_A}:
        movement = -1
    else:
        movement = 0

    return movement


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

    # board setup.
    BLOCK_GLYPH = '[]'
    GLYPH_LENGTH = len(BLOCK_GLYPH)
    EMPTY_GLYPH = '.' * GLYPH_LENGTH

    BOARD_HEIGHT = 20
    BOARD_WIDTH = 10
    BOARD_PADDING = 8

    board_win = curses.newwin(
        BOARD_HEIGHT + BOARD_PADDING//2,
        BOARD_WIDTH * GLYPH_LENGTH + BOARD_PADDING,
        3, 3
    )

    # create a 2d list, board_data using height and width.
    board_data = [
       [''] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)
    ]
    # Input ──────────────────────────────────────────────────────────

    # Process ────────────────────────────────────────────────────────
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
    # Output ─────────────────────────────────────────────────────────
    keyboard_input = stdscr.getch()
    while keyboard_input != ord('q'):
        # get keyboard input.
        keyboard_input = stdscr.getch()

        # TODO: REMOVE: DEBUG PRINT KEYBOARD INPUT
        stdscr.clear()
        stdscr.addstr(10,50,str(keyboard_input))
        stdscr.refresh()

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
        for y, row in enumerate(board_data):
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
        time.sleep(0.1)
    # Terminate ──────────────────────────────────────────────────────

    return 0  # Return 0 indicates a successful completion


# Program entry point
if __name__ == "__main__":
    wrapper(main)
