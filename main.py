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
from random import shuffle


# initialize curses.
stdscr = curses.initscr()
stdscr.nodelay(True)
stdscr.keypad(True)
curses.cbreak()
curses.noecho()
curses.curs_set(0)


# 2D array of strings. used a lot in this game's logic.
Matrix = list[list]

def empty_matrix(height:int, width:int):
    """return a string matrix of empty strings ('') from given height and
     width.
     """
    matrix = [
        [''] * width for _ in range(height)
    ]
    return matrix


def copy_matrix(matrix:Matrix):
    """copy the String Matrix smoothly."""
    new_matrix = [row.copy() for row in matrix]
    return new_matrix


def getTetrominoShape(tetromino_name):
    """return the shape of the tetromino, given its name"""
    tetrominoes = {
        'I': [['', '', '', ''],
              ['I', 'I', 'I', 'I'],
              ['', '', '', ''],
              ['', '', '', '']],

        'J': [['J', '', ''],
              ['J', 'J', 'J'],
              ['', '', '']],

        'L': [['', '', 'L'],
              ['L', 'L', 'L'],
              ['', '', '']],

        'O': [['', '', '', ''],
              ['', 'O', 'O', ''],
              ['', 'O', 'O', ''],
              ['', '', '', '']],

        'S': [['', 'S', 'S'],
              ['S', 'S', ''],
              ['', '', '']],

        'T': [['', 'T', ''],
              ['T', 'T', 'T'],
              ['', '', '']],

        'Z': [['Z', 'Z', ''],
              ['', 'Z', 'Z'],
              ['', '', '']],
    }
    return copy_matrix(tetrominoes[tetromino_name])


class PieceQueue:
    """represents the order in which pieces are given to player."""
    TETROMINOES = ['I', 'J', 'L', 'O', 'S', 'T', 'Z']

    def __init__(self, preview_length:int=1):
        """initialize the queue of tetrominoes."""
        self.preview_length = preview_length
        self.queue = []
        self.queue += self.generate_bag()
        self.active_piece = None

    def advance(self):
        """Move the next active piece, generate new bag if necessary."""
        if not self.get_remaining():
            self.queue += self.generate_bag()
        self.active_piece = self.queue.pop(0)

    def get_active(self):
        """return the active piece."""
        return self.active_piece

    def get_preview(self):
        """return the preview slice that will be shown to the player."""
        preview = self.queue[:self.preview_length]
        return preview

    def get_remaining(self):
        """return the pieces in the queue that exist outside the preview."""
        remaining = self.queue[self.preview_length:]
        return remaining

    def generate_bag(self):
        """generate a shuffled bag."""
        bag = self.TETROMINOES.copy()
        shuffle(bag)
        return bag


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


class GameWindow:
    """represents the curses window that the board and active piece are
    drawn to.
    """
    # set up glyphs.
    BLOCK_GLYPH = '[]'
    GLYPH_LENGTH = len(BLOCK_GLYPH)
    EMPTY_GLYPH = '-' * GLYPH_LENGTH

    def __init__(self, height:int, width:int, padding:int):
        self.height = height
        self.width = width

        # each character is twice as tall as it is wide, so the
        #   vertical padding must be cut in half to make the padding
        #   appear square.
        self.h_pad = padding * self.GLYPH_LENGTH
        self.v_pad = padding

        self.v_offset = self.v_pad // 2
        self.h_offset = self.h_pad // 2

        # create curses window.
        win_height = self.height + self.v_pad
        win_width = self.width * self.GLYPH_LENGTH + self.h_pad
        self.win = curses.newwin(win_height + 2, win_width + 2)
        self.current_data = []

    def render_data(self, screen_data:Matrix, color_pairs:dict):
        """render all screen data to game window."""
        if screen_data == self.current_data:
            return
        else:
            # safe the current screen data
            self.current_data = screen_data

            # render screen data to window, cell by cell.
            for y, row in enumerate(screen_data):
                for x, cell in enumerate(row):
                    # determine what glyph and color to use to render the cell.
                    if not cell:
                        glyph = self.EMPTY_GLYPH
                    else:
                        glyph = self.BLOCK_GLYPH
                    color = color_pairs[cell]

                    # calculate where in the window to render the glyph.
                    glyph_y = y + self.v_offset + 1
                    glyph_x = (x * self.GLYPH_LENGTH) + self.h_offset + 1

                    # render the glyph in the appropriate color.
                    self.win.addstr(glyph_y, glyph_x, glyph, color)

                # refresh window.
                self.win.refresh()


