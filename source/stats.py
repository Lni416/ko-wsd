"""Summary statistics for data/processed/instances.csv.

A "word" is the lemma `form`; a sense label is the pair (form, sense_id).
Special sense ids (777, 888, 999) are not dictionary senses, so they are
excluded from the sense statistics and reported separately.

Run from the project root:  python source/stats.py
"""
import csv
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IN_PATH = ROOT / "data" / "processed" / "instances.csv"
SPECIAL_IDS = {"777", "888", "999"}


def main():
    # csv reads every value as str, so sense_id keeps its leading zeros ("002").
    with IN_PATH.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    print(f"rows: {len(rows)}")
    print(f"sentences: {len({r['sentence_id'] for r in rows})}")

    special = Counter(r["sense_id"] for r in rows if r["sense_id"] in SPECIAL_IDS)
    print(f"special sense ids (excluded below): {dict(special)}")
    rows = [r for r in rows if r["sense_id"] not in SPECIAL_IDS]
    print(f"rows with a real sense id: {len(rows)}")

    print("\nPOS counts:")
    for pos, c in Counter(r["pos"] for r in rows).most_common():
        print(f"  {pos:5} {c}")

    # Is POS needed in the label? Check whether one (form, sense_id) pair
    # shows up with more than one POS tag.
    pos_of_label = defaultdict(set)
    for r in rows:
        pos_of_label[(r["form"], r["sense_id"])].add(r["pos"])
    multi_pos = {k: v for k, v in pos_of_label.items() if len(v) > 1}
    print(f"\n(form, sense_id) pairs seen with >1 POS: {len(multi_pos)} of {len(pos_of_label)}")
    for k, v in list(multi_pos.items())[:5]:
        print(f"  {k}: {sorted(v)}")

    # senses[form] = Counter of sense_id -> number of examples
    senses = defaultdict(Counter)
    for r in rows:
        senses[r["form"]][r["sense_id"]] += 1

    n_words = len(senses)
    poly = {w: c for w, c in senses.items() if len(c) >= 2}
    poly_tokens = sum(sum(c.values()) for c in poly.values())
    print(f"\ndistinct words (form): {n_words}")
    print(f"distinct senses (form, sense_id): {len(pos_of_label)}")
    print(f"words with 2+ senses: {len(poly)} ({len(poly) / n_words:.1%} of words, "
          f"{poly_tokens / len(rows):.1%} of rows)")

    print("\nsenses per word:")
    for k, c in sorted(Counter(len(c) for c in senses.values()).items()):
        print(f"  {k} senses: {c} words")

    ex_per_sense = sorted(n for c in senses.values() for n in c.values())
    def pct(p):
        return ex_per_sense[int(p * (len(ex_per_sense) - 1))]
    print(f"\nexamples per sense: median {pct(0.5)}, p90 {pct(0.9)}, p99 {pct(0.99)}, "
          f"max {ex_per_sense[-1]}, senses with 1 example: {ex_per_sense.count(1)}")

    # How many candidate words survive different "enough examples" thresholds?
    # A word qualifies if at least 2 of its senses have >= min_ex examples.
    print("\ncandidate words by threshold (>=2 senses with >= N examples each):")
    for min_ex in (5, 10, 20, 30, 50):
        cands = [w for w, c in poly.items() if sum(n >= min_ex for n in c.values()) >= 2]
        print(f"  N={min_ex:3}: {len(cands)} words")

    print("\ntop 30 polysemous words by frequency (form: total | sense counts):")
    top = sorted(poly.items(), key=lambda kv: -sum(kv[1].values()))[:30]
    for w, c in top:
        print(f"  {w}: {sum(c.values())} | {dict(c.most_common())}")


if __name__ == "__main__":
    main()
