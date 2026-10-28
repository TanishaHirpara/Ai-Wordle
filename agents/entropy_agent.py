import math
from collections import Counter
from game import get_feedback

FIRST_GUESS = 'raise'
FULL_SIZE = 2315

def expected_information(guess, possible_words):
    pattern_counts = Counter()
    for answer in possible_words:
        pattern_counts[get_feedback(guess, answer)] += 1
    total = len(possible_words)
    entropy = 0.0
    for count in pattern_counts.values():
        probability = count / total
        entropy -= probability * math.log2(probability)
    return entropy

def choose_guess(possible_words, all_guesses):
    if len(possible_words) == FULL_SIZE:
        return FIRST_GUESS
    if len(possible_words) == 1:
        return possible_words[0]
    best_word = None
    best_entropy = -1
    for guess in possible_words:
        entropy = expected_information(guess, possible_words)
        if entropy > best_entropy:
            best_entropy = entropy
            best_word = guess
    return best_word