class Board(GameWindow):
    """represents current state of the board."""
    def __init__(self, height:int, width:int,
                 buffer_zone:int, padding:int):
        super().__init__(height, width, padding)
        self.buffer_zone = buffer_zone
        self.data = empty_matrix(height+buffer_zone, width)

    def getData(self):
        return copy_matrix(self.data)

    def get_playfield(self):
        """get all data outside the buffer zone, that the player can see."""
        return self.getData()[self.buffer_zone:]

    def get_buffer_zone(self):
        """get all data within the buffer zone."""
        return self.getData()[:self.buffer_zone]

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

    def clearLines(self):
        """each completed line gets cleared, then """
        line_count = 0
        for i, row in enumerate(self.data):
            is_line = bool('' not in row)
            if is_line:
                line_count += 1
                # pop completed line from data.
                self.data.pop(i)
                # clear row.
                row = ['']*self.width
                self.data.insert(0, row)
        return line_count

    def render_data(self, screen_data:Matrix, color_pairs:dict):
        super().render_data(screen_data, color_pairs)
        self.win.box()
        self.win.refresh()


class Preview(GameWindow):
    """represents the piece preview."""
    EMPTY_GLYPH = ' ' * GameWindow.GLYPH_LENGTH
    def __init__(self, height:int, width:int, padding:int):
        super().__init__(height, width, padding)

    def render_data(self, piece_name:str, color_pairs:dict):
        """render a piece in the piece preview based on its name."""
        screen_data = empty_matrix(self.height, self.width)
        piece_shape = getTetrominoShape(piece_name)
        y_offset = 4-len(piece_shape)
        x_offset = 4-len(piece_shape)
        for y, row in enumerate(piece_shape):
            for x, cell in enumerate(row):
                screen_data[y+y_offset][x+x_offset] = cell
        super().render_data(screen_data, color_pairs)
        self.win.refresh()

class ActiveTetromino:
    """class to represent the falling tetromino"""
    def __init__(self, name:str, board:Board,
                 init_y:float=0,
                 init_x:int=2):
        self.name = name
        self.board = board
        self.y = init_y
        self.x = init_x
        self.is_locked = False

        self.shape = getTetrominoShape(name)
        self.height = len(self.shape)
        self.width = len(self.shape[0])

    def getState(self):
        """returns all data needed to recreate the active piece."""
        state = (self.getName(), self.getY_float(),
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
        return copy_matrix(self.shape)

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
            new_shape = empty_matrix(self.height, self.width)
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

    def transform(self, move_y:float, move_x:int, move_r:int):
        self.y += move_y
        self.x += move_x
        self.rotate(move_r)

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
            x >= board.width or x < 0
            or y >= board.height+board.buffer_zone or y < 0
        )  # border counts as collision.
        is_overlapping = bool(cell in occupied_cells)

        # add each collision to list.
        if is_out_of_bounds or is_overlapping:
            colliding_cells.append(cell)

    return colliding_cells


