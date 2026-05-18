"""Check decks_data.py for duplicate English entries within each deck."""
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


problems = check_for_internal_duplicates(decks)

if problems:
    print("❌ Duplicates found:")
    for deck_name, dupes in problems:
        print(f"  {deck_name}:")
        for english, first_idx, second_idx in dupes:
            print(f"    '{english}' (lines {first_idx} and {second_idx})")
    sys.exit(1)

print("✅ No duplicates found.")
