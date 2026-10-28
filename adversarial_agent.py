import random
from game import get_feedback


def choose_feedback(guess, possible_words):
    pattern_groups = {}
    for answer in possible_words:
        pattern = get_feedback(guess, answer)
        pattern_groups.setdefault(pattern, []).append(answer)
    max_size = max(len(group) for group in pattern_groups.values())
    tied_best_patterns = [(pattern, group) for pattern, group in pattern_groups.items()
                          if len(group) == max_size]
    return random.choice(tied_best_patterns)