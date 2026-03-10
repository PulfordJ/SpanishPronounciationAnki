"""
create_full_spanish_pronunciation_trainer_decks.py
---------------------------------------------------
Fully rebuilds the "Spanish Pronunciation Trainer" deck hierarchy directly in Anki via AnkiConnect.
Auto-creates the model "Spanish Pronunciation Model (EN->ES TTS)" if not present.

Requirements:
    - Anki must be open
    - AnkiConnect add-on installed (ID: 2055492159)
"""

import requests
import time  # <-- add near the top with other imports
from decks_data import decks  # <-- Import your data dictionary

ANKI_CONNECT_URL = "http://localhost:8765"


def invoke(action, **params):
    """Send a JSON-RPC request to AnkiConnect."""
    response = requests.post(ANKI_CONNECT_URL, json={"action": action, "version": 6, "params": params})
    response.raise_for_status()
    result = response.json()
    if result.get("error"):
        raise Exception(result["error"])
    return result.get("result")


# ---------- Model Definition ----------
MODEL_NAME = "Spanish Pronunciation Model (EN->ES TTS)"


def ensure_model_exists():
    """Create model if missing."""
    existing_models = invoke("modelNames")
    if MODEL_NAME in existing_models:
        print(f"✅ Model already exists: {MODEL_NAME}")
        return

    print(f"⚙️ Creating model: {MODEL_NAME}")
    model = {
        "modelName": MODEL_NAME,
        "inOrderFields": ["English", "Spanish", "Tags"],
        "css": """
.card { font-family: -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; font-size: 22px; text-align: center; color: #111; background-color: #fff; }
hr { border: none; border-top: 1px solid #ddd; }
""",
        "cardTemplates": [
            {
                "Name": "EN->ES with TTS",
                "Front": "{{English}}",
                "Back": (
                    "{{FrontSide}}"
                    "<hr id='answer'>"
                    "<div>{{tts es_ES voices=Google :Spanish}}</div>"
                    "<div style='font-size:26px; margin-top:8px;'><b>{{Spanish}}</b></div>"
                    "<div style='font-size:18px; color:#666; margin-top:6px;'>({{English}})</div>"
                    "<br>"
                    "<div style='font-size:16px; color:#888; margin-top:10px;'>Latin American Spanish:</div>"
                    "<div>{{tts es_US voices=Google:Spanish}}</div>"
                ),
            }
        ],
    }
    invoke("createModel", **model)
    print(f"✅ Created model: {MODEL_NAME}")


# ---------- Decks ----------
ROOT_DECK = "Spanish Pronunciation Trainer"
SUBDECKS = list(decks.keys())  # <-- inferred automatically

def create_decks():
    """Create all subdecks in a single AnkiConnect multi call."""
    existing = set(invoke("deckNames"))
    actions = []

    for subdeck in SUBDECKS:
        full_name = f"{ROOT_DECK}::{subdeck}"
        if full_name not in existing:
            actions.append({"action": "createDeck", "params": {"deck": full_name}})

    if not actions:
        print("✅ All decks already exist; skipped creation.")
        return

    # Batch them via "multi"
    print(f"⚙️ Creating {len(actions)} new decks in one API call...")
    result = invoke("multi", actions=actions)
    print("✅ Deck creation complete.")
    for deck, status in zip([a["params"]["deck"] for a in actions], result):
        print(f"   • {deck} ({'ok' if status is None else status})")



# ---------- Helpers ----------
def find_existing_cards(deck_name):
    """Return a set of (English, Spanish) already in this deck."""
    ids = invoke("findCards", query=f'deck:"{deck_name}"')
    if not ids:
        return set()
    notes = invoke("notesInfo", notes=ids)
    existing = set()
    for n in notes:
        fields = n.get("fields", {})
        en = fields.get("English", {}).get("value", "").strip()
        es = fields.get("Spanish", {}).get("value", "").strip()
        existing.add((en, es))
    return existing


# ---------- Helper: Add Note ----------
def add_note(deck_name, english, spanish, tags=None):
    note = {
        "deckName": deck_name,
        "modelName": MODEL_NAME,
        "fields": {"English": english, "Spanish": spanish, "Tags": ", ".join(tags) if tags else ""},
        "options": {"allowDuplicate": False},
        "tags": tags or [],
    }
    invoke("addNote", note=note)


# ---------- Data (Existing + New) ----------
from textwrap import dedent




