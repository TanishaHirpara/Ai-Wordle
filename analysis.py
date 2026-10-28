import json
import matplotlib.pyplot as plt

with open('results.json') as f:
    summary = json.load(f)

names = [s['agent'] for s in summary]
averages = [s['average_guesses'] for s in summary]
win_rates = [s['win_rate'] * 100 for s in summary]

print(f"{'agent':<20}{'avg guesses':<15}{'win rate':<12}{'time (s)'}")
for s in summary:
    print(f"{s['agent']:<20}{round(s['average_guesses'], 3):<15}{round(s['win_rate']*100, 1):<12}{round(s['duration'], 2)}")

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

axes[0].bar(names, averages, color='#4c72b0')
axes[0].set_title('Average Guesses per Agent')
axes[0].set_ylabel('Average Guesses')

axes[1].bar(names, win_rates, color='#55a868')
axes[1].set_title('Win Rate per Agent')
axes[1].set_ylabel('Win Rate (%)')
axes[1].set_ylim(0, 105)

plt.tight_layout()
plt.savefig('comparison.png')
print('saved comparison.png')

fig2, ax2 = plt.subplots(figsize=(8, 5))
for s in summary:
    ax2.hist(s['results'], bins=range(1, 8), alpha=0.5, label=s['agent'])
ax2.set_title('Distribution of Guesses Needed')
ax2.set_xlabel('Guesses Needed')
ax2.set_ylabel('Number of Games')
ax2.legend()
plt.tight_layout()
plt.savefig('distribution.png')
print('saved distribution.png')
