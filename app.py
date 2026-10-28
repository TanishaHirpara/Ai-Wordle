import os
import json
from flask import Flask, request, jsonify, send_from_directory

from game import load_words, get_feedback, filter_candidates
from adversarial_agent import choose_feedback
from agents import random_agent, frequency_agent, candidate_agent, entropy_agent

app = Flask(__name__, static_folder='static')

# Load words at startup
ALL_ANSWERS = load_words('words/valid_answers.txt')
ALL_GUESSES = load_words('words/valid_guesses.txt')

AGENTS = {
    'random': random_agent,
    'frequency': frequency_agent,
    'candidate': candidate_agent,
    'candidate_reduction': candidate_agent,
    'entropy': entropy_agent
}

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
    return response

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

@app.route('/api/solve', methods=['POST', 'OPTIONS'])
def solve():
    if request.method == 'OPTIONS':
        return ('', 204)
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Invalid JSON body'}), 400
    
    agent_name = data.get('agent')
    secret = (data.get('secret') or '').strip().lower()

    if agent_name not in AGENTS:
        return jsonify({'error': f"Unknown agent: '{agent_name}'. Choose from: {list(AGENTS.keys())}"}), 400
    
    if len(secret) != 5 or not secret.isalpha():
        return jsonify({'error': 'Secret word must be exactly 5 letters'}), 400
    
    agent = AGENTS[agent_name]
    possible_words = list(ALL_ANSWERS)
    turns = []
    solved = False
    max_guesses = 6

    for _ in range(max_guesses):
        if not possible_words:
            break
        guess = agent.choose_guess(possible_words, ALL_GUESSES)
        feedback = list(get_feedback(guess, secret))
        turns.append({
            'guess': guess,
            'feedback': feedback,
            'remaining': len(possible_words)
        })
        if feedback == ['green', 'green', 'green', 'green', 'green']:
            solved = True
            break
        possible_words = filter_candidates(possible_words, guess, tuple(feedback))

    return jsonify({'solved': solved, 'turns': turns})

@app.route('/api/suggest', methods=['POST', 'OPTIONS'])
def suggest():
    if request.method == 'OPTIONS':
        return ('', 204)
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Invalid JSON body'}), 400
    
    agent_name = data.get('agent')
    history = data.get('history', [])

    if agent_name not in AGENTS:
        return jsonify({'error': f"Unknown agent: '{agent_name}'"}), 400
    
    agent = AGENTS[agent_name]
    possible_words = list(ALL_ANSWERS)

    for item in history:
        guess = item.get('guess', '').strip().lower()
        feedback = tuple(item.get('feedback', []))
        if len(guess) != 5 or len(feedback) != 5:
            return jsonify({'error': 'Each history entry must have a 5-letter guess and 5 feedback strings'}), 400
        possible_words = filter_candidates(possible_words, guess, feedback)

    if not possible_words:
        return jsonify({'guess': '', 'remaining': 0, 'words': []})

    next_guess = agent.choose_guess(possible_words, ALL_GUESSES)
    return jsonify({
        'guess': next_guess,
        'remaining': len(possible_words),
        'words': possible_words[:20]
    })

@app.route('/api/adversarial', methods=['POST', 'OPTIONS'])
def adversarial():
    if request.method == 'OPTIONS':
        return ('', 204)
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Invalid JSON body'}), 400
    
    history = data.get('history', [])
    guess = (data.get('guess') or '').strip().lower()

    if len(guess) != 5 or not guess.isalpha():
        return jsonify({'error': 'Guess must be exactly 5 letters'}), 400

    possible_words = list(ALL_ANSWERS)
    for item in history:
        prev_guess = item.get('guess', '').strip().lower()
        prev_feedback = tuple(item.get('feedback', []))
        possible_words = filter_candidates(possible_words, prev_guess, prev_feedback)

    if not possible_words:
        return jsonify({'error': 'No words remaining consistent with history'}), 400

    feedback_tuple, remaining_group = choose_feedback(guess, possible_words)
    feedback_list = list(feedback_tuple)
    is_solved = (feedback_list == ['green', 'green', 'green', 'green', 'green'])

    return jsonify({
        'feedback': feedback_list,
        'remaining': len(remaining_group),
        'solved': is_solved
    })

@app.route('/api/results', methods=['GET', 'OPTIONS'])
def results():
    if request.method == 'OPTIONS':
        return ('', 204)
    if os.path.exists('results.json'):
        with open('results.json', 'r') as f:
            data = json.load(f)
        return jsonify(data)
    else:
        return jsonify({'error': 'results.json not found. Run simulate.py first.'}), 404

if __name__ == '__main__':
    print("Starting Wordle AI server at http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)