# ---------- Early Error Detection ----------
def check_for_internal_duplicates(decks_data):
    """Check for duplicate cards within each section that would cause silent failures."""
    problems = []
    
    for deck_name, cards in decks_data.items():
        seen_cards = {}
        section_duplicates = []
        
        for i, (english, spanish) in enumerate(cards):
            key = (english, spanish)
            if key in seen_cards:
                section_duplicates.append((key, seen_cards[key], i))
            else:
                seen_cards[key] = i
        
        if section_duplicates:
            problems.append((deck_name, section_duplicates))
    
    return problems

# ---------- Filter Notes with Multi ----------
def filter_addable_notes_all_decks(decks_data):
    """
    Run a single multi-call to check all notes across all decks using canAddNotesWithErrorDetail.
    Returns dict[deck_name] = (addable_notes, skipped_count)
    """
    multi_actions = []
    deck_keys = []
    for deck_name, cards in decks_data.items():
        full = f"{ROOT_DECK}::{deck_name}"
        notes = [
            {
                "deckName": full,
                "modelName": MODEL_NAME,
                "fields": {"English": en, "Spanish": es, "Tags": deck_name.lower().replace(" ", "_")},
                "options": {"allowDuplicate": False},
                "tags": [deck_name.lower().replace(" ", "_")],
            }
            for en, es in cards
        ]
        multi_actions.append({"action": "canAddNotesWithErrorDetail", "params": {"notes": notes}})
        deck_keys.append(deck_name)

    results = invoke("multi", actions=multi_actions)
    output = {}
    for deck_name, check_result, cards in zip(deck_keys, results, decks_data.values()):
        addable = []
        skipped = 0
        for (en, es), res in zip(cards, check_result):
            if res is None or not res.get("error"):
                addable.append(
                    {
                        "deckName": f"{ROOT_DECK}::{deck_name}",
                        "modelName": MODEL_NAME,
                        "fields": {"English": en, "Spanish": es, "Tags": deck_name.lower().replace(" ", "_")},
                        "options": {"allowDuplicate": False},
                        "tags": [deck_name.lower().replace(" ", "_")],
                    }
                )
            else:
                skipped += 1
        output[deck_name] = (addable, skipped)
    return output


# ---------- Add Notes in One Multi Call ----------
def add_notes_all_decks(filtered_results):

    total_added = 0
    total_skipped = 0

    """Batch-insert all addable notes across decks using one multi call."""
    multi_actions = []
    for deck_name, (addable, skipped) in filtered_results.items():
        if not addable:
            total_skipped += 1
            continue
        total_added += len(addable)
        multi_actions.append({"action": "addNotes", "params": {"notes": addable}})

    if not multi_actions:
        print("✅ No new cards to add — all duplicates skipped.")
        return

    print(f"⚙️ Adding notes for {len(multi_actions)} decks in one API call...")
    results = invoke("multi", actions=multi_actions)


    print(f"\n✅ Total added across all decks: {total_added} cards ({total_skipped} skipped).")



# ---------- Run ----------
def main():
    start_time = time.time()
    print("🔗 Connecting to AnkiConnect...")
    
    # Check for internal duplicates first (early error detection)
    print("🔍 Checking for internal duplicates that could cause silent failures...")
    duplicate_problems = check_for_internal_duplicates(decks)
    
    if duplicate_problems:
        print("❌ ERROR: Found internal duplicates that will prevent deck import:")
        for deck_name, duplicates in duplicate_problems:
            print(f"  • {deck_name}: {len(duplicates)} duplicate(s)")
            for (en, es), first_idx, second_idx in duplicates:
                print(f"    [{first_idx}] and [{second_idx}]: \"{en}\" → \"{es}\"")
        print("\n💡 Fix these duplicates in decks_data.py before running export.")
        print("🚫 ABORTING: Cannot proceed with duplicates present.")
        exit(1)
    
    print("✅ No internal duplicates found.")
    
    ensure_model_exists()
    create_decks()

    print("\n🔍 Checking which cards can be added...")
    filtered = filter_addable_notes_all_decks(decks)
    print("✅ Duplicate filtering complete.")

    print("\n🧩 Adding cards in bulk...")
    add_notes_all_decks(filtered)

    elapsed = time.time() - start_time
    minutes, seconds = divmod(elapsed, 60)
    print(f"\n🎉 Sync complete! Check Anki → Deck Browser → Spanish Pronunciation Trainer.")
    print(f"⏱️ Elapsed time: {int(minutes)}m {seconds:.1f}s")

if __name__ == "__main__":
    main()
