# ACSC430 - Dynamic Languages
# Lab 05 - Strings, Lists, and Files
# Regnum: st024395
# Name: Eleftheria
# Surname: Kyriakou
# Date: 2026-05-05

import string
from pathlib import Path
try:
    import htmlFunctions
except ImportError:
    htmlFunctions = None

TRUMP_SPEAKERS = \
    (
    "President Donald J. Trump:",
    "President Donald Trump:",
    "Donald Trump:",
    "Trump:",
)

BIDEN_SPEAKERS = \
    (
    "Vice President Joe Biden:",
    "Joe Biden:",
    "Biden:",
)


def prompt_filename():
    #Ask the user for a file name until the file exists.
    while True:
        filename = input("Enter the name of the debate file to process: ").strip()
        if Path(filename).is_file():
            return filename
        print(f"File '{filename}' was not found. Try again.")


def load_stopwords(filename="stopWords.txt"):
    #Read the stop words from the file and store them in a set.
    path = Path(filename)
    if not path.is_file():
        print(f"Warning: stopword file '{filename}' was not found.")
        return set()

    stopwords = set()
    with path.open(encoding="utf-8") as file_obj:
        for line in file_obj:
            word = line.strip().lower()
            if word:
                stopwords.add(word)
    return stopwords


def identify_speaker(line):
    #check whether the current line belongs to Trump or Biden.
    stripped_line = line.strip()

    for label in TRUMP_SPEAKERS:
        if stripped_line.startswith(label):
            return "trump"

    for label in BIDEN_SPEAKERS:
        if stripped_line.startswith(label):
            return "biden"

    return None


def remove_speaker_label(line):
    #Remove the speaker name and the timestamp from the line.
    stripped_line = line.strip()

    for label in TRUMP_SPEAKERS + BIDEN_SPEAKERS:
        if stripped_line.startswith(label):
            remainder = stripped_line[len(label):].strip()
            parts = remainder.split(maxsplit=1)
            if parts and parts[0].startswith("(") and parts[0].endswith(")"):
                return parts[1] if len(parts) > 1 else ""
            return remainder

    return stripped_line


def clean_word(word):
    #Convert the word to lowercase and remove punctuation marks.
    cleaned = word.lower().strip()
    for char in string.punctuation:
        cleaned = cleaned.replace(char, "")
    return cleaned


def update_counts(text, counts, stopwords):
    #split the text into words and count the valid ones.
    for raw_word in text.split():
        word = clean_word(raw_word)
        if not word or word in stopwords:
            continue
        counts[word] = counts.get(word, 0) + 1


def parse_debate_file(filename, stopwords):
    # Read the file and keep separate word counts for each candidate.
    trump_counts = {}
    biden_counts = {}
    current_speaker = None

    with open(filename, encoding="utf-8") as file_obj:
        for line in file_obj:
            speaker = identify_speaker(line)
            if speaker is not None:
                current_speaker = speaker
                line = remove_speaker_label(line)

            if current_speaker == "trump":
                update_counts(line, trump_counts, stopwords)
            elif current_speaker == "biden":
                update_counts(line, biden_counts, stopwords)

    return trump_counts, biden_counts


def top_words(counts, limit=40):
    # Sort by count from highest to lowest and keep the top 40.
    pairs = [(count, word) for word, count in counts.items()]
    pairs.sort(key=lambda item: (-item[0], item[1]))
    return pairs[:limit]


def print_word_frequencies(label, counts):
    # Print the top words using the format count:word.
    print("++++++++++++")
    print(f"{label} : words in frequency order as count:word pairs")

    top_counts = top_words(counts)
    for index, (count, word) in enumerate(top_counts, start=1):
        print(f"{count:2}:{word}", end=" ")
        if index % 4 == 0:
            print()

    if len(top_counts) % 4 != 0:
        print()


def create_tag_cloud(counts, output_name):
    # Use the given HTML functions to create the tag cloud file.
    if htmlFunctions is None:
        print("Warning: htmlFunctions.py is missing, so no HTML file was created.")
        return

    top_counts = top_words(counts)
    if not top_counts:
        print(f"Warning: no words available for '{output_name}'.")
        return

    alphabetic_words = sorted((word, count) for count, word in top_counts)
    high = top_counts[0][0]
    low = top_counts[-1][0]

    body = ""
    for word, count in alphabetic_words:
        body += htmlFunctions.make_HTML_word(word, count, high, low)

    html_box = htmlFunctions.make_HTML_box(body)
    htmlFunctions.print_HTML_file(html_box, output_name)


def output_names_from_filename(filename):
    #decide whether the file is for debate 1 or debate 2.
    stem = Path(filename).stem.lower()
    debate_number = "1"

    if "two" in stem or stem.endswith("2"):
        debate_number = "2"

    labels = {
        "trump_label": f"Trump_{debate_number}",
        "biden_label": f"Biden_{debate_number}",
        "trump_html": "trump",
        "biden_html": "biden",
    }

    return labels


def main():
    #load the stop words, read the debate file, print results, and create HTML.
    stopwords = load_stopwords()
    filename = prompt_filename()

    print(f"Parsing file '{filename}'")
    trump_counts, biden_counts = parse_debate_file(filename, stopwords)

    labels = output_names_from_filename(filename)

    print(f"Here is the word frequency for both Trump and Biden on debate {labels['trump_label'][-1]}")
    print_word_frequencies(labels["trump_label"], trump_counts)
    print_word_frequencies(labels["biden_label"], biden_counts)

    create_tag_cloud(trump_counts, labels["trump_html"])
    create_tag_cloud(biden_counts, labels["biden_html"])


if __name__ == "__main__":
    main()
