import sys
from game import load_words, feedback_to_emoji
from adversarial_agent import choose_feedback
from agents import random_agent, frequency_agent, candidate_agent, entropy_agent

AGENTS = {
    'random': random_agent,
    'frequency': frequency_agent,
    'candidate': candidate_agent,
    'entropy': entropy_agent
}

def play_adversarial_game(agent, all_answers, all_guesses, max_guesses=6):
    possible_words = list(all_answers)
    for turn in range(max_guesses):
        guess = agent.choose_guess(possible_words, all_guesses)
        feedback, possible_words = choose_feedback(guess, possible_words)
        print('turn', turn + 1, 'guess:', guess.upper(), feedback_to_emoji(feedback), 'remaining candidates:', len(possible_words))
        if feedback == ('green', 'green', 'green', 'green', 'green'):
            print('solved in', turn + 1, 'guesses, word was', guess.upper())
            return turn + 1, True
        if len(possible_words) == 0:
            print('no consistent word left')
            return turn + 1, False
    print('failed within', max_guesses, 'guesses, remaining candidates sample:', possible_words[:10])
    return max_guesses, False

if __name__ == '__main__':
    all_answers = load_words('words/valid_answers.txt')
    all_guesses = load_words('words/valid_guesses.txt')
    agent_name = sys.argv[1] if len(sys.argv) > 1 else 'entropy'
    play_adversarial_game(AGENTS[agent_name], all_answers, all_guesses)
