# ┌──────────────────────────────────────────────────────────────────┐
# │ Title:    TETRIS                                                 │
# │ Author:   Charlie Wensink                                        │
# │ Date:     May 25, 2026                                           │
# │ Purpose:  learn how to make tetris                               │
# └──────────────────────────────────────────────────────────────────┘

# initialize curses.
import curses
from curses import wrapper
stdscr = curses.initscr()


def main(stdscr : curses.window):
    # Initialize ─────────────────────────────────────────────────────
    # initialize colors.
    curses.start_color()
    if curses.COLORS < 8:
        CYAN = curses.COLOR_WHITE
        BLUE = curses.COLOR_WHITE
        YELLOW = curses.COLOR_WHITE
        PINK = curses.COLOR_WHITE
        RED = curses.COLOR_WHITE
        GREEN = curses.COLOR_WHITE
        ORANGE = curses.COLOR_WHITE
    elif curses.COLORS < 256:
        CYAN = curses.COLOR_CYAN
        BLUE = curses.COLOR_BLUE
        YELLOW = curses.COLOR_YELLOW
        PINK = curses.COLOR_MAGENTA
        RED = curses.COLOR_RED
        GREEN = curses.COLOR_GREEN
        ORANGE = curses.COLOR_RED
    else:
        CYAN = 14
        BLUE = 63
        YELLOW = 228
        PINK = 207
        RED = 196
        GREEN = 119
        ORANGE = 214
    TETRIS_COLORS = (CYAN, BLUE, YELLOW, PINK,
                    RED, GREEN, ORANGE)
    for i, color in enumerate(TETRIS_COLORS):
        curses.init_pair(i+1, color, curses.COLOR_BLACK)
    COLOR_PAIRS = {
        'I' : curses.color_pair(1),
        'J': curses.color_pair(2),
        'O': curses.color_pair(3),
        'T': curses.color_pair(4),
        'Z': curses.color_pair(5),
        'S': curses.color_pair(6),
        'L': curses.color_pair(7),
    }

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
    # TODO put this drawing the board stuff in its own method.
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

    # wait for user to press 'q' to escape.
    keyboard_input = stdscr.getkey()
    while keyboard_input != 'q':
        keyboard_input = stdscr.getkey()

    # Terminate ──────────────────────────────────────────────────────

    return 0  # Return 0 indicates a successful completion


# Program entry point
if __name__ == "__main__":
    wrapper(main)
