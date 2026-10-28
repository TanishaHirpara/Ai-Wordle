def load_words(path):
    with open(path) as f:
        return [w.strip() for w in f if w.strip()]

def get_feedback(guess, answer):
    result = ['gray'] * 5
    answer_letters = list(answer)
    for i in range(5):
        if guess[i] == answer[i]:
            result[i] = 'green'
            answer_letters[i] = None
    for i in range(5):
        if result[i] == 'green':
            continue
        if guess[i] in answer_letters:
            result[i] = 'yellow'
            answer_letters[answer_letters.index(guess[i])] = None
    return tuple(result)

def feedback_to_emoji(feedback):
    symbols = {'green': '🟩', 'yellow': '🟨', 'gray': '⬜'}
    return ''.join(symbols[f] for f in feedback)

def filter_candidates(candidates, guess, feedback):
    return [word for word in candidates if get_feedback(guess, word) == feedback]
