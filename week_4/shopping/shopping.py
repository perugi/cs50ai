import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """

    MONTHS = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "June",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]

    evidence = []
    labels = []

    with open(filename) as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=",")

        for i, row in enumerate(csv_reader):

            single_evidence = []
            single_evidence.append(int(row["Administrative"]))
            single_evidence.append(float(row["Administrative_Duration"]))
            single_evidence.append(int(row["Informational"]))
            single_evidence.append(float(row["Informational_Duration"]))
            single_evidence.append(int(row["ProductRelated"]))
            single_evidence.append(float(row["ProductRelated_Duration"]))
            single_evidence.append(float(row["BounceRates"]))
            single_evidence.append(float(row["ExitRates"]))
            single_evidence.append(float(row["PageValues"]))
            single_evidence.append(float(row["SpecialDay"]))

            if row["Month"] in MONTHS:
                single_evidence.append(MONTHS.index(row["Month"]))
            else:
                raise RuntimeError(f"Month specification invalid for row {i}: {row}")

            single_evidence.append(int(row["OperatingSystems"]))
            single_evidence.append(int(row["Browser"]))
            single_evidence.append(int(row["Region"]))
            single_evidence.append(int(row["TrafficType"]))

            if row["VisitorType"] == "Returning_Visitor":
                single_evidence.append(1)
            else:
                single_evidence.append(0)

            if row["Weekend"] == "TRUE":
                single_evidence.append(1)
            elif row["Weekend"] == "FALSE":
                single_evidence.append(0)
            else:
                raise RuntimeError(f"Weekend specification invalid for row {i}: {row}")

            if row["Revenue"] == "TRUE":
                single_label = 1
            elif row["Revenue"] == "FALSE":
                single_label = 0
            else:
                raise RuntimeError(f"Revenue specification invalid for row {i}: {row}")

            evidence.append(single_evidence)
            labels.append(single_label)

        return (evidence, labels)


def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """

    model = KNeighborsClassifier(n_neighbors=1)
    model.fit(evidence, labels)

    return model


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificity).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """

    # Counts of "True" and "False" labels in the test data.
    count_true = 0
    count_false = 0

    # Counts of correct predictions of "True" and "False" in the test data
    count_correct_true = 0
    count_correct_false = 0

    for label, prediction in zip(labels, predictions):
        if label == 1:
            count_true += 1
            if label == prediction:
                count_correct_true += 1
        else:
            count_false += 1
            if label == prediction:
                count_correct_false += 1

    sensitivity = count_correct_true / count_true
    specificity = count_correct_false / count_false

    return (sensitivity, specificity)


if __name__ == "__main__":
    main()
