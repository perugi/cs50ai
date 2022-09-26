from questions import tokenize

print(
    tokenize(
        "This is a test string! We should return a list of words and filter out any punctuation, like $#&*@! and any stop words."
    )
)
