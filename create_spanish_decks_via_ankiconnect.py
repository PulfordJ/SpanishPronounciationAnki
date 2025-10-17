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
                ),
            }
        ],
    }
    invoke("createModel", **model)
    print(f"✅ Created model: {MODEL_NAME}")


# ---------- Decks ----------
ROOT_DECK = "Spanish Pronunciation Trainer"
SUBDECKS = [
    "Phrases",
    "Verb Conjugations",
    "Help",
    "Numbers",
    "Preguntar (Questions)",
    "Responses",
    "Saludar (Greetings)",
    "Despedirse (Goodbyes)",
    "Dialogue",
    "Original Cards",
    "Classroom Objects",
    "Grammar (Tener & Plurals)",
    "Requests & Needs",
    "Feelings & Concepts",
    "Virtues & Abstract Words",
    "Miscellaneous",
    "Common Verbs & Phrases",
    "Math & Quantities",
    # New categories:
    "Nationalities & Countries",
    "Professions",
    "Food & Culture",
    "Grammar (Articles & Gender)",
    "Pronunciation Practice",
    "Mini Dialogues",
]


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

decks = {
    "Phrases": [
        ("the morning", "la mañana"),
        ("from where", "de dónde"),
        ("What are you doing this afternoon?", "¿Qué haces esta tarde?"),
        ("to review / revise", "repasar"),
        ("What do you mean, why?", "¿Qué por qué?"),
        ("What day is it today?", "¿Qué día es hoy?"),
        ("clear as water", "clara como el agua"),
        ("Sorry, I don't know", "Lo siento, no lo sé"),
        ("Sorry, I don't speak Japanese", "Lo siento, no hablo japonés"),
        ("Sorry, I speak a bit of Spanish", "Lo siento, hablo un poco de español"),
        ("What does it mean?", "¿Qué significa?"),
    ],

    "Verb Conjugations": [
        ("My name", "Me llamo (yo)"),
        ("Your name", "Te llamas (tú)"),
        ("His/Her name", "Se llama (él / ella)"),
        ("Their names", "Se llaman (ellos / ellas)"),
        ("Our names", "Nos llamamos (nosotros)"),
        ("You all names", "Os llamáis (vosotros)"),
        ("Formal your name", "Se llama (usted)"),
    ],

    "Help": [
        ("how", "cómo"),
        ("What did you say?", "¿Cómo dices?"),
        ('What does "vale" mean?', '¿Qué significa "vale"?'),
        ('How do you say "water" in Spanish?', '¿Cómo se dice "water" en español?'),
        ("How do you say this in Spanish?", "¿Cómo se dice esto en español?"),
        ("Can you speak louder, please?", "¿Puedes hablar más alto, por favor?"),
        ("Can you speak more slowly, please?", "¿Puedes hablar más despacio, por favor?"),
        ("Can you repeat, please?", "¿Puedes repetir, por favor?"),
        ("to be able to (infinitive form of puedo)", "poder"),
        ("I can", "yo puedo"),
    ],

    "Numbers": [
        ("one", "uno"),
        ("two", "dos"),
        ("three", "tres"),
        ("four", "cuatro"),
        ("five", "cinco"),
        ("six", "seis"),
        ("seven", "siete"),
        ("eight", "ocho"),
        ("nine", "nueve"),
        ("ten", "diez"),
        ("eleven", "once"),
        ("twelve", "doce"),
        ("thirteen", "trece"),
        ("fourteen", "catorce"),
        ("fifteen", "quince"),
        ("sixteen", "dieciséis"),
        ("seventeen", "diecisiete"),
        ("eighteen", "dieciocho"),
        ("nineteen", "diecinueve"),
        ("twenty", "veinte"),
        ("thirty", "treinta"),
        ("forty", "cuarenta"),
        ("fifty", "cincuenta"),
        ("sixty", "sesenta"),
        ("seventy", "setenta"),
        ("eighty", "ochenta"),
        ("ninety", "noventa"),
        ("one hundred", "cien"),
        ("twenty-one", "veintiuno"),
        ("twenty-two", "veintidós"),
        ("thirty-three", "treinta y tres"),
        ("thirty-four", "treinta y cuatro"),
        ("forty-four", "cuarenta y cuatro"),
        ("forty-five", "cuarenta y cinco"),
        ("fifty-six", "cincuenta y seis"),
        ("fifty-seven", "cincuenta y siete"),
        ("sixty-eight", "sesenta y ocho"),
        ("seventy-seven", "setenta y siete"),
        ("eighty-eight", "ochenta y ocho"),
        ("ninety-three", "noventa y tres"),
    ],

    "Preguntar (Questions)": [
        ("How are (things)?", "¿Qué tal?"),
        ("How are you?", "¿Cómo estás?"),
        ("All good?", "¿Todo bien?"),
        ("How is everything?", "¿Qué tal todo?"),
        ("How's it going (for you)?", "¿Qué tal te va?"),
        ("What's up?", "¿Qué hay?"),
        ("What are you up to?", "¿Qué te cuentas?"),
        ("How is (he/she)?", "¿Cómo está?"),
        ("How are you? (formal)", "¿Cómo se encuentra?"),
        ("How are you? (formal, alt.)", "¿Cómo le va?"),
    ],

    "Responses": [
        ("very well", "muy bien"),
        ("well", "bien"),
        ("great", "genial"),
        ("all good", "todo bien"),
        ("everything great", "todo genial"),
        ("well...", "bueno..."),
        ("getting by", "tirando"),
        ("so-so, and you?", "regular, ¿y tú?"),
        ("not very well", "no muy bien"),
        ("bad", "mal"),
        ("awful", "fatal"),
    ],

    "Saludar (Greetings)": [
        ("hello", "hola"),
        ("hi / hello (neutral)", "buenas"),
        ("good morning", "buenos días"),
        ("good afternoon", "buenas tardes"),
        ("long time no see!", "¡cuánto tiempo!"),
        ("I'm glad to see you", "me alegro de verte"),
        ("nice to see you", "qué gusto verte"),
        ("so happy to see you", "qué alegría verte"),
    ],

    "Despedirse (Goodbyes)": [
        ("goodbye", "adiós"),
        ("see you soon", "hasta pronto"),
        ("good night", "buenas noches"),
        ("see you later", "hasta luego"),
        ("see you tomorrow", "hasta mañana"),
        ("bye", "chao"),
        ("see you", "hasta la vista"),
        ("see you Monday/Tuesday", "hasta el lunes / martes"),
        ("see you another time", "hasta otra"),
        ("see you (soon)", "nos vemos (pronto)"),
        ("hope it goes well!", "¡que vaya bien!"),
    ],

    "Dialogue": [
        ("Naomi and Pedro", "Naomi y Pedro"),
        ("My name is David. Nice to meet you.", "Me llamo David. Mucho gusto."),
        ("Pleased to meet you (fem.)", "Encantada."),
        ("Fine, a little tired.", "Bien, un poco cansada."),
        ("Sleep well / rest up.", "Que descanses."),
        ("Likewise, see you tomorrow.", "Igualmente, hasta mañana."),
        ("Where are you from?", "¿De dónde eres?"),
        ("How interesting!", "¡Qué interesante!"),
        ("Yes, me too. Hey, what are you doing this afternoon?", "Sí, yo también. Oye, ¿qué haces esta tarde?"),
        ("Nothing special. And you?", "Nada especial. ¿Y tú?"),
        ("I have Spanish class.", "Tengo clase de español."),
        ("Okay, I'm off now.", "Bueno, me voy ya."),
        ("Goodbye, have a good day.", "Adiós, que tengas un buen día."),
        ("Thanks, likewise.", "Gracias, igualmente."),
    ],

    "Classroom Objects": [
        ("pen", "bolígrafo"),
        ("pencil", "lápiz"),
        ("laptop", "portátil"),
        ("chair", "silla"),
        ("projector", "proyector"),
        ("whiteboard", "pizarra blanca"),
        ("tablet", "tableta"),
        ("pencil case", "estuche"),
        ("table / desk", "mesa"),
        ("book", "libro"),
        ("notebook", "cuaderno"),
        ("sheet of paper", "hoja de papel"),
        ("backpack", "mochila"),
        ("computer (alt.)", "ordenador"),
        ("ruler", "regla"),
        ("scissors", "tijeras"),
        ("calculator", "calculadora"),
        ("eraser", "borrador"),
        ("sharpener", "sacapuntas"),
        ("camera", "cámara de fotos"),
        ("also / too", "también"),
    ],

    "Grammar (Tener & Plurals)": [
        ("I have three coins", "yo tengo tres monedas"),
        ("I have four things", "yo tengo cuatro cosas"),
        ("I have a pen", "yo tengo un bolígrafo"),
        ("I have a laptop", "yo tengo un portátil"),
        ("I have a table", "yo tengo una mesa"),
        ("I don’t have the books", "yo no tengo los libros"),
        ("I don’t have a glass of water", "yo no tengo un vaso de agua"),
        ("I don’t have the glasses", "yo no tengo las gafas"),
        ("plural of lápiz", "lápices"),
        ("plural of silla", "sillas"),
        ("plural of portátil", "portátiles"),
        ("plural of hoja de papel", "hojas de papel"),
        ("the ball", "el balón"),
        ("the balls", "los balones"),
        ("the plant", "la planta"),
        ("the plants", "las plantas"),
    ],

    "Requests & Needs": [
        ("I like to draw with a pencil", "me gusta dibujar con un lápiz"),
        ("Can you lend me a blue pen?", "¿me dejas un boli azul?"),
        ("I have a yellow highlighter", "tengo un subrayador amarillo"),
        ("This pencil has no tip", "este lápiz no tiene punta"),
        ("I need a sharpener", "¡necesito un sacapuntas!"),
        ("Can you lend me your eraser?", "¿me prestas tu borrador?"),
        ("I have to look for a house", "tengo que buscar una casa"),
        ("In maths class we use calculators", "en clase de matemáticas utilizamos calculadoras"),
        ("I keep all my things in my backpack", "guardo todas mis cosas en mi mochila"),
        ("In my notebook I write with a pen", "en mi cuaderno escribo con bolígrafo"),
        ("The teacher writes on the board", "la profesora escribe en la pizarra"),
        ("A pair of glasses", "un par de gafas"),
        ("With a ruler you can make straight lines", "con la regla puedes hacer líneas rectas"),
    ],

    "Feelings & Concepts": [
        ("sun", "sol"),
        ("star", "estrella"),
        ("dawn", "alborada"),
        ("trust / confidence", "confianza"),
        ("bat (animal)", "murciélago"),
        ("we dance", "bailamos"),
        ("thank you", "gracias"),
        ("feeling", "sentimiento"),
        ("solidarity", "la solidaridad"),
        ("mother", "madre"),
        ("joy / happiness", "alegría"),
        ("lawyer", "abogado"),
        ("football / soccer", "fútbol"),
        ("I desire love", "deseo amor"),
        ("to love / to want", "querer"),
        ("male / macho", "macho"),
        ("researcher / investigator", "investigador"),
        ("beauty", "belleza"),
        ("you (informal)", "tú"),
        ("affection / darling", "cariño"),
        ("mellifluous / sweet-sounding", "melíflua"),
        ("I am sleepy", "yo tengo sueño"),
        ("I have a dream", "yo tengo un sueño"),
    ],

    "Virtues & Abstract Words": [
        ("truth", "verdad"),
        ("loyalty", "lealtad"),
        ("confidence", "confianza"),
        ("spirit", "espíritu"),
        ("love", "amor"),
    ],

    "Miscellaneous": [
        ("How was it? It was...", "¿Cómo fue? Fue..."),
        ("It was easy / difficult / so-so / more or less", "fue fácil / difícil / así así / más o menos"),
        ("the mountain peak", "la punta de la montaña"),
        ("I need food", "necesito comida"),
        ("I need a cup of wine", "necesito una copa de vino"),
        ("Do you have anything?", "¿tienes algo?"),
        ("You have nothing", "no tienes nada"),
        ("other languages", "otras lenguas"),
        ("come se escribe __ en español", "¿cómo se escribe __ en español?"),
        ("how do you pronounce 'pizarra'?", "¿cómo se pronuncia 'pizarra'?"),
    ],

    "Common Verbs & Phrases": [
        ("to leave / to let", "dejar"),
        ("I leave / I let", "dejo"),
        ("I leave you a pencil", "te dejo un lápiz"),
        ("to take / to drink", "tomar"),
        ("take (here you go)", "toma"),
    ],

    "Math & Quantities": [
        ("more", "más"),
        ("less / minus", "menos"),
        ("nine plus one equals ten", "nueve más uno = diez"),
    ],

    "Nationalities & Countries": [
        ("Canadian", "canadiense"),
        ("He is French", "es francés"),
        ("She is French", "es francesa"),
        ("He is Italian", "es italiano"),
        ("She is Italian", "es italiana"),
        ("American / from the U.S.", "estadounidense"),
        ("Scottish (fem.)", "escocesa"),
        ("Belgian", "belga"),
        ("England", "Inglaterra"),
        ("Spain", "España"),
        ("Switzerland", "Suiza"),
        ("Chile", "Chile"),
        ("Norway", "Noruega"),
        ("Sweden", "Suecia"),
        ("Algeria", "Argelia"),
        ("Russian (fem.)", "rusa"),
        ("Russian (masc.)", "ruso"),
        ("Denmark", "Dinamarca"),
        ("Panamanian", "panameño"),
        ("Venezuelan", "venezolano"),
        ("Cuban", "cubano"),
        ("Chilean", "chileno"),
        ("Peruvian", "peruano"),
        ("Ecuadorian", "ecuatoriano"),
        ("Argentine / Argentinian", "argentino"),
        ("Maltese (masc.)", "maltés"),
        ("Maltese (fem.)", "maltesa"),
        ("Poland", "Polonia"),
        ("Polish (masc.)", "polaco"),
        ("Lithuanian (masc.)", "lituano"),
        ("Lithuanian (fem.)", "lituana"),
        ("Indonesian (fem.)", "indonesia"),
        ("Indonesian (masc.)", "indonesio"),
        ("Irish", "irlandés"),
        ("In pairs, think of four things and write the nationality you associate with each one", "En parejas, pensad cuatro cosas y escribid la nacionalidad con la que relacionáis cada una."),
    ],

    "Professions": [
        ("pronunciation", "pronunciación"),
        ("painter (masc.)", "pintor"),
        ("painter (fem.)", "pintora"),
        ("writer (masc.)", "escritor"),
        ("writer (fem.)", "escritora"),
        ("teacher (masc.)", "profesor"),
        ("teacher (fem.)", "profesora"),
        ("scientist (fem.)", "científica"),
        ("student", "estudiante"),
        ("journalist", "periodista"),
        ("salesperson / commercial agent", "comercial"),
        ("driver / chauffeur", "chófer"),
        ("agent", "agente"),
        ("police officer", "policía"),
        ("model", "modelo"),
        ("fashion designer", "diseñador/a de moda"),
        ("librarian (masc.)", "bibliotecario"),
        ("librarian (fem.)", "bibliotecaria"),
        ("employee (masc.)", "empleado"),
        ("employee (fem.)", "empleada"),
        ("waiter", "camarero"),
        ("waitress", "camarera"),
        ("hairdresser (masc.)", "peluquero"),
        ("hairdresser (fem.)", "peluquera"),
        ("doctor (masc.)", "doctor"),
        ("doctor (fem.)", "doctora"),
        ("translator", "traductor"),
        ("nurse (masc.)", "enfermero"),
        ("engineer (masc.)", "ingeniero"),
        ("engineer (fem.)", "ingeniera"),
        ("lawyer (masc.)", "abogado"),
        ("lawyer (fem.)", "abogada"),
        ("architect (fem.)", "arquitecta"),
        ("architect (masc.)", "arquitecto"),
        ("editor (masc.)", "editor"),
        ("editor (fem.)", "editora"),
        ("bookstore", "librería"),
        ("shop assistant", "dependiente"),
        ("vendor / seller", "vendedor"),
        ("occupational therapist", "terapeuta ocupacional"),
        ("systems engineer", "ingeniero de sistemas"),
        ("dentist", "dentista"),
        ("homemaker", "ama de casa"),
        ("midwife", "matrona"),
        ("father", "padre"),
        ("carpenter", "tablador"),
        ("artist", "artista"),
        ("counsellor", "consejero"),
        ("accountant", "contador"),
        ("quantitative analyst (masc.)", "analista cuantitativo"),
        ("quantitative analyst (fem.)", "analista cuantitativa"),
    ],

    "Food & Culture": [
        ("The tango is Argentine", "el tango es argentino"),
        ("Sushi is Japanese", "el sushi es japonés"),
        ("Pizza is Italian", "la pizza es italiana"),
        ("Flamenco is Spanish", "el flamenco es español"),
        ("The balalaika is Russian", "la balalaika es rusa"),
        ("The croissant is French", "el cruasán es francés"),
        ("The baguette is French", "la baguette es francesa"),
        ("Big Ben is British", "el Big Ben es británico"),
        ("Big Ben is English", "el Big Ben es inglés"),
        ("Paella is Spanish", "la paella es española"),
        ("The city is Chinese", "la ciudad es china"),
        ("Curry is Indian", "el curry es indio"),
        ("The hamburger is American", "la hamburguesa es estadounidense"),
        ("From which country do these things come?", "¿De qué país proceden estas cosas?"),
        ("Write in your notebook the nationality that corresponds to them", "Escribe en tu cuaderno la nacionalidad que les corresponde"),
        ("Be careful with gender!", "¡Cuidado con el género!"),
    ],

    "Grammar (Articles & Gender)": [
        ("to the (abbreviation)", "al (a + el)"),
        ("from the (abbreviation)", "del (de + el)"),
        ("some (masculine)", "unos"),
        ("some (feminine)", "unas"),
        ("determined / definite", "determinados"),
        ("undetermined / indefinite", "indeterminados"),
        ("some pens", "unos bolígrafos"),
        ("some tables", "unas mesas"),
    ],

    "Pronunciation Practice": [
        ("pronunciation pattern: gi", "gi"),
        ("pronunciation pattern: ge", "ge"),
        ("pronunciation pattern: ga", "ga"),
        ("pronunciation pattern: go", "go"),
        ("pronunciation pattern: gu", "gu"),
        ("pronunciation pattern: gue", "gue"),
        ("pronunciation pattern: gui", "gui"),
        ("cook / chef", "cocinero"),
    ],

    "Mini Dialogues": [
        ("What", "qué"),
        ("Where", "dónde"),
        ("What do you do for a living?", "¿A qué te dedicas?"),
        ("What do you do for a living? (formal)", "¿A qué se dedica usted?"),
        ("I know", "conozco"),
        ("Then / so / in that case", "entonces"),
        ("Are you the new colleague?", "¿Tú eres el nuevo compañero?"),
        ("Do you work here at the centre or from home?", "¿Trabajas aquí en el centro o desde casa?"),
        ("Hello, my name is Andrés. I’m Argentine and a Spanish teacher. I’m 35 years old.", "Hola, mi nombre es Andrés. Soy argentino y soy profesor de español. Tengo 35 años."),
        ("Hello, my name is John. I work as a systems engineer and I’m English. I’m 33 years old.", "Hola, mi nombre es John. Trabajo de ingeniero de sistemas y soy inglés. Tengo 33 años."),
        ("Maha works in a workshop.", "Maha en un taller."),
        ("Chloe works at a TV channel.", "Chloe en un canal de televisión."),
        ("Ulrich works in a language school.", "Ulrich en una escuela de lenguas."),
        ("Gibson works in a laboratory.", "Gibson en un laboratorio."),
        ("Andrés works at a university.", "Andrés en una universidad."),
        ("name", "nombre"),
        ("nationality", "nacionalidad"),
        ("profession", "profesión"),
        ("age", "edad"),
    ],
}


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
    """Batch-insert all addable notes across decks using one multi call."""
    multi_actions = []
    for deck_name, (addable, skipped) in filtered_results.items():
        if not addable:
            continue
        multi_actions.append({"action": "addNotes", "params": {"notes": addable}})

    if not multi_actions:
        print("✅ No new cards to add — all duplicates skipped.")
        return

    print(f"⚙️ Adding notes for {len(multi_actions)} decks in one API call...")
    results = invoke("multi", actions=multi_actions)

    for (deck_name, (addable, skipped)), result in zip(filtered_results.items(), results):
        added = len(addable)
        print(f"🃏 {ROOT_DECK}::{deck_name}: Added {added} new cards ({skipped} skipped).")


# ---------- Run ----------
def main():
    start_time = time.time()
    print("🔗 Connecting to AnkiConnect...")
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
