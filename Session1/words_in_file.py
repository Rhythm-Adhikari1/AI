def count_words_in_file(filename):
    try:
        with open(filename, 'r') as file:
            content = file.read()
            
            # Split words by whitespace
            words = content.split()
            
            return len(words)

    except FileNotFoundError:
        print("Error: File does not exist.")
        return None
    except Exception as e:
        print("An unexpected error occurred:", e)
        return None


# Example usage
filename = input("Enter file name: ")
word_count = count_words_in_file(filename)

if word_count is not None:
    print("Total number of words:", word_count)