from tictactoe import initial_state, player, actions, result, winner, terminal, utility

X = "X"
O = "O"
EMPTY = None

board = initial_state()
terminal_board = [[X, O, O], [O, X, X], [X, O, O]]
for row in board:
    print(row)
print(player(board))
print(actions(board))
print(winner(board))
print(terminal(board))
print(utility(board))

print("--------")

board = result(board, (0, 0))
for row in board:
    print(row)
print(player(board))
print(actions(board))
print(winner(board))
print(terminal(board))
print(utility(board))

print("--------")

board = result(board, (0, 1))
for row in board:
    print(row)
print(player(board))
print(actions(board))
print(winner(board))
print(terminal(board))
print(utility(board))

print("--------")

board = [[O, O, O], [X, X, X], [EMPTY, EMPTY, EMPTY]]
for row in board:
    print(row)
print(player(board))
print(actions(board))
print(winner(board))
print(terminal(board))
print(utility(board))

print("--------")

board = [[O, O, X], [O, X, X], [O, EMPTY, EMPTY]]
for row in board:
    print(row)
print(player(board))
print(actions(board))
print(winner(board))
print(terminal(board))
print(utility(board))

print("--------")

board = [[O, O, X], [O, O, X], [X, EMPTY, O]]
for row in board:
    print(row)
print(player(board))
print(actions(board))
print(winner(board))
print(terminal(board))
print(utility(board))

print("--------")

board = [[O, O, X], [O, X, X], [X, EMPTY, EMPTY]]
for row in board:
    print(row)
print(player(board))
print(actions(board))
print(winner(board))
print(terminal(board))
print(utility(board))

print("--------")

for row in terminal_board:
    print(row)
print(player(terminal_board))
print(actions(terminal_board))
print(winner(terminal_board))
print(terminal(terminal_board))
print(utility(terminal_board))
