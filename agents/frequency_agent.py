from collections import Counter

def letter_scores(possible_words):
    counter = Counter()
    for word in possible_words:
        for letter in set(word):
            counter[letter] += 1
    return counter

def choose_guess(possible_words, all_guesses):
    scores = letter_scores(possible_words)
    best_word = None
    best_score = -1
    for word in possible_words:
        score = sum(scores[letter] for letter in set(word))
        if score > best_score:
            best_score = score
            best_word = word
    return best_word
