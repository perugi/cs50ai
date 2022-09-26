"""
Tic Tac Toe Player
"""

import math
from copy import deepcopy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY], [EMPTY, EMPTY, EMPTY], [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    turn_count = 0

    for row in board:
        for field in row:
            if field:
                turn_count += 1

    if turn_count % 2:
        return O
    else:
        return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possible_actions = set()

    for column in range(len(board)):
        for row in range(len(board[0])):
            if board[row][column] == EMPTY:
                possible_actions.add((row, column))

    return possible_actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    new_board = deepcopy(board)
    if new_board[action[0]][action[1]] == EMPTY:
        new_board[action[0]][action[1]] = player(board)
    else:
        raise RuntimeError("Action not allowed")

    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """

    # Check all rows for three O or X.
    for row_under_test in board:
        if is_same(row_under_test):
            return row_under_test[0]

    # Check all columns for three O or X.
    for column in range(len(board)):
        column_under_test = []
        for row in range(len(board[0])):
            column_under_test.append(board[row][column])

        if is_same(column_under_test):
            return column_under_test[0]

    # Check one diagonal for three 0 or X.
    diag_under_test = []
    for coord in range(len(board)):
        diag_under_test.append(board[coord][coord])

    if is_same(diag_under_test):
        return diag_under_test[0]

    # Check the other diagonal for three 0 or X.
    diag_under_test = []
    for column in range(len(board)):
        diag_under_test.append(board[len(board) - column - 1][column])

    if is_same(diag_under_test):
        return diag_under_test[0]

    return None


def is_same(list):
    """
    Returns True if all elements in the list are the same and defined (not None)
    """
    if list[0]:
        return all(element == list[0] for element in list)
    else:
        return False


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    # Check if any player has won the game.
    if winner(board):
        return True

    # Since no player has won the game, if any of the spaces are still empty, the game is not over
    for row in board:
        for field in row:
            if field == EMPTY:
                return False

    # No player has won the game and all spaces are filled (game is over as a tie).
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    winning_player = winner(board)

    if winning_player == X:
        return 1
    elif winning_player == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    # The X player optimizes for maximized utility, while the O player optimizes for the minimal.
    if player(board) == X:
        return max_value(board, -math.inf, math.inf)[1]
    else:
        return min_value(board, -math.inf, math.inf)[1]


def max_value(board, alpha, beta):
    """
    Return the action that produces the highest value of min_value (the opponents optimization)
    Also return the calculated utility of that action, in order to use it in the recursive function.
    Alpha-beta pruning is performed to optimize the algorithm.
    """
    if terminal(board):
        return (utility(board), None)

    v = -math.inf
    optimal_action = None

    for action in actions(board):
        result_v = min_value(result(board, action), alpha, beta)[0]
        if result_v > v:
            v = result_v
            optimal_action = action

        if v >= beta:
            return (v, optimal_action)

        if v > alpha:
            alpha = v

    return (v, optimal_action)


def min_value(board, alpha, beta):
    """
    Return the action that produces the lowest value of max_value (the opponents optimization)
    Also return the calculated utility of that action, in order to use it in the recursive function.
    Alpha-beta pruning is performed to optimize the algorithm.
    """
    if terminal(board):
        return (utility(board), None)

    v = math.inf
    optimal_action = None

    for action in actions(board):
        result_v = max_value(result(board, action), alpha, beta)[0]
        if result_v < v:
            v = result_v
            optimal_action = action

        if v <= alpha:
            return (v, optimal_action)

        if v < beta:
            beta = v

    return (v, optimal_action)
