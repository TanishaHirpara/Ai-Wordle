import sys
import time
import json
import random
from game import load_words, get_feedback, filter_candidates
from agents import random_agent, frequency_agent, candidate_agent, entropy_agent

def play_game(agent, answer, all_answers, all_guesses, max_guesses=6):
    possible_words = list(all_answers)
    guesses_made = 0
    for turn in range(max_guesses):
        guess = agent.choose_guess(possible_words, all_guesses)
        guesses_made += 1
        feedback = get_feedback(guess, answer)
        if feedback == ('green', 'green', 'green', 'green', 'green'):
            return guesses_made, True
        possible_words = filter_candidates(possible_words, guess, feedback)
    return guesses_made, False

def run_simulation(agent, agent_name, all_answers, all_guesses, test_words):
    results = []
    wins = 0
    start = time.time()
    for i, answer in enumerate(test_words):
        guesses_made, won = play_game(agent, answer, all_answers, all_guesses)
        results.append(guesses_made)
        if won:
            wins += 1
        print(agent_name, i + 1, '/', len(test_words), answer, guesses_made, won)
    duration = time.time() - start
    average_guesses = sum(results) / len(results)
    win_rate = wins / len(results)
    return {
        'agent': agent_name,
        'average_guesses': average_guesses,
        'win_rate': win_rate,
        'results': results,
        'duration': duration
    }

if __name__ == '__main__':
    all_answers = load_words('words/valid_answers.txt')
    all_guesses = load_words('words/valid_guesses.txt')
    sample_size = int(sys.argv[1]) if len(sys.argv) > 1 else 200

    random.seed(42)
    test_words = random.sample(all_answers, sample_size)

    agents_to_test = [
        (random_agent, 'random'),
        (frequency_agent, 'frequency'),
        (candidate_agent, 'candidate_reduction'),
        (entropy_agent, 'entropy')
    ]

    summary = []
    for agent, name in agents_to_test:
        stats = run_simulation(agent, name, all_answers, all_guesses, test_words)
        summary.append(stats)

    with open('results.json', 'w') as f:
        json.dump(summary, f)

    print('---SUMMARY---')
    for s in summary:
        print(s['agent'], 'avg guesses:', round(s['average_guesses'], 3), 'win rate:', s['win_rate'], 'time:', round(s['duration'], 2))

