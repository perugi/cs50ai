from operator import itemgetter
import sys
import logging

from crossword import *

logging.basicConfig(filename="debug.log", filemode="w", level=logging.DEBUG)


class CrosswordCreator:
    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy() for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont

        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size, self.crossword.height * cell_size),
            "black",
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border, i * cell_size + cell_border),
                    (
                        (j + 1) * cell_size - cell_border,
                        (i + 1) * cell_size - cell_border,
                    ),
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (
                                rect[0][0] + ((interior_size - w) / 2),
                                rect[0][1] + ((interior_size - h) / 2) - 10,
                            ),
                            letters[i][j],
                            fill="black",
                            font=font,
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """

        logging.info("Starting enforce_node_consistency")

        logging.info(f"Initial variable domains:")
        for variable in self.crossword.variables:
            logging.info(f"{variable}:")
            logging.info(f"    {self.domains[variable]}")

        for variable in self.domains:
            self.domains[variable] = set(
                [
                    word
                    for word in self.domains[variable]
                    if len(word) == variable.length
                ]
            )

        logging.info(f"Final variable domains:")
        for variable in self.crossword.variables:
            logging.info(f"{variable}:")
            logging.info(f"    {self.domains[variable]}")

        logging.info("Exiting enforce_node_consistency")

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """

        revised = False

        if not self.crossword.overlaps[(x, y)]:
            # If there is no overlap between the two variables, exit the function.
            return revised

        for x_word in self.domains[x].copy():
            # This variable is used to track if the word in the domain of x has a
            # corresponding possible value in the domain of y.
            word_match = False

            for y_word in self.domains[y]:
                if (
                    x_word[self.crossword.overlaps[(x, y)][0]]
                    == y_word[self.crossword.overlaps[(x, y)][1]]
                ):
                    # If a word that matches the criteria (same character in the field
                    # that overlaps) is found in the y domain then we can break the loop,
                    # the word will not be deleted from the x domain
                    word_match = True
                    break

            if not word_match:
                self.domains[x].remove(x_word)
                revised = True

        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        logging.info("Starting ac3")
        logging.debug(f"Overlaps: {self.crossword.overlaps}")

        if arcs:
            queue = arcs
        else:
            # Add all the arcs (overlaps) to the queue. As the constraints are valid for both
            # directions of the arc (both words that overlap), add both to the queue.
            queue = []
            for overlap in self.crossword.overlaps.keys():
                queue.append((overlap[0], overlap[1]))
                queue.append((overlap[1], overlap[0]))

        logging.debug(f"Initial queue: {queue}")
        logging.info(f"Initial variables:")
        for variable in self.crossword.variables:
            logging.info(variable)
            logging.info(f"    {self.domains[variable]}")

        while queue:
            (x, y) = queue.pop()
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                current_neighbors = self.crossword.neighbors(x)
                current_neighbors.remove(y)
                for neighbor in current_neighbors:
                    queue.append((x, neighbor))

        logging.debug(f"Final queue: {queue}")
        logging.info(f"Variables:")
        for variable in self.crossword.variables:
            logging.info(variable)
            logging.info(f"    {self.domains[variable]}")
        logging.info("Exiting ac3")

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """

        logging.debug("Starting assingnment_complete")
        logging.debug(f"Assignment: {assignment}")

        for variable in self.crossword.variables:
            # Check if all the variables exist in the assignment
            if variable not in assignment or not assignment[variable]:
                logging.debug(
                    "Not all variables have been assigned a word, exiting assignment_complete"
                )
                return False

        logging.debug("Assignment complete, exiting assignment_complete")
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        logging.debug("Starting consistent")
        logging.debug(f"Assignment: {assignment}")

        assigned_words = []

        for variable, word in assignment.items():

            # Check if a duplicate word exists in the assignment.
            if word in assigned_words:
                logging.debug(
                    f"Duplicate values of '{word}' exist in the assignment, exiting consistent"
                )
                return False
            assigned_words.append(word)

            # Check if the assigned word is the correct length.
            if len(word) != variable.length:
                logging.debug(
                    f"The word '{word}' should be {variable.length} characters long, exiting consistent"
                )
                return False

            # Check if the binary constraints are satisfied (overlapping words have the same
            # character at the required location).
            for variable_2, word_2 in assignment.items():
                if variable == variable_2:
                    continue

                # If there is no overlap between the two variables, don't perform any check.
                if not self.crossword.overlaps[(variable, variable_2)]:
                    continue

                if (
                    word[self.crossword.overlaps[(variable, variable_2)][0]]
                    != word_2[self.crossword.overlaps[(variable, variable_2)][1]]
                ):
                    logging.debug(
                        f"The words '{word}' and '{word_2}' should have the same characters on positions {self.crossword.overlaps[(variable, variable_2)][0]} and {self.crossword.overlaps[(variable, variable_2)][0]}, exiting consistent"
                    )
                    return False

        # If nothing is inconsistent, then the assignment is consistent
        logging.debug("Consistency check passed, exiting consistent")
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        logging.debug("Starting order_domain_values")

        # Create a list of words in the domain with corresponding number of values they rule out
        # for neighboring variables.
        domain_values = []
        for word in self.domains[var]:
            count = 0
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    continue

                for word_2 in self.domains[neighbor]:
                    if (
                        word[self.crossword.overlaps[(var, neighbor)][0]]
                        != word_2[self.crossword.overlaps[(var, neighbor)][1]]
                    ):
                        count += 1
            domain_values.append((word, count))

        logging.debug(f"Domain values: {domain_values}")
        # Sort the list by the corresponding counts.
        domain_values.sort(key=itemgetter(1))
        logging.debug(f"Domain values (sorted): {domain_values}")

        return [value[0] for value in domain_values]

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """

        logging.debug("Starting select_unassigned_variable")
        logging.debug(f"Current assignment: {assignment}")
        logging.debug(f"All variables: {self.crossword.variables}")

        # Create a list of variables with corresponding numbers of remaining values in its domain
        # and the number of its neighbors.
        unassigned_variables = []
        for variable in self.crossword.variables:
            if variable not in assignment:
                domain_number = len(self.domains[variable])
                degree = len(self.crossword.neighbors(variable))
                unassigned_variables.append((variable, domain_number, degree))

        # Sort the list, first based on degrees in reverse order and then based on the number
        # of remaining valies in its domain. The resulting element in [0] follows the defined heuristic
        logging.debug(f"Unassigned variables: {unassigned_variables}")
        unassigned_variables.sort(key=itemgetter(2), reverse=True)
        unassigned_variables.sort(key=itemgetter(1))
        logging.debug(f"Unassigned variables (sorted): {unassigned_variables}")

        if len(unassigned_variables) > 0:
            logging.debug(
                f"Selecting variable {unassigned_variables[0][0]}, exiting select_unassigned_variable"
            )
            return unassigned_variables[0][0]
        else:
            logging.debug("No variable unassigned, exiting select_unassigned_variable")
            return None

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """

        logging.info("Starting Backtrack")

        if self.assignment_complete(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            new_assignment = assignment.copy()
            new_assignment[var] = value

            if self.consistent(new_assignment):
                result = self.backtrack(new_assignment)
                if result is not None:
                    return result

        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
