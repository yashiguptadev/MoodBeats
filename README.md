# MoodTune — Mood-Based AI Music Recommendation System

## Run locally
Requires Python 3.10+.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000

## Algorithms used (for viva)
1. **AI approach:** content-based recommendation using mood, energy, valence and genre.
2. **Heuristic search:** weighted similarity score; rank candidate songs by estimated match.
3. **Fuzzy logic:** triangular overlapping membership functions for each mood. Handles partial membership rather than strict labels.
4. **Neural network:** scikit-learn MLPClassifier with two hidden layers, trained on a small curated demonstration dataset to estimate mood class probabilities. This is illustrative, NOT a validated model or proof of generalization.
5. **Genetic algorithm:** chromosomes are five unique song IDs. Tournament selection chooses parents; one-point crossover, duplicate repair, mutation and elitism evolve playlist quality and artist variety.
6. **Adversarial search:** a two-ply minimax *simulation*: MAX selects a song, MIN chooses the worst among synthetic listener responses. The utility is a defined pedagogical score, not real-world listener prediction.
7. **Implementation:** Flask JSON API + HTML/CSS/JavaScript responsive UI.

### Score formula
Heuristic = 0.52 * energy similarity + 0.28 * valence similarity + 0.20 * genre match.
Final = 0.55 * heuristic + 0.25 * fuzzy mood membership + 0.20 * neural mood probability.

### Limitations
- Dataset consists of 20 hand-curated demonstration records. Energy/valence values are illustrative.
- Song links search YouTube; no audio streaming or API integration is implemented.
- Mood is manually selected, not detected from facial expressions or medical signals.
- The MLP trains on the same tiny catalogue used for recommendation. No held-out accuracy claims are made.
- Adversarial responses are simulated and the minimax stage is mainly educational.
- To build a production system, obtain properly licensed song features, a larger training set, a test split, and real user feedback.

## Viva questions
**Q: Why fuzzy logic?** A: Mood boundaries overlap; fuzzy membership captures degrees of fit.
**Q: What is a chromosome?** A: A sequence of unique song IDs representing one playlist.
**Q: What does minimax mean here?** A: Choose the recommendation maximizing utility under the worst modeled listener response.
**Q: What does the neural network predict?** A: Probabilities of five mood labels based on the song's numeric features and genre.
**Q: Is this Spotify?** A: No, it's a standalone educational recommender with YouTube search links.

## Genetic Algorithm Working visualizer
After clicking **Recommend my songs**, click **🧬 View Genetic Algorithm Working** under the playlist. The visualizer shows real initial/final best playlists, the fitness formula, population size, selection/crossover/mutation settings, and a slider to inspect all 35 generations. Each generation records one actual reproduction example (two parents, crossover child, whether mutation occurred, and resulting child), plus the best and average fitness before reproduction. The displayed example may have no mutation because mutation is probabilistic.
