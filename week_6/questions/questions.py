import math
import nltk
import sys
import os
import string

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {filename: tokenize(files[filename]) for filename in files}
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """

    files = dict()

    for filename in os.listdir(directory):
        with open(os.path.join(directory, filename)) as f:
            files[filename] = f.read()

    return files


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """

    contents = [
        word.lower()
        for word in nltk.word_tokenize(document)
        if word not in string.punctuation
        and word not in nltk.corpus.stopwords.words("english")
    ]

    return contents


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """

    # Compile all the words in the documents into a single set.
    words = set()
    for filename in documents:
        for word in documents[filename]:
            words.add(word)

    # IDF is log of total number of documents, divided by number of documents the word appears in.
    idfs = dict()
    for word in words:
        f = sum(word in documents[filename] for filename in documents)
        idf = math.log(len(documents.keys()) / f)
        idfs[word] = idf

    return idfs


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """

    tf_idfs = []

    for filename in files:
        tf_idf_sum = 0

        for query_word in query:
            tf = sum(query_word == word for word in files[filename])
            tf_idf_sum += tf * idfs[query_word]

        tf_idfs.append((filename, tf_idf_sum))

    # Sort the files by their tf-idf sum
    tf_idfs.sort(key=lambda tfidf: tfidf[1], reverse=True)

    # Select only the top n filenames to return
    top_filenames = []
    for i in range(n):
        top_filenames.append(tf_idfs[i][0])

    return top_filenames


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """

    sentence_idfs = []

    for sentence in sentences:
        idf_sum = 0
        no_query_words = 0

        # Calculate the sum of IDF values for all the query words that appear in the sentence.
        for query_word in query:
            if query_word in sentences[sentence]:
                idf_sum += idfs[query_word]

        # Calculate the query term density, which is the proportion of words in the sentence that are query words.
        for word in sentences[sentence]:
            if word in query:
                no_query_words += 1
        qtd = no_query_words / len(sentences[sentence])

        sentence_idfs.append((sentence, idf_sum, qtd))

    # First sort the files by their qtd, then by the idf sum.
    sentence_idfs.sort(key=lambda tfidf: tfidf[2], reverse=True)
    sentence_idfs.sort(key=lambda tfidf: tfidf[1], reverse=True)

    # Select only the top n sentences to return
    top_sentences = []
    for i in range(n):
        top_sentences.append(sentence_idfs[i][0])

    return top_sentences


if __name__ == "__main__":
    main()
