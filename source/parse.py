"""Parse NIKL Word Sense Tagged Corpus 2025 (NXLS = newspaper) into a flat CSV.

One row per WSD annotation:
    sentence_id, sentence, form, pos, sense_id, begin, end

Notes (verified on NXLS2502512313.json):
- The annotation list key is "WSD" (uppercase).
- `form` is the dictionary form (lemma), e.g. "오르". For verbs/adjectives the
  text at sentence[begin:end] is the inflected surface form ("오른"), so the
  two often differ. For nouns they match ~99.9% of the time.
- Special sense ids 777 / 888 / 999 are kept here as-is; filtering is done in
  the analysis step, not in the parser.

Run from the project root:  python source/parse.py
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "NIKL_LS_2025_v1.0"
OUT_PATH = ROOT / "data" / "processed" / "instances.csv"

COLUMNS = ["sentence_id", "sentence", "form", "pos", "sense_id", "begin", "end"]


def iter_rows(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    for doc in data["document"]:
        for sent in doc["sentence"]:
            for w in sent["WSD"]:
                yield {
                    "sentence_id": sent["id"],
                    # begin/end index into "form", not "original_form"
                    "sentence": sent["form"],
                    "form": w["form"],
                    "pos": w["pos"],
                    "sense_id": w["sense_id"],
                    "begin": w["begin"],
                    "end": w["end"],
                }


def main():
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    n_rows = 0
    with OUT_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        for path in sorted(DATA_DIR.glob("NXLS*.json")):
            n_file = 0
            for row in iter_rows(path):
                writer.writerow(row)
                n_file += 1
            print(f"{path.name}: {n_file} rows")
            n_rows += n_file
    print(f"total: {n_rows} rows -> {OUT_PATH}")


if __name__ == "__main__":
    main()
