# HistWords ACL 2016 Reproduction Notes

Paper: *Diachronic Word Embeddings Reveal Statistical Laws of Semantic Change* (ACL 2016)

## Official resources

- Code repository: `https://github.com/williamleif/histwords`
- Project page: `https://nlp.stanford.edu/projects/histwords/`
- Official pretrained embeddings:
  - `http://snap.stanford.edu/historical_embeddings/eng-fiction-all_sgns.zip`
  - `http://snap.stanford.edu/historical_embeddings/coha-word_sgns.zip`
  - `http://snap.stanford.edu/historical_embeddings/coha-lemma_sgns.zip`
  - `http://snap.stanford.edu/historical_embeddings/eng-all_sgns.zip`

## Local paths prepared in this workspace

- Repo root: `/Users/sdf/Desktop/语义计算/histwords`
- Python env: `/Users/sdf/Desktop/语义计算/histwords/.venv`
- Downloaded data:
  - `/Users/sdf/Desktop/语义计算/histwords/embeddings/eng-fiction-all_sgns.zip`
  - `/Users/sdf/Desktop/语义计算/histwords/embeddings/coha-word_sgns.zip`
- Extracted data:
  - `/Users/sdf/Desktop/语义计算/histwords/embeddings/eng-fiction-all_sgns`
  - `/Users/sdf/Desktop/语义计算/histwords/embeddings/coha-word_sgns`

## Notes on compatibility

The official repository targets Python 2.7. Minimal Python 3 compatibility fixes were applied only to make the official example and evaluation scripts run in the current environment. The embedding files and algorithms were not changed.

## Commands verified locally

Activate env:

```bash
source /Users/sdf/Desktop/语义计算/histwords/.venv/bin/activate
cd /Users/sdf/Desktop/语义计算/histwords
```

Run the official example:

```bash
python example.py
```

Observed output:

```text
Similarity between gay and lesbian drastically increases from 1950s to the 1990s:
1950, cosine similarity=0.00
1960, cosine similarity=0.00
1970, cosine similarity=0.34
1980, cosine similarity=0.43
1990, cosine similarity=0.68
```

Run the official word similarity evaluation:

```bash
python -m vecanalysis.ws_eval embeddings/eng-fiction-all_sgns/1990 \
  vecanalysis/simtestsets/ws/bruni_men.txt --type SGNS
```

Observed output:

```text
OOV:  31
Correlation: 0.6361379479106024
```

## About the dataset

There are two levels of “data” in this project:

1. Pretrained historical embeddings: directly downloadable and already obtained locally.
2. Raw corpora used to train them:
   - Google Ngrams: public and scriptable.
   - COHA: referenced by the official repo, but the raw corpus is managed externally and may require separate access or license terms.

## Recommended next step for a fuller reproduction

If the goal is to reproduce the paper more closely rather than only run the official examples, the next step is to reimplement the paper's statistical-law analyses on top of the downloaded embeddings:

- semantic change rate vs. frequency
- semantic change rate vs. polysemy
- nearest-neighbor drift across decades

The current repo does not ship a full end-to-end notebook for those ACL 2016 figures, so that part needs to be reconstructed from the paper description.
