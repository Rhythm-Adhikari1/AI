"""Word-count utility script.

This module provides a simple function that reads a text file and counts the
number of whitespace-separated words it contains. It also includes a minimal
interactive example for direct execution.
"""


def count_words_in_file(filename):
    """Return the number of words in the specified text file.

    Args:
        filename: Path to the text file to read.

    Returns:
        The number of words as an integer, or None if the file cannot be read.
    """
    try:
        with open(filename, 'r') as file:
            content = file.read()

            words = content.split()

            return len(words)

    except FileNotFoundError:
        print("Error: File does not exist.")
        return None
    except Exception as e:
        print("An unexpected error occurred:", e)
        return None


filename = input("Enter file name: ")
word_count = count_words_in_file(filename)

if word_count is not None:
    print("Total number of words:", word_count)