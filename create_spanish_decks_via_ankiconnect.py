"""
create_spanish_pronunciation_trainer_decks.py
---------------------------------------------
Creates the "Spanish Pronunciation Trainer" deck hierarchy in Anki via AnkiConnect,
using the model "Spanish Pronunciation Model (EN->ES TTS)".

Requirements:
    - Anki must be open
    - AnkiConnect add-on must be installed (ID: 2055492159)
"""

import requests
import json

ANKI_CONNECT_URL = "http://localhost:8765"

def invoke(action, **params):
    """Send a JSON-RPC request to AnkiConnect."""
    response = requests.post(ANKI_CONNECT_URL, json={"action": action, "version": 6, "params": params})
    response.raise_for_status()
    result = response.json()
    if result.get("error"):
        raise Exception(result["error"])
    return result.get("result")


# ---------- Deck Hierarchy ----------
ROOT_DECK = "Spanish Pronunciation Trainer"

SUBDECKS = [
    "Classroom Objects",
    "Grammar (Tener & Plurals)",
    "Requests & Needs",
    "Feelings & Concepts",
    "Virtues & Abstract Words",
    "Miscellaneous",
    "Common Verbs & Phrases",
    "Math & Quantities",
]

# Create root + subdecks
for subdeck in SUBDECKS:
    full_name = f"{ROOT_DECK}::{subdeck}"
    invoke("createDeck", deck=full_name)
    print(f"✅ Created deck: {full_name}")


# ---------- Helper: Add Note ----------
def add_note(deck_name, english, spanish, tags=None):
    """
    Adds a note using the custom model "Spanish Pronunciation Model (EN->ES TTS)".
    Fields: English, Spanish, Tags
    """
    note = {
        "deckName": deck_name,
        "modelName": "Spanish Pronunciation Model (EN->ES TTS)",
        "fields": {
            "English": english,
            "Spanish": spanish,
            "Tags": ", ".join(tags) if tags else "",
        },
        "options": {"allowDuplicate": False},
        "tags": tags or [],
    }
    return invoke("addNote", note=note)


# ---------- Example Notes ----------
examples = {
    "Classroom Objects": [
        ("pen", "bolígrafo"),
        ("pencil", "lápiz"),
    ],
    "Grammar (Tener & Plurals)": [
        ("I have a pen", "yo tengo un bolígrafo"),
        ("plural of lápiz", "lápices"),
    ],
    "Requests & Needs": [
        ("Can you lend me a blue pen?", "¿me dejas un boli azul?"),
    ],
    "Feelings & Concepts": [
        ("truth", "verdad"),
        ("love", "amor"),
    ],
    "Virtues & Abstract Words": [
        ("beauty", "belleza"),
        ("spirit", "espíritu"),
    ],
    "Miscellaneous": [
        ("How was it?", "¿Cómo fue?"),
    ],
    "Common Verbs & Phrases": [
        ("to leave", "dejar"),
        ("take (here you go)", "toma"),
    ],
    "Math & Quantities": [
        ("nine plus one equals ten", "nueve más uno = diez"),
    ],
}

# Add notes
for subdeck, cards in examples.items():
    deck_full = f"{ROOT_DECK}::{subdeck}"
    for en, es in cards:
        add_note(deck_full, en, es, tags=[subdeck.lower().replace(" ", "_")])
    print(f"🃏 Added {len(cards)} notes to {deck_full}")

print("\n🎉 All decks created successfully using model 'Spanish Pronunciation Model (EN->ES TTS)'!")
print("👉 Check Anki → Decks → 'Spanish Pronunciation Trainer' to confirm.")
