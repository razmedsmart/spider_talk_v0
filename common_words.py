import nltk
from nltk.corpus import opinion_lexicon

# Download the opinion lexicon (if not already downloaded)
nltk.download('opinion_lexicon')

def get_emotional_words(n=20):
    """
    Get the n most common emotional words.

    Args:
    - n (int): Number of emotional words to return (default is 20).

    Returns:
    - emotional_words (list): A list of the most common emotional words.
    """
    # Get positive and negative words from the opinion lexicon
    positive_words = opinion_lexicon.positive()
    negative_words = opinion_lexicon.negative()

    # Combine positive and negative words
    emotional_words = set(positive_words + negative_words)

    # Get the n most common emotional words
    emotional_words = list(emotional_words)[:n]

    return emotional_words

def main():
    # Get the 20 most common emotional words
    emotional_words = get_emotional_words()

    # Print the emotional words
    print("The 20 most common emotional words are:")
    for word in emotional_words:
        print(word)

if __name__ == "__main__":
    main()
