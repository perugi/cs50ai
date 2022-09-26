from minesweeper import Minesweeper, Sentence

game = Minesweeper()

game.print()

knowledge = []

knowledge.append(Sentence({(1, 0), (1, 1)}, 1))
knowledge.append(Sentence({(1, 0), (1, 1), (1, 2)}, 1))
knowledge.append(Sentence({(1, 1), (1, 2)}, 1))
knowledge.append(Sentence({(1, 0), (1, 1), (1, 2), (2, 0), (2, 2)}, 2))

for sentence in knowledge:
    print(sentence)

print("--------")

for sentence in knowledge:
    sentence.mark_safe((1, 1))

for sentence in knowledge:
    print(sentence)

print("--------")

for sentence in knowledge:
    print(sentence.known_mines())
