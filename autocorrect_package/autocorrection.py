import string
import re
from collections import Counter
import editdistance


class Autocorrection:

    def __init__(self, filename):
        # Load the corpus and process words
        with open(filename, "r", encoding="utf-8") as file:
            words = []
            for line in file:
                words += re.findall(r'\w+', line.lower())

        self.vocabulary = set(words)
        self.counts_of_word = Counter(words)
        self.total_words = float(sum(self.counts_of_word.values()))
        self.prob_of_word = {w: self.counts_of_word[w] / self.total_words for w in self.counts_of_word.keys()}

    def edit1(self, word):
        letters = string.ascii_lowercase
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        inserts = [L + c + R for L, R in splits for c in letters]
        deletes = [L + R[1:] for L, R in splits if R]
        replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
        swaps = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
        return set(inserts + deletes + replaces + swaps)

    def edit2(self, word):
        # Edit distance 2 suggestions
        return set(e2 for e1 in self.edit1(word) for e2 in self.edit1(e1))

    def common_prefix_length(self, word1, word2):
        # Compute the length of the common prefix
        return len([1 for c1, c2 in zip(word1, word2) if c1 == c2])

    def custom_score(self, suggestion, original_word):
        # Assign weights to edit operations
        replace_weight = 1
        insert_weight = 2
        delete_weight = 3
        swap_weight = 4

        # Calculate edit distance
        distance = editdistance.eval(suggestion, original_word)

        # Calculate score based on edit operations
        if len(suggestion) == len(original_word):  # Replace
            return distance * replace_weight + len(original_word) - self.common_prefix_length(suggestion, original_word)
        elif len(suggestion) == len(original_word) + 1:  # Insert
            return distance * insert_weight
        elif len(suggestion) == len(original_word) - 1:  # Delete
            return distance * delete_weight
        else:  # Swap
            return distance * swap_weight

    def correct_spelling(self, word):
        # Return if the word is correctly spelled
        if word in self.vocabulary:
            print(f"'{word}' is already correctly spelled.")
            return [(word, self.prob_of_word[word])]

        # Generate suggestions
        suggestions = self.edit1(word) or self.edit2(word) or [word]
        best_guesses = [w for w in suggestions if w in self.vocabulary]

        # Sort suggestions based on custom score and probability
        best_guesses.sort(key=lambda w: (self.custom_score(w, word), -self.prob_of_word.get(w, 0)))

        # Return suggestions with probabilities
        return [(w, self.prob_of_word.get(w, 0)) for w in best_guesses]
