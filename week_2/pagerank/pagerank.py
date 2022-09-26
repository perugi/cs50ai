import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(link for link in pages[filename] if link in pages)

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """

    # Set of linked pages from the current page.
    linked_pages = corpus[page]

    link_probabilities = {}

    if len(linked_pages) == 0:
        # If the current page has no links, we return a probability distribution of
        # equal probabilities to visit any page in the corpus.
        for page in corpus:
            link_probabilities[page] = 1.0 / len(corpus)

    else:
        for page in corpus:
            # Build up the probabilities that the surfer visits one of the random pages
            # in the corpus - the (1 - damping_factor) probability should be distributed
            # among all the pages in the corpus.
            link_probabilities[page] = (1.0 - damping_factor) / len(corpus)

            # Add the linked page probabilities - for the linked pages, the
            # damping_factor probability should be distributed over the number of linked
            # pages.
            if page in linked_pages:
                link_probabilities[page] += damping_factor / len(linked_pages)

    return link_probabilities


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # Initialize all page counts to zero
    page_counts = {}
    for page in corpus:
        page_counts[page] = 0

    # The first page is chosen at random.
    next_page = random.choice(list(corpus.keys()))
    page_counts[next_page] += 1

    for sample_number in range(n - 1):
        link_probabilities = transition_model(corpus, next_page, damping_factor)
        # Make a selection of next page, weighted by the probabilities, returned by the
        # transition model.
        next_page = random.choices(
            list(link_probabilities.keys()), list(link_probabilities.values())
        )[0]

        page_counts[next_page] += 1

    # Normalize the page ranks, based on the number of samples (in order to sum up to 1)
    page_ranks = {}
    for page in page_counts:
        page_ranks[page] = page_counts[page] / n

    return page_ranks


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    ACCURACY = 0.001
    iteration_num = 0

    # Initialize all page ranks to 1 / N (N = number of pages in the corpus)
    page_ranks = {}
    for page in corpus:
        page_ranks[page] = 1 / len(corpus)

    while True:
        repeat_iteration = False
        new_page_ranks = {}

        for page in page_ranks:
            # Probability that we ended on the page randomly (1 - d, divided by the number
            # of pages)
            new_page_ranks[page] = (1 - damping_factor) / len(corpus)

            # Find all the pages that link to the page
            for linking_page in corpus:
                # If a page has no links, it should be interpreted as having one link
                # for every page in the corpus, including itself.
                if len(corpus[linking_page]) == 0:
                    new_page_ranks[page] += (
                        damping_factor * page_ranks[linking_page] / len(corpus)
                    )
                # If the page we are looking for is on the list of links for the linking
                # page, add the probability we got to our page through this one (damping
                # probability, multiplied by the probability we are on the page (page
                # ranking), divided by the number of links on the page.
                else:
                    if page in corpus[linking_page]:
                        new_page_ranks[page] += (
                            damping_factor
                            * page_ranks[linking_page]
                            / len(corpus[linking_page])
                        )

            # If the difference between the old and new rank for any page rank is higher
            # than the requested accuracy, repeat the iteration
            if abs(new_page_ranks[page] - page_ranks[page]) >= ACCURACY:
                repeat_iteration = True

        page_ranks = new_page_ranks
        iteration_num += 1

        if not repeat_iteration:
            break

    return page_ranks


if __name__ == "__main__":
    main()
