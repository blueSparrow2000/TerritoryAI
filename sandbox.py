from plotting import *

# plot helper
last_N_games = 10
oldest_index = 0
last_N_scores = []

mean_scores = []
scores = []
for score in range(32):
    mean_score = 0
    if len(last_N_scores) < last_N_games:
        last_N_scores.append(score)
        mean_score = sum(last_N_scores) / len(last_N_scores)
    else:
        last_N_scores[oldest_index] = score
        oldest_index = (oldest_index + 1) % last_N_games
        mean_score = sum(last_N_scores) / last_N_games

    scores.append(score)
    mean_scores.append(mean_score)

# print("Scores:      ", ' '.join('{:2d}.00'.format(s) for s in scores))
# print("Mean scores: ", ' '.join('{:05.2f}'.format(s) for s in mean_scores))











