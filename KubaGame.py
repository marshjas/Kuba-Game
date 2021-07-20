# Name: Jason Marsh
# Date: 5/31/2021
# Description: Implementation of the game Kuba. The game is played by two players
# who take alternating turns pushing marbles forwards, backwards, left, or right. When a marble is pushed, it moves
# one space. If there is a marble currently occupying that next space, that marble also moves a space in the same
# direction, and so on until an empty space is reached. If a marble gets pushed off the edge, it is removed from the
# board. There are three types of marbles: White and Black, each color belonging to one player, and Red, which
# is neutral. The game is won when a player either pushes off all of the other players marbles, or if they push
# off 7 red marbles. The player may not push their own marbles off of the board. Additionally. the player can only push
# one of their own marbles, and there must be an empty space (or the edge of the board) in the opposite direction
# from which they are pushing the marble. A player is also not allowed to "undo" the opponents move, by moving
# into a location that causes to board to be identical to where it was prior to the previous player's turn.
#
# This implementation consists of three classes, one overarching class for the game, as well as a class for the
# board and for the player.

class KubaGame:
    """Overarching Kuba class containing all elements of the game. This class contains the main functions
    for the running of the game: making moves, getting basic info about the status of the game,
    switching turns, and win conditions. It initializes Player objects and the Board object in its
    init method, and calls on them to get Player info and update/get the board positions respectively
    """
    def __init__(self, player1, player2):
        """Init method for KubaGame. Takes tuples containing each player's name and piece color, and uses
        that to initialize two Player objects, also contained in a defined dictionary. It initializes the Board object
        (which begins at the game's starting position), and sets current turn to None, since either player may begin
        the game. Lastly, it initializes the marble count.
        """
        self._player1 = Player(player1[0], player1[1])
        self._player2 = Player(player2[0], player2[1])

        self._players = {
            self._player1.get_name(): self._player1,
            self._player2.get_name(): self._player2
        }

        self._board = Board(self)

        self._current_turn = None

        self._marble_count = ()
        return

    def get_current_turn(self):
        """Returns the name of the player whose turn it currently is"""
        return self._current_turn

    def print_board(self):
        """Method to print the dictionary containing the board to the console"""
        for row in self._board.get_board():
            print(str(row) + ": " + str(self._board.get_board()[row]))

    def just_board(self):
        """Method to print board to the console neatly"""
        print("  0 1 2 3 4 5 6")
        for row in self._board.get_board():
            print(str(row), end=' ')
            for column in self._board.get_board()[row]:
                print(str(self._board.get_board()[row][column]), end=' ')
            print()

    def switch_turn(self, playername):
        """Change turn from 'B' to 'W', or from 'W' to 'B'"""

        # For the first turn, set turn to player who went first, then call function again
        if self._current_turn is None:
            self._current_turn = self._players[playername].get_color()
            self.switch_turn(playername)
        elif self._current_turn == 'B':
            self._current_turn = 'W'
        elif self._current_turn == 'W':
            self._current_turn = 'B'
        return

    def make_move(self, playername, coords, dir):
        """Takes player name, position of current piece, and direction as arguments,
        moves the marble in the direction specified (by updating the board with each move)
        returns True if move is successful, if move is invalid returns False
        """
        add_marble = False
        if self.validate_move(playername, coords, dir):

            # Move a 'pointer' in the direction specified by the player until the last marble to be moved
            # is reached, then point to the next empty space (i.e. the last marble before an empty space or the edge)
            current_space = coords
            while self.get_marble(current_space) != 'X' \
                    and self.get_marble(self.next_space(current_space, dir)) is not False:
                current_space = self.next_space(current_space, dir)

            # If a marble is being pushed off of the edge, ensure that it does not belong the the player making
            # the move. If it does, return False without changing the board
            if self.get_marble(current_space) == self._players[playername].get_color() \
                    and not self.get_marble(self.next_space(current_space, dir)):
                return False

            # If a red marble is going to be pushed off of the edge, add a red marble to the player's count.
            # Sets a boolean rather than executing the add to account for the case where the move has to
            # be undone
            if not self.get_marble(self.next_space(current_space, dir)) \
                    and self.get_marble(current_space) == 'R':
                add_marble = True

            # Handles case where one piece is being pushed off of the edge. Note that this is not reachable in
            # this implementation due to the rules of the game preventing moving any piece except for your
            # own, but also preventing you from pushing your own piece off the edge
            if current_space == coords:
                self._board.update_board(current_space, 'X')

            # Starting at the empty space, replace marble with previous marble, then place an X at the space
            # formerly containing the original marble
            while current_space != coords:
                self._board.update_board(current_space,
                                         self.get_marble(self.next_space(current_space, self.opposite_direction(dir))))
                self._board.update_board(self.next_space(current_space, self.opposite_direction(dir)), 'X')
                current_space = self.next_space(current_space, self.opposite_direction(dir))

            # Check board state from beginning of previous player's turn to ensure that the move is not
            # "undoing" the previous move. If so, revert the board to the state at the beginning of this
            # current turn and return False
            if self._board.get_states()[-2] == self._board.get_board():
                self._board.set_board(self._board.get_states()[-1])
                return False

            # Add red marble to player's count if boolean was set earlier
            if add_marble is True:
                self._players[playername].add_red_marble()

            self._board.save_state(self._board.get_board())
            self.switch_turn(playername)
            return True
        return False    #if move can't be validated, return False

    def validate_move(self, playername, coordinates, direction):
        """Function takes playername, coordinates, and direction and checks the following cases:
        - Ensures no one has won the game yet
        - Ensures it is the correct player's turn
        - Ensures the marble color being moved matches the player's color
        - Ensures there is an open space, or the edge of the board, in the opposite direction of the direction the
        marble is being moved in
        If any of these conditions are not met, returns False
        """
        if self.get_winner() is None:
            if self._current_turn == self._players[playername].get_color() \
                    or self._current_turn is None:
                if self._players[playername].get_color() == self.get_marble(coordinates):
                    if self.is_open_space(coordinates, self.opposite_direction(direction)):
                        return True
                    return False
                return False
            return False
        return False

    @staticmethod
    def opposite_direction(direction):
        """Takes a direction (F, B, L, or R), and returns the opposite direction"""
        if direction == 'F':
            return 'B'
        if direction == 'B':
            return 'F'
        if direction == 'L':
            return 'R'
        if direction == 'R':
            return 'L'
        return

    @staticmethod
    def next_space(coordinates, direction):
        """Takes coordinates and a direction and returns the marble at the next space in that direction
        Returns True if space is off the edge
        """
        try:
            if direction == 'F':
                return coordinates[0]-1, coordinates[1]
            if direction == 'B':
                return coordinates[0]+1, coordinates[1]
            if direction == 'L':
                return coordinates[0], coordinates[1]-1
            if direction == 'R':
                return coordinates[0], coordinates[1]+1
        except KeyError:
            return True     # Space is off the edge
        return False

    def is_open_space(self, coordinates, direction):
        """Takes coordinates and a direction and returns True if space is open ('X'), or if space is off the edge"""
        try:
            if direction == 'F':
                if self.get_marble((coordinates[0]-1, coordinates[1])) == 'X'\
                        or self.get_marble((coordinates[0]-1, coordinates[1])) is False:
                    return True
            if direction == 'B':
                if self.get_marble((coordinates[0]+1, coordinates[1])) == 'X'\
                        or self.get_marble((coordinates[0]+1, coordinates[1])) is False:
                    return True
            if direction == 'L':
                if self.get_marble((coordinates[0], coordinates[1]-1)) == 'X'\
                        or self.get_marble((coordinates[0], coordinates[1]-1)) is False:
                    return True
            if direction == 'R':
                if self.get_marble((coordinates[0], coordinates[1]+1)) == 'X'\
                        or self.get_marble((coordinates[0], coordinates[1]+1)) is False:
                    return True
        except KeyError:
            return True     # Space is off the edge
        return False

    def get_winner(self):
        """Returns name of winner if a player has won, returns None if there is no winner yet"""
        if self._player1.get_red_marbles() >= 7:
            return self._player1.get_name()

        if self._player2.get_red_marbles() >= 7:
            return self._player2.get_name()

        if self.get_marble_count()[0] == 0:
            for playername in self._players:
                if self._players[playername].get_color() == 'B':
                    return self._players[playername].get_name()

        if self.get_marble_count()[1] == 0:
            for playername in self._players:
                if self._players[playername].get_color() == 'W':
                    return self._players[playername].get_name()
        return

    def get_captured(self, playername):
        """Takes name of player as argument, returns number of red marbles captured by specified player"""
        return self._players[playername].get_red_marbles()

    def get_marble(self, coordinates):
        """Takes coordinates as argument, Returns marble type ('B','W','R') present at specified coordinates,
        if no marble exists there, returns 'X'
        """
        try:
            return self._board.get_board()[coordinates[0]][coordinates[1]]
        except KeyError:
            return False

    def get_marble_count(self):
        """Returns number of White, Black, and Red marbles, in that order, as a single tuple"""
        w_count = 0
        b_count = 0
        r_count = 0
        for row in self._board.get_board():
            for column in self._board.get_board():
                if self._board.get_board()[row][column] == 'W':
                    w_count += 1
                if self._board.get_board()[row][column] == 'B':
                    b_count += 1
                if self._board.get_board()[row][column] == 'R':
                    r_count += 1
        return w_count, b_count, r_count


