import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set(),
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set(),
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """

    # If the two names are the same person, return an empty list (zero length).
    if source == target:
        return []

    node = solve(source, target)
    if node:
        # A solution exists, format it into a list of tuples (movie_id, person_id)
        solution = []
        while node.parent != None:
            solution.append((node.action, node.state))
            node = node.parent
        solution.reverse()
        return solution

    else:
        # A solution does not exist, return None.
        return None


def solve(source, target):
    """
    Solve the shortest path problem between the source and target,
    by using a BFS search algorithm.
    """

    # Create a frontier with the initial state as the only node in it.
    frontier = QueueFrontier()
    frontier.add(Node(source, None, None))

    explored = set()
    solution_found = False

    while True:

        # If the frontier is empty, there is no path between the two node.
        if frontier.empty():
            return None

        node = frontier.remove()

        explored.add(node.state)

        # Expand the node by adding all the neighboring nodes to the frontier.
        for movie_id, person_id in neighbors_for_person(node.state):

            next_node = Node(person_id, node, movie_id)

            # Optimization of the algorithm - check for a match already when expanding the node.
            if next_node.state == target:
                # A path has been found. Store the solution into the node variable,
                # as we still need to backtrack through our nodes, in order to return a list of movie_id and person_id tuples
                node = next_node
                solution_found = True
                break

            # Check that the node is not in the frontier and that it has not been explored yet.
            if frontier.contains_state(person_id) or person_id in explored:
                continue

            frontier.add(next_node)

        # This helper statements breaks us out of the while loop, if the solution has been
        # found during the expansion of the node.
        if solution_found:
            break

    return node


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
