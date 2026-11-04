"""Check decks_data.py for duplicate English entries.

Two checks:
* the same English front twice within one deck;
* the same English front in two decks with *different* Spanish. Anki rejects a
  note whose first field already exists anywhere in the collection, so the
  second card is silently never added (and the sync can't tell which Spanish
  answer is meant).
"""
import sys
from decks_data import decks


def check_for_internal_duplicates(decks_data):
    problems = []
    for deck_name, cards in decks_data.items():
        seen = {}
        dupes = []
        for i, (english, spanish) in enumerate(cards):
            if english in seen:
                dupes.append((english, seen[english], i))
            else:
                seen[english] = i
        if dupes:
            problems.append((deck_name, dupes))
    return problems


def check_for_conflicting_fronts(decks_data):
    first = {}
    conflicts = []
    for deck_name, cards in decks_data.items():
        for english, spanish in cards:
            if english in first and first[english][1] != spanish:
                conflicts.append((english, first[english], (deck_name, spanish)))
            first.setdefault(english, (deck_name, spanish))
    return conflicts


problems = check_for_internal_duplicates(decks)
conflicts = check_for_conflicting_fronts(decks)

if problems:
    print("❌ Duplicates found:")
    for deck_name, dupes in problems:
        print(f"  {deck_name}:")
        for english, first_idx, second_idx in dupes:
            print(f"    '{english}' (lines {first_idx} and {second_idx})")

if conflicts:
    print("❌ Same English front with different Spanish in two decks (the second is never added to Anki):")
    for english, (deck_a, es_a), (deck_b, es_b) in conflicts:
        print(f"    '{english}': {deck_a} -> '{es_a}' | {deck_b} -> '{es_b}'")

if problems or conflicts:
    sys.exit(1)

print("✅ No duplicates found.")
