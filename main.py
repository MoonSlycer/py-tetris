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


def paste_matrix(added_matrix:Matrix, base_matrix:Matrix,
                 y_offset=0, x_offset=0):
    """paste one matrix on top of another."""
    for y, row in enumerate(added_matrix):
        for x, cell in enumerate(row):
            base_matrix[y_offset + y][x_offset + x] = cell


class GameSettings:
    """defines the player's current game configuration."""
    # Gameplay
    CONTROLS = {
        'Move Right': curses.KEY_RIGHT,
        'Move Left' : curses.KEY_LEFT,
        'Rotate Right': curses.KEY_UP,
        'Rotate Left': ord('z'),
        'Soft Drop' :  curses.KEY_DOWN,
        'Hard Drop' : ord(' '),
        'Hold' : ord('c'),
    }
    LINE_THRESHOLD = 10
    STARTING_LEVEL = 1
    GRAVITY_TABLE = {
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


    # Graphics
    COLOR_BACKGROUND = curses.COLOR_BLACK
    PIECE_COLORS = {
        'I' : 14,
        'J' : 63,
        'L' : 214,
        'O' : 228,
        'S' : 119,
        'T' : 207,
        'Z' : 196,
        ''  : 236
    }
    BLOCK_GLYPH = '[]' # TODO
    EMPTY_GLYPH = '.' * len(BLOCK_GLYPH) # TODO


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

    def get_current(self):
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
        self.current_colors = {}

    def render_data(self, screen_data:Matrix, color_pairs:dict):
        """render all screen data to game window."""
        if (screen_data == self.current_data and
                color_pairs == self.current_colors):
            return
        else:
            # safe the current screen data
            self.current_data = screen_data
            self.current_colors = color_pairs

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


class Preview:
    """generates the column of future pieces to the right of the board."""
    def __init__(self, disp_height, disp_width, display_count, x):
        self.displays = []
        for i in range(display_count):
            display = PieceDisplay(disp_height, disp_width, 0)
            display.win.mvwin(i * disp_height, x)
            self.displays.append(display)

    def render_preview(self, preview:list, color_pairs:dict):
        """render the given preview using the given colors."""
        for i, display in enumerate(self.displays):
            display:PieceDisplay
            display.render_data(preview[i],color_pairs)


class PieceDisplay(GameWindow):
    """a window containing a single piece's graphics; used for showing the
    held piece and piece preview.
    """
    EMPTY_GLYPH = ' ' * GameWindow.GLYPH_LENGTH
    def __init__(self, height:int, width:int, padding:int):
        super().__init__(height, width, padding)

    def render_data(self, piece_name:str, color_pairs:dict):
        """render a piece in the piece preview based on its name."""
        piece_shape = getTetrominoShape(piece_name)

        # remove all empty rows from piece shape.
        empty_row = ['']*len(piece_shape)
        while empty_row in piece_shape:
            piece_shape.remove(empty_row)

        # put the piece shape into the correct sized screen.
        screen_data = empty_matrix(self.height, self.width)
        paste_matrix(piece_shape, screen_data)

        super().render_data(screen_data, color_pairs)


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
    controls = GameSettings.CONTROLS

    def __init__(self, keyboard_input):
        self.key = keyboard_input

    def getHorizontal(self):
        """Get horizontal movement from keyboard."""
        horizontal = 0
        if self.key == Input.controls['Move Right']:
           horizontal = 1
        elif self.key == Input.controls['Move Left']:
            horizontal = -1
        return horizontal

    def getVertical(self):
        """Get vertical movement from keyboard."""
        vertical = 0
        if self.key == Input.controls['Soft Drop']:
            vertical = 1
        return vertical

    def getRotational(self):
        """get piece rotation from keyboard."""
        rotation = 0
        if self.key == Input.controls['Rotate Right']:
            rotation = 1
        if self.key == Input.controls['Rotate Left']:
            rotation = -1
        return rotation


class PlayerStats:
    """keep track of score, level, speed, etc."""
    def __init__(self):
        self.level = GameSettings.STARTING_LEVEL

        self.line_thresh = GameSettings.LINE_THRESHOLD
        self.total_lines = 0
        self.level_lines = 0 # lines cleared since last level-up

        self.score = 0
        self.speed = GameSettings.GRAVITY_TABLE[self.level]


    def update_stats(self, lines_cleared:int=0):
        """update all player stats, given the number of lines cleared."""
        self.level_lines += lines_cleared
        self.total_lines += lines_cleared

        # update player's level.
        if self.level_lines >= self.line_thresh:
            self.level += 1
            self.level_lines = self.level_lines % self.line_thresh

        # update player's speed.
        self.speed = GameSettings.GRAVITY_TABLE[self.level]

        # TODO: update player's score.


def main(stdscr : curses.window):
    # Initialize ─────────────────────────────────────────────────────
    curses.start_color()

    piece_colors = GameSettings.PIECE_COLORS
    color_background = GameSettings.COLOR_BACKGROUND

    COLOR_PAIRS = {}
    for pair_number, (name, color) in enumerate(
            piece_colors.items(), start=1):
        curses.init_pair(pair_number, color, color_background)
        COLOR_PAIRS[name] = curses.color_pair(pair_number)

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
        curses.init_pair(pair_number, color, color_background)
        GRAYSCALE_PAIRS[name] = curses.color_pair(pair_number)

    curses.init_pair(255, curses.COLOR_RED, curses.COLOR_BLACK)
    GAMEOVER_PAIR = curses.color_pair(255)

    BOARD_HEIGHT = 20
    BOARD_WIDTH = 10
    BUFFER_ZONE = 20
    BOARD_PADDING = 0

    PREVIEW_HEIGHT = 3
    PREVIEW_WIDTH = 4
    PREVIEW_COUNT = 5

    # board setup
    board = Board(BOARD_HEIGHT, BOARD_WIDTH, BUFFER_ZONE, BOARD_PADDING)

    # piece preview setup.
    preview_x = board.win.getmaxyx()[1]+2
    piece_preview = Preview(PREVIEW_HEIGHT, PREVIEW_WIDTH,
                            PREVIEW_COUNT, preview_x)

    # initialize piece queue.
    piece_queue = PieceQueue(PREVIEW_COUNT)

    # initialize player stats.
    stats = PlayerStats()

    # begin gameplay loop.
    gameover = False
    while not gameover:
        # advance the piece queue.
        piece_queue.advance()

        # render piece preview.
        piece_preview.render_preview(
            piece_queue.get_preview(),
            COLOR_PAIRS
        )

        # activate the new 'current' piece.
        active_tetromino = ActiveTetromino(
            piece_queue.get_current(),
            board, BUFFER_ZONE-2)

        # initialize lock timer.
        lock_timer = 0

        # initialize gravity.
        gravity = stats.speed

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
            board.render_data(screen_data, COLOR_PAIRS)

            # keep frame rate at roughly 60fps.
            sleep_time = 1/60 - (time.time()-start)
            if sleep_time > 0:
                time.sleep(sleep_time)

        # save tetromino to board data and clear any lines created.
        board.addTetromino(active_tetromino)
        lines_cleared = board.clearLines()

        # update player's stats.
        stats.update_stats(lines_cleared)

        # re-render the playfield with new info.
        board.render_data(board.get_playfield(), COLOR_PAIRS)

        # detect top-out (game over).
        buffer_zone = board.get_buffer_zone()
        for row in buffer_zone:
            for cell in row:
                if cell:
                    gameover = True
    else:
        # turn the entire playfield black and white.
        screen_data = board.get_playfield()
        board.render_data(screen_data, GRAYSCALE_PAIRS)
        piece_preview.render_preview(
            piece_queue.get_preview(), GRAYSCALE_PAIRS
        )
        # print game over message.
        stdscr.addstr(10, 5, ' Game Over! ', GAMEOVER_PAIR)
        stdscr.refresh()

    # Terminate ──────────────────────────────────────────────────────
    # wait for user to quit a final time before quitting.
    key_pressed = stdscr.getch()
    while key_pressed != ord('q'):
        key_pressed = stdscr.getch()

    return 0  # Return 0 indicates a successful completion


# Program entry point
if __name__ == "__main__":
    wrapper(main)