class Player:
    """Class for Player. Used to store and retrieve data on player's name, piece color and number of red marbles
    captured. Instances of this class are used in the KubaGame class.
    """
    def __init__(self, name, color):
        self._name = name
        self._color = color
        self._red_marbles = 0
        return

    def get_color(self):
        """Getter method for player's color"""
        return self._color

    def set_color(self, color):
        """Setter method for player's color ('B','W'). Takes color as argument."""
        self._color = color
        return

    def get_name(self):
        """Getter method for player's name"""
        return self._name

    def set_name(self, name):
        """Setter method for player's name. Takes name as argument."""
        self._name = name
        return

    def add_red_marble(self):
        """Add a red marble to player's count"""
        self._red_marbles += 1

    def get_red_marbles(self):
        """Return number of red marbles captured by player"""
        return self._red_marbles


class Board:
    """Class for Board. Initializes board in starting position, and contains a method to update the board.
    This will be declared once at the start of the game in the main KubaGame class __init__ method
    """
    def __init__(self, game):
        """Initializes board in starting position as dictionary of rows,
        each row is a key for which the value is a dictionary of columns, each of those
        columns is a key for which the value is the color of the marble ('B', 'W', 'R'),
        or 'X' to represent an empty space
        """
        self._board = {
            0: {0: 'W', 1: 'W', 2: 'X', 3: 'X', 4: 'X', 5: 'B', 6: 'B'},
            1: {0: 'W', 1: 'W', 2: 'X', 3: 'R', 4: 'X', 5: 'B', 6: 'B'},
            2: {0: 'X', 1: 'X', 2: 'R', 3: 'R', 4: 'R', 5: 'X', 6: 'X'},
            3: {0: 'X', 1: 'R', 2: 'R', 3: 'R', 4: 'R', 5: 'R', 6: 'X'},
            4: {0: 'X', 1: 'X', 2: 'R', 3: 'R', 4: 'R', 5: 'X', 6: 'X'},
            5: {0: 'B', 1: 'B', 2: 'X', 3: 'R', 4: 'X', 5: 'W', 6: 'W'},
            6: {0: 'B', 1: 'B', 2: 'X', 3: 'X', 4: 'X', 5: 'W', 6: 'W'}
        }

        self._board_states = [None, None]

        self._game = game

    def get_board(self):
        """Getter method for board variable"""
        return self._board

    def set_board(self, board):
        """Setter method for board variable"""
        self._board = board
        return

    def update_board(self, coordinates, new_marble):
        """Method used to update board position when a valid move is made. Takes coordinates of space to be changed,
        as well as the new type of marble occupying the space ('B','W','R', 'X')
        """
        self._board[coordinates[0]][coordinates[1]] = new_marble

    def save_state(self, board):
        """"Takes "board" dictionary as an argument and copies it, new board is an independent dictionary
        variable and is not linked to the object argument.
        When finished, appends state to list containing all previous states
        """
        new_board = {
            0: {0: 'W', 1: 'W', 2: 'X', 3: 'X', 4: 'X', 5: 'B', 6: 'B'},
            1: {0: 'W', 1: 'W', 2: 'X', 3: 'R', 4: 'X', 5: 'B', 6: 'B'},
            2: {0: 'X', 1: 'X', 2: 'R', 3: 'R', 4: 'R', 5: 'X', 6: 'X'},
            3: {0: 'X', 1: 'R', 2: 'R', 3: 'R', 4: 'R', 5: 'R', 6: 'X'},
            4: {0: 'X', 1: 'X', 2: 'R', 3: 'R', 4: 'R', 5: 'X', 6: 'X'},
            5: {0: 'B', 1: 'B', 2: 'X', 3: 'R', 4: 'X', 5: 'W', 6: 'W'},
            6: {0: 'B', 1: 'B', 2: 'X', 3: 'X', 4: 'X', 5: 'W', 6: 'W'}
        }
        for row in board:
            for column in board[row]:
                new_board[row][column] = board[row][column]
        self._board_states.append(new_board)

    def get_states(self):
        """Returns list of previous board states"""
        return self._board_states