class Input:
    """class used for input handling."""
    # configure keyboard controls.
    CONTROLS = {
        'Move Right': curses.KEY_RIGHT,
        'Move Left' : curses.KEY_LEFT,
        'Rotate Right': curses.KEY_UP,
        'Rotate Left': ord('z'),
        'Soft Drop' :  curses.KEY_DOWN,
        'Hard Drop' : ord(' '),
        'Hold' : ord('c'),
    }

    def __init__(self, keyboard_input):
        self.key = keyboard_input

    def getHorizontal(self):
        """Get horizontal movement from keyboard."""
        horizontal = 0
        if self.key == Input.CONTROLS['Move Right']:
           horizontal = 1
        elif self.key == Input.CONTROLS['Move Left']:
            horizontal = -1
        return horizontal

    def getVertical(self):
        """Get vertical movement from keyboard."""
        vertical = 0
        if self.key == Input.CONTROLS['Soft Drop']:
            vertical = 1
        return vertical

    def getRotational(self):
        """get piece rotation from keyboard."""
        rotation = 0
        if self.key == Input.CONTROLS['Rotate Right']:
            rotation = 1
        if self.key == Input.CONTROLS['Rotate Left']:
            rotation = -1
        return rotation


class PlayerData:
    """keep track of score, level, speed, etc."""
    level = 1
    lines_cleared = 0
    score = 0
    speed = 0


def center_window(outer_win: curses.window,
                  inner_win:curses.window):
    """center a window within another window."""
    outer_height, outer_width = outer_win.getmaxyx()
    inner_height, inner_width = inner_win.getmaxyx()

    center_y = outer_height//2 - inner_height//2
    center_x = outer_width//2 - inner_width//2

    inner_win.mvwin(center_y, center_x)


