# KoWSD: Korean Word Sense Disambiguation — Project Brief

## Goal

Build a Korean word sense disambiguation (WSD) classifier using the National Institute of Korean Language (NIKL) "Modu Corpus" (모두의 말뭉치), and compare classical ML against a fine-tuned pretrained model.

Given a sentence and a target word, predict which dictionary sense (from 우리말샘) the word has in that context.

Example: in "배가 아파서 병원에 갔다", the target word "배" should map to the "body part" sense, not "fruit" or "ship".

The owner is a first-year CS student who wants hands-on ML experience and a portfolio project. Timeline: about 8 weeks, started 2026-10.

## Data

- Corpus: Lexical Sense Analysis corpus 2025 (어휘 의미 분석 말뭉치 2025), JSON format.
- Files seen so far: `NXLS*` and `SXLS*`. My guess (unverified): N = newspaper, S = spoken, LS = lexical sense. Check against the corpus documentation.
- Start with the `NXLS` files only. Keep `SXLS` (spoken) as an optional, separate test set for a later domain-transfer experiment. Do not mix them into training at first.
- Data lives in `data/`. It must never be committed or redistributed (corpus license).

### Observed structure (from a pasted, partly truncated sample)

```
data (dict): "id", "metadata", "document"
  document: probably a list of documents (NOT yet verified; could be a dict)
    each doc (dict): "id", "metadata", "paragraph", "sentence"
      sentence (list of dicts):
        "id", "form", "original_form",
        "word":  [{"id", "form", "begin", "end"}, ...]
        "wsd":   [{"form", "sense_id", "pos", "begin", "end", "word_id"}, ...]
```

Example `wsd` entry: `{"form": "보스턴", "sense_id": "002", "pos": "NNP", "begin": 1, "end": 4, "word_id": 1}`

Things to verify, not assume:
- The type of `data["document"]` (list or dict) and the exact key names (e.g. `wsd` vs `WSD`).
- `sense_id` is only meaningful together with `form`, so the label is the pair `(form, sense_id)`. Check whether `pos` is also needed to disambiguate.
- `begin`/`end` appear to index into the sentence `form` (not `original_form`, whose spacing can differ). Verify with `sent["form"][begin:end] == w["form"]` and report the match rate.
- `metadata.topic` looked unreliable (a business article labeled "미용/건강"). Do not use it as a feature.
- Nearly every word seems to carry a sense id, including words with only one sense. Single-sense words are useless for WSD and must be filtered out.

## Pipeline plan

1. **Parse** the JSON into rows of `(sentence, target form, pos, sense_id, begin, end)` and save to CSV. Keep the target position, since fine-tuning needs it later.
2. **Analyze and scope.** Count senses per word, examples per sense, and POS distribution. Select roughly 20–50 polysemous words (2+ senses, enough examples per sense). Split into train/validation/test without leaking the same sentence across splits.
3. **Baselines.** Majority-sense baseline per word, then TF-IDF on a context window around the target with logistic regression or SVM.
4. **Classical ML experiments.** Window size, morphological analysis vs. none, character n-grams, per-word models vs. one shared model.
5. **Fine-tune KcELECTRA** (Hugging Face Transformers, Colab free GPU). Try marking the target word in the input, for example with marker tokens around it.
6. **Error analysis.** Group errors (rare senses, near-synonymous senses, ambiguous labels).
7. **Compare and demo.** Plot majority vs. classical vs. KcELECTRA. Build a small Gradio demo (sentence + word in, predicted sense out).
8. **Write up.** README covering problem, data, method, results, limitations.

## Current status

Corpus access is approved and downloaded. Currently working on week 1: understanding the JSON structure and writing the parser.

## Constraints and working style

- Add `data/` to `.gitignore` before the first commit, along with `__pycache__/`, `.ipynb_checkpoints/`, `*.pt`, `*.safetensors`, `checkpoints/`. Never commit corpus text.
- Keep it simple. Write the minimum code that solves the task. No speculative features, abstractions, or configuration that was not asked for.
- State assumptions explicitly. If the data structure is ambiguous, inspect the real files and report what you found instead of guessing.
- Define a check for each step (for example the offset match rate, row counts, a few printed samples compared against the source) and run it.
- The owner is learning. Keep code readable and commented where the logic is not obvious, and explain non-trivial choices briefly. The owner reads Korean, so Korean explanations are welcome, but code and identifiers stay in English.
- Python with pandas, scikit-learn, and Hugging Face. Prefer pathlib and the standard `json` module for parsing.

## Immediate tasks for the agent

1. Inspect one `NXLS` file and report: top-level types and keys, the type of `document`, and the keys at each level down to a `wsd` entry.
2. Measure the `begin`/`end` offset match rate against `sentence["form"]`. Print a few mismatches if any.
3. Write `parse.py` that walks all `NXLS` files and writes `(sentence, form, pos, sense_id, begin, end)` rows to `data/processed/instances.csv`.
4. Produce summary stats: rows, distinct words, senses per word, examples per sense, POS counts. Report the share of words with 2+ senses.
5. Stop and report before choosing the polysemous-word subset, so the owner can decide the selection criteria.
