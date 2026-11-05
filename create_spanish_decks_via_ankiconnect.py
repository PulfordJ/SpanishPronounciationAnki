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

import tts_audio  # embedded-audio generation + content-addressed cache
import tag_mapping  # Aula Internacional Plus 1 unit/skill/priority tags
import card_migrations  # renamed / retired English fronts for notes already in Anki

ANKI_CONNECT_URL = "http://localhost:8765"

# Audio fields hold a `[sound:...]` reference to a pre-generated MP3 so the
# deck plays on any importer (FSRS Mobile Flashcards on iOS, AnkiDroid, etc.)
# rather than relying on Anki's on-the-fly {{tts}} directive.
AUDIO_FIELDS = {"AudioES": "es_ES", "AudioLA": "es_US"}


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


MODEL_FIELDS = ["English", "Spanish", "AudioES", "AudioLA", "Tags"]

MODEL_CSS = """
.card { font-family: -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; font-size: 22px; text-align: center; color: #111; background-color: #fff; }
hr { border: none; border-top: 1px solid #ddd; }
.accent { font-size:14px; color:#888; margin-top:10px; }
"""

CARD_NAME = "EN->ES with TTS"
CARD_FRONT = "{{English}}"
# Plays bundled MP3s via [sound:...] in the audio fields instead of {{tts}},
# so audio works in importers that don't implement Anki's TTS directive (iOS).
CARD_BACK = (
    "{{FrontSide}}"
    "<hr id='answer'>"
    "<div style='font-size:26px; margin-top:8px;'><b>{{Spanish}}</b></div>"
    "<div style='font-size:18px; color:#666; margin-top:6px;'>({{English}})</div>"
    "<div class='accent'>European Spanish:</div>"
    "<div>{{AudioES}}</div>"
    "<div class='accent'>Latin American Spanish:</div>"
    "<div>{{AudioLA}}</div>"
)


def ensure_model_exists():
    """Create the model if missing, or reconcile an existing one.

    Reconciling matters for collections that already have the old TTS-template
    model: we add the audio fields and switch the card template to play
    bundled MP3s.
    """
    if MODEL_NAME not in invoke("modelNames"):
        print(f"⚙️ Creating model: {MODEL_NAME}")
        invoke(
            "createModel",
            modelName=MODEL_NAME,
            inOrderFields=MODEL_FIELDS,
            css=MODEL_CSS,
            cardTemplates=[{"Name": CARD_NAME, "Front": CARD_FRONT, "Back": CARD_BACK}],
        )
        print(f"✅ Created model: {MODEL_NAME}")
        return

    print(f"🔧 Reconciling existing model: {MODEL_NAME}")
    existing_fields = invoke("modelFieldNames", modelName=MODEL_NAME)
    for field in ("AudioES", "AudioLA"):
        if field not in existing_fields:
            invoke("modelFieldAdd", modelName=MODEL_NAME, fieldName=field, index=len(existing_fields))
            existing_fields.append(field)
            print(f"   • added field: {field}")

    invoke("updateModelTemplates", model={"name": MODEL_NAME, "templates": {CARD_NAME: {"Front": CARD_FRONT, "Back": CARD_BACK}}})
    invoke("updateModelStyling", model={"name": MODEL_NAME, "css": MODEL_CSS})
    print("✅ Model reconciled (audio fields + [sound:] template).")


def audio_field_values(spanish):
    """`[sound:...]` references for both accents of a Spanish phrase."""
    es = spanish.strip()
    return {
        field: f"[sound:{tts_audio.audio_filename(es, voice_key)}]"
        for field, voice_key in AUDIO_FIELDS.items()
    }


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
        "fields": {
            "English": english,
            "Spanish": spanish,
            "Tags": ", ".join(tags) if tags else "",
            **audio_field_values(spanish),
        },
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
            key = english
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
                "fields": {"English": en, "Spanish": es, "Tags": ", ".join(tag_mapping.get_tags_for_card(deck_name, en, es)), **audio_field_values(es)},
                "options": {"allowDuplicate": False},
                "tags": tag_mapping.get_tags_for_card(deck_name, en, es),
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
                        "fields": {"English": en, "Spanish": es, "Tags": ", ".join(tag_mapping.get_tags_for_card(deck_name, en, es)), **audio_field_values(es)},
                        "options": {"allowDuplicate": False},
                        "tags": tag_mapping.get_tags_for_card(deck_name, en, es),
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



# ---------- Audio: generate + upload media ----------
def _chunked(seq, size):
    for i in range(0, len(seq), size):
        yield seq[i : i + size]


