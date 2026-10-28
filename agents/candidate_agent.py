from collections import Counter
from game import get_feedback

FIRST_GUESS = 'arise'
FULL_SIZE = 2315

def choose_guess(possible_words, all_guesses):
    if len(possible_words) == FULL_SIZE:
        return FIRST_GUESS
    if len(possible_words) == 1:
        return possible_words[0]
    best_word = None
    best_score = None
    for guess in possible_words:
        pattern_counts = Counter()
        for answer in possible_words:
            pattern_counts[get_feedback(guess, answer)] += 1
        worst_case = max(pattern_counts.values())
        if best_score is None or worst_case < best_score:
            best_score = worst_case
            best_word = guess
    return best_word
