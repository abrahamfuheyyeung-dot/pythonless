import csv
import re
from pathlib import Path

import spacy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

BASE = Path(__file__).parent
CSV_PATH = BASE / "IMDB Dataset.csv"
OUT_PATH = BASE / "sentiment_comparison.csv"

# "Personal belief" carries more weight than "descriptor of movie".
WEIGHTS = {"personal": 0.7, "descriptor": 0.3}

NLP = spacy.load("en_core_web_sm")


def is_first_person_subject(token):
    return token.dep_ in ("nsubj", "nsubjpass") and "1" in token.morph.get("Person")


def is_personal_belief(token):
    """True when the term sits in a clause whose subject is the reviewer (I/we),
    e.g. "I loved it" or "I think it's great". Decided by the dependency parse."""
    return any(
        is_first_person_subject(child)
        for node in (token, *token.ancestors)
        for child in node.children
    )


def is_negated(token):
    return any(c.dep_ == "neg" for c in token.children) or any(
        c.dep_ == "neg" for c in token.head.children
    )


def categorize_terms(analyzer, text):
    """Return {'personal': [(term, valence)], 'descriptor': [...]} for sentiment-bearing terms."""
    text = re.sub(r"<[^>]+>", " ", text)
    terms = {"personal": [], "descriptor": []}
    for token in NLP(text):
        valence = analyzer.lexicon.get(token.lower_)
        if not valence or token.is_stop and token.pos_ not in ("ADJ", "ADV", "VERB"):
            continue
        if is_negated(token):
            valence = -valence * 0.74
        category = "personal" if is_personal_belief(token) else "descriptor"
        terms[category].append((token.lower_, valence / 4))
    return terms


def category_score(items):
    """Mean valence in [-1, 1], or None when the category has no terms."""
    return sum(v for _, v in items) / len(items) if items else None


def evaluate(analyzer, text):
    terms = categorize_terms(analyzer, text)
    scores = {c: category_score(items) for c, items in terms.items()}
    present = {c: s for c, s in scores.items() if s is not None}
    if not present:
        return terms, scores, 0.0
    weight_sum = sum(WEIGHTS[c] for c in present)
    overall = sum(WEIGHTS[c] * s for c, s in present.items()) / weight_sum
    return terms, scores, overall


def polarity(score):
    return "positive" if score >= 0 else "negative"


def fmt(score):
    return "n/a" if score is None else round(score, 4)


def main():
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        rows = [r for _, r in zip(range(2), csv.DictReader(f))]

    analyzer = SentimentIntensityAnalyzer()
    results = [evaluate(analyzer, r["review"]) for r in rows]
    overall = [res[2] for res in results]
    matches = polarity(overall[0]) == polarity(overall[1])
    difference = abs(overall[0] - overall[1])

    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Review Row", "Personal Belief Score", "Movie Descriptor Score",
            "Weighted Score", "Matches Row 2", "How Far Off",
        ])
        for n, (terms, scores, score) in enumerate(results, start=1):
            if n == 1:
                writer.writerow([n, fmt(scores["personal"]), fmt(scores["descriptor"]),
                                 round(score, 4), "Yes" if matches else "No", round(difference, 4)])
            else:
                writer.writerow([n, fmt(scores["personal"]), fmt(scores["descriptor"]),
                                 round(score, 4), "-", "-"])

    for n, (row, (terms, scores, score)) in enumerate(zip(rows, results), start=1):
        print(f"Row {n}: weighted {score:+.4f} ({polarity(score)}), dataset label: {row['sentiment']}")
        for cat in ("personal", "descriptor"):
            words = ", ".join(f"{t}({v:+.2f})" for t, v in terms[cat])
            print(f"  {cat} [{fmt(scores[cat])}]: {words}")
    print(f"Matches: {matches} | Difference: {difference:.4f}")
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