def main(stdscr : curses.window):
    # Initialize ─────────────────────────────────────────────────────
    # set up all curses color pairs.
    curses.start_color()

    COLOR_BACKGROUND = curses.COLOR_BLACK

    # create a dictionary of all tetromino's and their colors.
    TETROMINO_COLORS = {
        'I' : 14,
        'J' : 63,
        'L' : 214,
        'O' : 228,
        'S' : 119,
        'T' : 207,
        'Z' : 196,
        ''  : 236
    }

    # initialize tetromino color pairs.
    COLOR_PAIRS = {}
    for pair_number, (name, color) in enumerate(
            TETROMINO_COLORS.items(), start=1):
        curses.init_pair(pair_number, color, COLOR_BACKGROUND)
        COLOR_PAIRS[name] = curses.color_pair(pair_number)

    # setup grayscale colors (when you lose)
    GRAYSCALE_COLORS = {
        'I' : 248,
        'J' : 243,
        'L' : 248,
        'O' : 255,
        'S' : 248,
        'T' : 248,
        'Z' : 251,
    }

    GRAYSCALE_PAIRS = {'' : COLOR_PAIRS['']}
    for pair_number, (name, color) in enumerate(
            GRAYSCALE_COLORS.items(),
            start=len(COLOR_PAIRS) + 1):
        curses.init_pair(pair_number, color, COLOR_BACKGROUND)
        GRAYSCALE_PAIRS[name] = curses.color_pair(pair_number)

    # board setup
    BOARD_HEIGHT = 20
    BOARD_WIDTH = 10
    BUFFER_ZONE = 20
    BOARD_PADDING = 0
    board = Board(BOARD_HEIGHT, BOARD_WIDTH, BUFFER_ZONE, BOARD_PADDING)

    # piece preview setup.
    PREVIEW_HEIGHT = 4
    PREVIEW_WIDTH = 5
    PREVIEW_COUNT = 5

    previews = []
    for i in range(PREVIEW_COUNT):
        preview = Preview(PREVIEW_HEIGHT, PREVIEW_WIDTH, 0)
        preview.win.mvwin(i * PREVIEW_HEIGHT,
                          board.win.getmaxyx()[1] + 2)
        previews.append(preview)

    # initialize piece queue.
    piece_queue = PieceQueue(PREVIEW_COUNT)

    # begin gameplay loop.
    running = True
    old_screen_data = None # initialize old screen data. (for drawing output)
    lines_cleared = 0
    level = 1
    while running:
        # advance the piece queue.
        piece_queue.advance()

        # render piece preview.
        for i in range(PREVIEW_COUNT):
            piece = piece_queue.get_preview()[i]
            previews[i].render_data(piece, COLOR_PAIRS)


        # get the active tetromino from the queue, instantiate it.
        active_tetromino = ActiveTetromino(
            piece_queue.get_active(),
            board, BUFFER_ZONE-2)

        # determine which level the player is on.
        line_thresh = 10
        if lines_cleared >= line_thresh:
            level += 1
            lines_cleared = line_thresh-lines_cleared

        # determine gravity based on level.
        gravity = getGravity(level)

        # initialize lock timer.
        lock_timer = 0
        # loop until tetromino gets locked down.
        while not active_tetromino.is_locked:
            start = time.time() # begin a timer.

            # Input ──────────────────────────────────────────────────────────
            # get the keyboard input from the player.
            key_pressed = stdscr.getch()
            player_input = Input(key_pressed)

            # Process ────────────────────────────────────────────────────────
            # quit the game if player presses 'q'.
            if key_pressed == ord('q'): quit()

            # determine the player's horizontal and rotational movements.
            move_x = player_input.getHorizontal()
            move_r = player_input.getRotational()

            # determine player's vertical movements.
            move_y = player_input.getVertical()
            if not move_y: move_y = gravity

            # try each movement individually, get collisions.
            active_tetromino.x += move_x
            x_collisions = getCollidingCells(active_tetromino, board)
            if x_collisions:
                active_tetromino.x -= move_x

            active_tetromino.rotate(move_r)
            r_collisions = getCollidingCells(active_tetromino, board)
            if r_collisions:
                active_tetromino.rotate(-move_r)

            active_tetromino.y += move_y
            y_collisions = getCollidingCells(active_tetromino, board)
            if y_collisions:
                active_tetromino.y -= move_y

            # determine how much the piece is locked down.
            if y_collisions:
                # reset the lock timer if the piece rotates or moves laterally.
                if move_x or move_r:
                    lock_timer = 0
                elif move_y:
                    # increase lock timer by 2 if player is pressing down.
                    lock_timer += 2
                else:
                    lock_timer += 1

            # lock the piece if the lock timer exceeds 5.
            if lock_timer >= 5:
                active_tetromino.is_locked = True

            # prepare to draw all board data and the active tetromino to the
            # screen.
            screen_data = board.get_playfield()
            for (y, x) in active_tetromino.getOccupiedCells():
                if y >= BUFFER_ZONE: # only render if piece is in buffer zone.
                    screen_data[y-BUFFER_ZONE][x] = active_tetromino.getName()

            # Output ────────────────────────────────────────────────────────
            # only redraw the board if there is a difference in the output.
            if screen_data != old_screen_data:
                board.render_data(screen_data, COLOR_PAIRS)
            old_screen_data = screen_data

            # keep frame rate at roughly 60fps.
            sleep_time = 1/60 - (time.time()-start)
            if sleep_time > 0:
                time.sleep(sleep_time)

        # save tetromino to board data and clear any lines created.
        board.addTetromino(active_tetromino)
        lines_cleared += board.clearLines()

        # re-render the playfield with new info.
        board.render_data(board.get_playfield(), COLOR_PAIRS)

        # detect top-out (game over).
        buffer_zone = board.get_buffer_zone()
        for row in buffer_zone:
            for cell in row:
                if cell:
                    running = False
                    # make everything grayscale.
                    screen_data = board.get_playfield()
                    board.render_data(screen_data, GRAYSCALE_PAIRS)
                    for i in range(PREVIEW_COUNT):
                        piece = piece_queue.get_preview()[i]
                        previews[i].render_data(piece, GRAYSCALE_PAIRS)

    # Terminate ──────────────────────────────────────────────────────
    # wait for user to quit a final time before quitting.
    key_pressed = stdscr.getch()
    while key_pressed != ord('q'):
        key_pressed = stdscr.getch()

    return 0  # Return 0 indicates a successful completion


# Program entry point
if __name__ == "__main__":
    wrapper(main)