def generate_audio():
    """Synthesize any missing MP3s into the local cache (skips cached ones)."""
    texts = tts_audio.collect_unique_spanish()
    print(f"\n🔊 Ensuring audio for {len(texts)} phrases x {len(tts_audio.VOICES)} accents...")
    start = time.perf_counter()
    print(f"   • start: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    stats = tts_audio.generate_missing(texts)
    elapsed = time.perf_counter() - start
    print(f"   • end:   {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   • generated {stats['generated']} new, {stats['cached']} already cached")
    print(f"   • time taken: {elapsed:.2f}s")


def store_audio_media():
    """Copy cached MP3s into Anki's media collection (only files not present)."""
    already = set(invoke("getMediaFilesNames", pattern=f"{tts_audio.MEDIA_PREFIX}*.mp3"))
    actions = []
    for text in tts_audio.collect_unique_spanish():
        for voice_key in tts_audio.VOICES:
            filename = tts_audio.audio_filename(text, voice_key)
            if filename in already:
                continue
            path = tts_audio.cache_path(text, voice_key)
            if not path.exists():
                print(f"   ⚠️ missing cached audio (run generate first): {filename}")
                continue
            actions.append({"action": "storeMediaFile", "params": {"filename": filename, "path": str(path)}})

    if not actions:
        print("🎵 Media already up to date in Anki.")
        return

    print(f"🎵 Uploading {len(actions)} audio file(s) to Anki media...")
    for batch in _chunked(actions, 500):
        invoke("multi", actions=batch)
    print("✅ Media upload complete.")

def reconcile_existing_tags():
    """Ensure existing notes have the latest tag mapping."""
    note_ids = invoke("findNotes", query=f'note:"{MODEL_NAME}"')
    if not note_ids:
        return
        
    # We need to map English text to its target deck to use the tag mapping
    en_to_deck = {}
    for deck_name, cards in decks.items():
        for en, es in cards:
            en_to_deck[en] = (deck_name, es)
            
    updates_fields = []
    actions = []
    
    for info in invoke("notesInfo", notes=note_ids):
        fields = info.get("fields", {})
        en = fields.get("English", {}).get("value", "").strip()
        
        if en not in en_to_deck:
            continue
            
        deck_name, es = en_to_deck[en]
        desired_tags_list = tag_mapping.get_tags_for_card(deck_name, en, es)
        desired_tags_str = ", ".join(desired_tags_list)
        
        # 1. Update the 'Tags' field if it's out of sync
        current_tags_field = fields.get("Tags", {}).get("value", "")
        if current_tags_field != desired_tags_str:
            updates_fields.append({
                "action": "updateNoteFields",
                "params": {"note": {"id": info["noteId"], "fields": {"Tags": desired_tags_str}}}
            })
            
        # 2. Update the Anki note tags if out of sync
        current_note_tags = set(info.get("tags", []))
        desired_note_tags = set(desired_tags_list)
        
        tags_to_add = " ".join(desired_note_tags - current_note_tags)
        tags_to_remove = " ".join(current_note_tags - desired_note_tags)
        
        if tags_to_add:
            actions.append({"action": "addTags", "params": {"notes": [info["noteId"]], "tags": tags_to_add}})
        if tags_to_remove:
            actions.append({"action": "removeTags", "params": {"notes": [info["noteId"]], "tags": tags_to_remove}})

    if updates_fields:
        print(f"🏷️  Updating 'Tags' field on {len(updates_fields)} existing note(s)...")
        for batch in _chunked(updates_fields, 500):
            invoke("multi", actions=batch)
            
    if actions:
        # Actions has both addTags and removeTags so len might be up to 2x notes. 
        print(f"🏷️  Updating Anki tags on {len(actions)} batch operations...")
        for batch in _chunked(actions, 500):
            invoke("multi", actions=batch)
            
    if updates_fields or actions:
        print("✅ Existing tags updated.")


def _run_checked(actions, size=500):
    """Run actions through `multi` in batches and fail loudly on any error.

    `multi` doesn't raise when a sub-action fails; it returns
    {"result": None, "error": "..."} in that action's slot instead.
    """
    for batch in _chunked(actions, size):
        results = invoke("multi", actions=batch)
        errors = [r["error"] for r in results if isinstance(r, dict) and r.get("error")]
        if errors:
            raise Exception(f"{len(errors)} of {len(batch)} AnkiConnect actions failed, first error: {errors[0]}")


def _notes_by_front():
    """English front -> note ids, for every note of our model."""
    note_ids = invoke("findNotes", query=f'note:"{MODEL_NAME}"')
    by_front = {}
    for info in invoke("notesInfo", notes=note_ids) if note_ids else []:
        en = info.get("fields", {}).get("English", {}).get("value", "").strip()
        by_front.setdefault(en, []).append(info["noteId"])
    return by_front


def apply_card_migrations():
    """Rename / retire existing notes listed in card_migrations.py.

    Must run before cards are added: the add step matches notes on the English
    field, so a renamed front would otherwise be added as a second note and the
    old note (with its review history) left behind.
    """
    by_front = _notes_by_front()

    retire = [(front, nid) for front in sorted(card_migrations.RETIRED_FRONTS) for nid in by_front.get(front, [])]
    if retire:
        print(f"🗑️  Deleting {len(retire)} retired back-to-front duplicate note(s):")
        for front, _ in retire:
            print(f"   • {front}")
        invoke("deleteNotes", notes=[nid for _, nid in retire])

    renames = []
    for old, new in card_migrations.RENAMED_FRONTS.items():
        ids = by_front.get(old, [])
        if not ids:
            continue  # already migrated, or never added
        if new in by_front or len(ids) > 1:
            print(f"   ⚠️ not renaming {old!r} -> {new!r}: target exists or front is ambiguous")
            continue
        renames.append({"action": "updateNoteFields", "params": {"note": {"id": ids[0], "fields": {"English": new}}}})

    if renames:
        print(f"✏️  Renaming {len(renames)} existing note(s) in place (review history kept)...")
        _run_checked(renames)


def reconcile_existing_spanish():
    """Sync the Spanish field (and its audio) of existing notes with decks_data.

    The add step skips notes whose English already exists, so without this a
    corrected Spanish answer in decks_data.py never reaches cards already in Anki.
    """
    en_to_es, ambiguous = {}, set()
    for cards in decks.values():
        for en, es in cards:
            if en_to_es.setdefault(en, es) != es:
                ambiguous.add(en)
    for en in sorted(ambiguous):
        del en_to_es[en]
        print(f"   ⚠️ {en!r} has different Spanish in two decks; leaving its Spanish unchanged")

    note_ids = invoke("findNotes", query=f'note:"{MODEL_NAME}"')
    if not note_ids:
        return
    updates = []
    for info in invoke("notesInfo", notes=note_ids):
        fields = info.get("fields", {})
        en = fields.get("English", {}).get("value", "").strip()
        desired = en_to_es.get(en)
        if desired is None or fields.get("Spanish", {}).get("value", "").strip() == desired.strip():
            continue
        new_fields = {"Spanish": desired, **audio_field_values(desired)}
        updates.append({"action": "updateNoteFields", "params": {"note": {"id": info["noteId"], "fields": new_fields}}})

    if not updates:
        return
    print(f"🩹 Updating Spanish on {len(updates)} existing note(s)...")
    _run_checked(updates)
    print("✅ Existing Spanish updated.")


def reconcile_existing_audio():
    """Populate audio fields on notes that predate the embedded-audio change."""
    note_ids = invoke("findNotes", query=f'note:"{MODEL_NAME}"')
    if not note_ids:
        return
    updates = []
    for info in invoke("notesInfo", notes=note_ids):
        fields = info.get("fields", {})
        spanish = fields.get("Spanish", {}).get("value", "").strip()
        if not spanish:
            continue
        desired = audio_field_values(spanish)
        if any(fields.get(f, {}).get("value", "") != v for f, v in desired.items()):
            updates.append({"action": "updateNoteFields", "params": {"note": {"id": info["noteId"], "fields": desired}}})

    if not updates:
        return
    print(f"🩹 Updating audio fields on {len(updates)} existing note(s)...")
    for batch in _chunked(updates, 500):
        invoke("multi", actions=batch)
    print("✅ Existing notes updated.")


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
            for en in duplicates:
                print(f"    {en}")
        print("\n💡 Fix these duplicates in decks_data.py before running export.")
        print("🚫 ABORTING: Cannot proceed with duplicates present.")
        exit(1)
    
    print("✅ No internal duplicates found.")

    # Generate any missing audio before touching Anki so notes can reference it.
    generate_audio()

    ensure_model_exists()
    create_decks()
    store_audio_media()

    # Rename/retire changed fronts first so they aren't re-added as new notes.
    apply_card_migrations()

    print("\n🔍 Checking which cards can be added...")
    filtered = filter_addable_notes_all_decks(decks)
    print("✅ Duplicate filtering complete.")

    print("\n🧩 Adding cards in bulk...")
    add_notes_all_decks(filtered)

    # Push corrected Spanish answers onto notes that already exist.
    reconcile_existing_spanish()

    # Backfill audio onto notes that already existed before this change.
    reconcile_existing_audio()

    # Backfill the latest tags onto notes that already existed before this change.
    reconcile_existing_tags()

    elapsed = time.time() - start_time
    minutes, seconds = divmod(elapsed, 60)
    print(f"\n🎉 Sync complete! Check Anki → Deck Browser → Spanish Pronunciation Trainer.")
    print(f"⏱️ Elapsed time: {int(minutes)}m {seconds:.1f}s")

if __name__ == "__main__":
    main()
