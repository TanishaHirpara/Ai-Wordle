# AI Wordle Solver: Heuristic Search, Information Gain and Adversarial Reasoning

An AISC (CSE3121) project. Four AI agents solve Wordle using different strategies and are benchmarked against each other over every word in the original answer list. An adversarial "Evil Wordle" opponent and a web interface let you watch, use and play against the agents.

**Contents:** [Features](#features) · [Results](#results) · [PEAS description](#peas-description) · [Agent design](#agent-design) · [Adversarial mode](#adversarial-mode) · [The website](#the-website) · [Setup and running](#setup-and-running) · [Testing](#testing) · [Limitations](#limitations)

## Features

- Four solving agents: random, letter frequency, candidate reduction (minimax) and entropy (information gain)
- Benchmark over all 2315 answers with average guesses, win rate and guess histograms
- Adversarial opponent that never commits to a secret and always gives the hardest honest feedback
- Web interface with four tabs: watch the AI solve, get help with a real Wordle, play Evil Wordle, view benchmark charts
- Command-line demo for a single game with live turn-by-turn output

## Results

All 2315 answers, each tested once per agent (`python simulate.py 2315`). A win means solved within 6 guesses.

| Agent | Average guesses | Win rate |
|---|---|---|
| Entropy (information gain) | 3.594 | 99.5% |
| Candidate reduction (minimax) | 3.671 | 99.4% |
| Frequency | 3.672 | 99.0% |
| Random | 4.079 | 98.4% |

Entropy is best because it optimises the average case directly, and average guesses is the score being compared. Candidate reduction only protects against the worst case, so it wins more games than frequency but does not need fewer guesses on average. The sample is seeded, so a rerun gives the same numbers. Runtimes depend on your machine.

## Project structure

```
wordle_ai/
  game.py                  feedback rules, word loading, candidate filtering
  agents/
    random_agent.py
    frequency_agent.py
    candidate_agent.py
    entropy_agent.py
  adversarial_agent.py     picks the hardest feedback
  adversarial_game.py      one adversarial game in the terminal
  demo.py                  one game with turn-by-turn output
  simulate.py              benchmark, writes results.json
  analysis.py              writes comparison.png and distribution.png
  app.py                   Flask server and API for the website
  static/
    index.html             the website (single file, vanilla JavaScript)
  words/
    valid_answers.txt      2315 original Wordle answers
    valid_guesses.txt      about 14,855 accepted guesses
  results.json             created by simulate.py
```

## PEAS description

| Element | Wordle solver |
|---|---|
| **P**erformance measure | Solve the puzzle in as few guesses as possible, within the limit of 6. Agents are compared by average guesses and win rate |
| **E**nvironment | The Wordle board and a hidden 5-letter answer from the 2315-word list. In adversarial mode the answer is not fixed: the environment keeps the set of words still consistent with the feedback |
| **A**ctuators | Submitting a 5-letter word as a guess |
| **S**ensors | The green, yellow or gray feedback for each letter position |

Environment properties:

- Partially observable: the secret word is hidden, and only the feedback reveals information about it
- Deterministic: the feedback is fully decided by the guess and the secret
- Sequential: each guess changes what the agent knows, so earlier guesses affect later ones
- Static: the board does not change while the agent is choosing
- Discrete: finite words and three feedback colours
- Single agent in normal mode, and a competitive two-agent setting in adversarial mode

Agent types: the random agent has no model of the game. The frequency and candidate-reduction agents are goal-based, scoring guesses with a heuristic. The entropy agent is utility-based, because it scores each guess by its expected information gain.

## Agent design

Every agent runs the same loop. Only the step that picks the guess differs.

```
list of possible words -> agent picks a guess -> game returns green/yellow/gray
        ^                                                    |
        +---- keep only words that would give that feedback -+
```

State is the list of words that could still be the answer. An action is a guess, and the feedback is the transition: `filter_candidates` keeps only the words that would have produced the feedback that was seen.

| Agent | Heuristic used to pick the guess |
|---|---|
| Random | None. Any remaining word. |
| Frequency | Sum, over the word's distinct letters, of how many remaining words contain that letter. Highest wins. |
| Candidate reduction | For each guess, the size of the largest group of words sharing one feedback pattern. Smallest wins (minimax). |
| Entropy | H = −Σ p·log₂(p) over the feedback patterns the guess can produce. Highest wins. |

The candidate and entropy agents hardcode their first guess (`arise` and `raise`). It is the same word every game, so it is computed once instead of 2315 times. Those two agents choose guesses only from the remaining candidates, not from the full guess list. This keeps the code simple and fast, but it means the results are slightly worse than an agent allowed to guess any word.

## Adversarial mode

`adversarial_agent.py` has no fixed secret. It groups every word still consistent with earlier feedback by the pattern the current guess would produce, and returns the pattern with the largest group. It never lies, since every word in that group is a valid answer. It maximises the same group size that the candidate agent minimises, which makes the two a minimax pair.

## The website

Run the server and open `http://127.0.0.1:5000`. Do not open `index.html` by double-clicking, because browsers block a page opened from disk from calling the server.

| Tab | What it does | API used |
|---|---|---|
| Watch the AI solve | Pick an agent and a secret word from the answer list, then watch the guesses animate with candidates remaining | `POST /api/solve` |
| Help me solve my Wordle | The AI suggests a guess, you click the tiles to match the colours you got elsewhere, and it suggests the next one | `POST /api/suggest` |
| Play Evil Wordle | Type your own guesses against the adversary | `POST /api/adversarial` |
| Results | Table and charts built from `results.json` | `GET /api/results` |

The server keeps no game state. For suggest and adversarial, the page sends the whole history every time and the server replays it with `filter_candidates`. Feedback is always an array of five strings, each `"green"`, `"yellow"` or `"gray"`. Errors come back as HTTP 400 with `{"error": "message"}`, which the page shows in a banner.

| Endpoint | Request body | Response |
|---|---|---|
| `POST /api/solve` | `{"agent": "entropy", "secret": "crane"}` | `{"solved": true, "turns": [{"guess", "feedback", "remaining"}]}` |
| `POST /api/suggest` | `{"agent": "entropy", "history": [{"guess", "feedback"}]}` | `{"guess", "remaining", "words"}` |
| `POST /api/adversarial` | `{"history": [...], "guess": "slate"}` | `{"feedback", "remaining", "solved"}` |
| `GET /api/results` | none | list of `{agent, average_guesses, win_rate, duration, results}` |

Agent names: `random`, `frequency`, `candidate` (or `candidate_reduction`), `entropy`. The secret word must be in the 2315-word answer list, and Evil Wordle guesses must be valid words.

## Setup and running

Python 3.8 or newer. Use `python3` instead of `python` on macOS and Linux.

```
pip install flask matplotlib
python simulate.py 2315
python analysis.py
python app.py
```

`simulate.py 2315` takes about 90 seconds and creates `results.json`, which the Results tab needs. Then open `http://127.0.0.1:5000`. The charts load Chart.js from a CDN, so they need an internet connection.

Command-line tools:

```
python demo.py entropy crane
python adversarial_game.py entropy
python simulate.py 300
```

## Testing

Benchmark: every agent plays the same words with a fixed seed (`random.seed(42)`). The candidate pool stays in its original order, and only the list of test words is sampled with `random.sample`. Small samples are noisy, so use the full 2315 for any numbers you report.

Website API, with the server running (Command Prompt):

```
curl.exe -X POST http://127.0.0.1:5000/api/solve -H "Content-Type: application/json" -d "{\"agent\":\"entropy\",\"secret\":\"crane\"}"
```
Expect three turns: raise, grace, crane, with `"solved":true`.

```
curl.exe -X POST http://127.0.0.1:5000/api/solve -H "Content-Type: application/json" -d "{\"agent\":\"entropy\",\"secret\":\"zzzzz\"}"
```
Expect HTTP 400 with an error message.

```
curl.exe http://127.0.0.1:5000/api/results
```
Expect the four agents. In PowerShell, put the JSON in a file and send it with `-d "@body.json"`.

Browser checklist: solve `crane` with each agent; in the help tab, enter impossible colours and confirm you get an error and the last row is undone; in Evil Wordle, try a non-word and confirm it is rejected; switch the theme and confirm the charts redraw.

## Limitations

- Agents guess only from remaining candidates, and look one step ahead
- Every remaining answer is treated as equally likely
- The answer list has 2315 words, so the website cannot solve words outside it
- No alpha-beta pruning is used. The adversary is a one-ply maximiser
- As far as I know, optimal play with the full guess list averages about 3.4 guesses, so results here are expected to be somewhat higher

## Mapping to the syllabus

- Intelligent agents, PEAS and agent types: the PEAS description and agent design above
- Problem solving, state space and heuristic search: candidate set as state, guess as action, heuristic scoring of guesses
- Game playing and minimax: candidate reduction and the adversary
- Uncertain knowledge and decision theory: entropy agent, belief update by filtering

## Word list sources

- Guess dictionary: `tabatkins/wordle-list` on GitHub
- Original answer list (2315 words): from `steve-kasica/wordle-words`, keeping only rows with a recorded day number

## Troubleshooting

| Problem | Fix |
|---|---|
| "Cannot reach the server" or fetch errors | Start `python app.py` and open `http://127.0.0.1:5000` |
| Results tab shows an error | Run `python simulate.py 2315` first |
| `FileNotFoundError: words/valid_answers.txt` | Run `python app.py` from the `wordle_ai` folder |
| Charts do not appear | Check your internet connection (Chart.js is loaded from a CDN) |
| "That word is not in the answer list" | Pick a word from `words/valid_answers.txt` |

## Suggested report outline

Problem statement, PEAS description, state-space formulation, heuristics for each agent, the information-gain mathematics, the experimental setup and results table with charts, the adversarial extension, the website architecture, limitations, conclusion.
