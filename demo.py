import sys
import random
from game import load_words, get_feedback, feedback_to_emoji, filter_candidates
from agents import random_agent, frequency_agent, candidate_agent, entropy_agent
from agents.entropy_agent import expected_information

AGENTS = {
    'random': random_agent,
    'frequency': frequency_agent,
    'candidate': candidate_agent,
    'entropy': entropy_agent
}

def run_demo(agent_name, answer=None):
    all_answers = load_words('words/valid_answers.txt')
    all_guesses = load_words('words/valid_guesses.txt')
    agent = AGENTS[agent_name]
    if answer is None:
        answer = random.choice(all_answers)
    possible_words = list(all_answers)
    print('WORDLE AI DEMO')
    print('strategy:', agent_name)
    print('secret word chosen (for testing only):', answer.upper())
    print()
    for turn in range(1, 7):
        guess = agent.choose_guess(possible_words, all_guesses)
        info_line = ''
        if agent_name == 'entropy' and len(possible_words) > 1:
            bits = expected_information(guess, possible_words)
            info_line = f'  (expected information: {round(bits, 2)} bits)'
        print(f'turn {turn}: candidates remaining = {len(possible_words)}')
        print(f'guess: {guess.upper()}{info_line}')
        feedback = get_feedback(guess, answer)
        print(feedback_to_emoji(feedback))
        print()
        if feedback == ('green', 'green', 'green', 'green', 'green'):
            print(f'solved in {turn} guesses! word was {answer.upper()}')
            return
        possible_words = filter_candidates(possible_words, guess, feedback)
    print(f'failed to solve in 6 guesses, word was {answer.upper()}')

if __name__ == '__main__':
    agent_name = sys.argv[1] if len(sys.argv) > 1 else 'entropy'
    answer = sys.argv[2] if len(sys.argv) > 2 else None
    run_demo(agent_name, answer)
