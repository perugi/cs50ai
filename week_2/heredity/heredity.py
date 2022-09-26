import csv
import itertools
import sys

PROBS = {
    # Unconditional probabilities for having gene
    "gene": {2: 0.01, 1: 0.03, 0: 0.96},
    "trait": {
        # Probability of trait given two copies of gene
        2: {True: 0.65, False: 0.35},
        # Probability of trait given one copy of gene
        1: {True: 0.56, False: 0.44},
        # Probability of trait given no gene
        0: {True: 0.01, False: 0.99},
    },
    # Mutation probability
    "mutation": 0.01,
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {"gene": {2: 0, 1: 0, 0: 0}, "trait": {True: 0, False: 0}}
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (
                people[person]["trait"] is not None
                and people[person]["trait"] != (person in have_trait)
            )
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (
                    True
                    if row["trait"] == "1"
                    else False
                    if row["trait"] == "0"
                    else None
                ),
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s)
        for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """

    probability = 1

    for person in people:
        if people[person]["father"] == None and people[person]["mother"] == None:
            # Person does not have parents defined, we should take the population
            # probabilities for the presence of the genes.
            gene_prob = pop_gene_prob(person, one_gene, two_genes)
            trait_prob = pop_trait_prob(person, one_gene, two_genes, have_trait)

        else:
            # Person has parents defined, calculate the probabilities for having
            # the gene based on inheritance from parents.

            if person in one_gene:
                # Calculate the probability that exactly one gene was inherited.

                # Gene was inherited from the mother and not the father.
                gene_prob_mother = gene_inherit_prob(
                    people[person]["mother"], one_gene, two_genes
                ) * (
                    1 - gene_inherit_prob(people[person]["father"], one_gene, two_genes)
                )

                # Gene was inherited from the father and not the mother.
                gene_prob_father = gene_inherit_prob(
                    people[person]["father"], one_gene, two_genes
                ) * (
                    1 - gene_inherit_prob(people[person]["mother"], one_gene, two_genes)
                )

                gene_prob = gene_prob_mother + gene_prob_father

            elif person in two_genes:
                # Calculate the probability that the person inherited the gene
                # from both the parents.

                gene_prob = gene_inherit_prob(
                    people[person]["mother"], one_gene, two_genes
                ) * gene_inherit_prob(people[person]["father"], one_gene, two_genes)

            else:
                # Calculate the probability that the person did not inherit the gene
                # from either the mother or father.

                gene_prob = (
                    1 - gene_inherit_prob(people[person]["mother"], one_gene, two_genes)
                ) * (
                    1 - gene_inherit_prob(people[person]["father"], one_gene, two_genes)
                )

            trait_prob = pop_trait_prob(person, one_gene, two_genes, have_trait)

        # Multiply the total probability with the probabilities, calculated for
        # this particular person.
        probability *= gene_prob * trait_prob

    return probability


def gene_inherit_prob(parent, one_gene, two_genes):
    """
    Return the probability that the gene was inherited from a parent.
    """
    if parent in one_gene:
        inherit_prob = 0.5
    elif parent in two_genes:
        inherit_prob = 1 - PROBS["mutation"]
    else:
        inherit_prob = PROBS["mutation"]

    return inherit_prob


def pop_gene_prob(person, one_gene, two_genes):
    """
    Find the probabilities that the person has zero, one or two copies
    of the gene, based on the population probabilities.
    """

    if person in one_gene:
        gene_prob = PROBS["gene"][1]
    elif person in two_genes:
        gene_prob = PROBS["gene"][2]
    else:
        gene_prob = PROBS["gene"][0]

    return gene_prob


def pop_trait_prob(person, one_gene, two_genes, have_trait):
    """
    Find the probability that the trait is expressed or not, based on
    the presence of one, two or three genes.
    """

    if person in one_gene:
        if person in have_trait:
            trait_prob = PROBS["trait"][1][True]
        else:
            trait_prob = PROBS["trait"][1][False]
    elif person in two_genes:
        if person in have_trait:
            trait_prob = PROBS["trait"][2][True]
        else:
            trait_prob = PROBS["trait"][2][False]
    else:
        if person in have_trait:
            trait_prob = PROBS["trait"][0][True]
        else:
            trait_prob = PROBS["trait"][0][False]

    return trait_prob


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """

    for person in probabilities:
        if person in one_gene:
            probabilities[person]["gene"][1] += p
        elif person in two_genes:
            probabilities[person]["gene"][2] += p
        else:
            probabilities[person]["gene"][0] += p

        if person in have_trait:
            probabilities[person]["trait"][True] += p
        else:
            probabilities[person]["trait"][False] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """

    for person in probabilities:

        # Normalize gene number probabilities
        total_prob = 0
        for gene_no in probabilities[person]["gene"]:
            total_prob += probabilities[person]["gene"][gene_no]

        for gene_no in probabilities[person]["gene"]:
            probabilities[person]["gene"][gene_no] /= total_prob

        # Normalize trait expression probabilities
        total_prob = 0
        for have_trait in probabilities[person]["trait"]:
            total_prob += probabilities[person]["trait"][have_trait]

        for have_trait in probabilities[person]["trait"]:
            probabilities[person]["trait"][have_trait] /= total_prob


if __name__ == "__main__":
    main()
