# AI Wordle Solver - Heuristic Search, Information Gain and Adversarial Reasoning

## What this project is

Four agents try to solve Wordle using different AI strategies, then get benchmarked
against each other over hundreds of simulated games. There is also an adversarial
mode where the secret word is not fixed in advance - the game instead always gives
whichever feedback keeps the largest number of words still possible.

## PEAS description

- Performance: solve the puzzle in as few guesses as possible, within 6 guesses
- Environment: the Wordle board and a hidden 5-letter answer
- Actuators: submitting a 5-letter word as a guess
- Sensors: green / yellow / gray feedback for each letter position

## The four agents

1. **Random** - picks any remaining possible word. Baseline only.
2. **Frequency** - scores words by how common their letters are among remaining
   candidates, picks the highest-scoring word.
3. **Candidate reduction (greedy/minimax)** - for every possible guess, simulates
   every possible feedback pattern and picks the guess that minimizes the
   worst-case number of words still possible afterward.
4. **Entropy / information gain** - for every possible guess, computes the
   Shannon entropy of the feedback-pattern distribution it would produce, and
   picks the guess expected to reveal the most information:
   `IG = -sum(p_i * log2(p_i))` over each possible feedback pattern.

For agents 3 and 4, guesses are chosen from the same list of words that are still
possible answers, rather than the full ~15,000-word guess dictionary. This is a
deliberate simplification that keeps the code simple and the runtime fast, and it
is the same simplification used by most published Wordle-solver writeups. The
first-turn guess for these two agents (`arise` and `raise`) is hardcoded because
it is always the same word every single game before any feedback exists — it is
the result of the full search, just precomputed once instead of recomputed
every simulation.

## Adversarial mode

`adversarial_agent.py` implements an "evil Wordle" opponent. Instead of checking
the guess against one fixed secret word, it looks at every word still consistent
with feedback given so far, groups them by what feedback pattern the current
guess would produce against each one, and returns whichever feedback pattern
keeps the biggest group alive. This is a search over feedback outcomes rather
than over guesses, and it makes solving noticeably harder — it is the same idea
behind the online game "Absurdle."

## Files

```
game.py                 core feedback function and word list loading
agents/random_agent.py
agents/frequency_agent.py
agents/candidate_agent.py
agents/entropy_agent.py
adversarial_agent.py    picks the hardest feedback instead of a fixed secret
adversarial_game.py     runs one adversarial game
demo.py                 runs one game with live turn-by-turn output
simulate.py             runs many games per agent and saves results.json
analysis.py             turns results.json into comparison.png and distribution.png
words/valid_answers.txt   2315 words — the original NYT Wordle answer list
words/valid_guesses.txt   full list of words accepted as valid guesses
```

## Word list source

Both word lists were pulled from public GitHub repositories:

- Guess dictionary: `tabatkins/wordle-list`
- Original answer list (2315 words): extracted from `steve-kasica/wordle-words`,
  keeping only rows that have a recorded day number, since that is exactly the
  original Wordle answer set before the NYT started drawing from a larger pool

## How to run it

```
python3 demo.py entropy              # single game, entropy agent, random secret
python3 demo.py entropy crane        # single game against a chosen secret word
python3 adversarial_game.py entropy  # adversarial mode, no fixed secret
python3 simulate.py 300              # simulate 300 games per agent, saves results.json
python3 analysis.py                  # builds comparison.png and distribution.png from results.json
```

Increase the sample size in `simulate.py` for a more rigorous result set if you
have time before submission — 300 games per agent already takes a few seconds
per agent and gives stable averages, but running the full 2315-word answer list
(`python3 simulate.py 2315`) is more defensible in a report if you can afford
the runtime.

## For the report

Suggested structure: problem statement -> PEAS -> state-space formulation
(candidate word set as state, guess as action, feedback as transition) ->
heuristic search formulation for the greedy agent -> information-gain math for
the entropy agent -> experimental setup and the comparison table/plots ->
adversarial extension -> conclusion. Tie each section back to the specific
lecture topics it maps to (intelligent agents, heuristic search, decision
theory / uncertain knowledge, evolutionary techniques if you add the GA
extension) since it shows you deliberately connected the project to the
syllabus rather than picking a project at random.
