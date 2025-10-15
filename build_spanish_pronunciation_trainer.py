# build_spanish_pronunciation_trainer.py
# Full Spanish Pronunciation Trainer deck generator
# English → Spanish (auto TTS es_ES, English confirmation on back)

import genanki

DECK_ROOT = "Spanish Pronunciation Trainer"

# ---------- Model ----------
model = genanki.Model(
    1607392327,
    'Spanish Pronunciation Model (EN->ES TTS)',
    fields=[
        {'name': 'English'},
        {'name': 'Spanish'},
        {'name': 'Tags'},
    ],
    templates=[
        {
            'name': 'EN->ES with TTS',
            'qfmt': '{{English}}',
            'afmt': (
                '{{FrontSide}}'
                '<hr id="answer">'
                '<div>{{tts es_ES voices=Google :Spanish}}</div>'
                '<div style="font-size:26px; margin-top:8px;"><b>{{Spanish}}</b></div>'
                '<div style="font-size:18px; color:#666; margin-top:6px;">({{English}})</div>'
            ),
        },
    ],
    css="""
        .card {
            font-family: -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
            font-size: 22px;
            text-align: center;
            color: #111;
            background-color: #fff;
        }
        hr { border: none; border-top: 1px solid #ddd; }
    """,
)

def make_deck(name_suffix):
    full_name = f"{DECK_ROOT}::{name_suffix}" if name_suffix else DECK_ROOT
    did = abs(hash(full_name)) % (10**10) + 1
    return genanki.Deck(did, full_name)

def add_cards(deck, pairs, tag=None):
    for en, es in pairs:
        note = genanki.Note(
            model=model,
            fields=[en, es, tag or ""],
            tags=[tag] if tag else []
        )
        deck.add_note(note)

# ---------- Decks ----------
root_deck = make_deck("")
deck_phrases = make_deck("Phrases")
deck_verbs = make_deck("Verb Conjugations")
deck_help = make_deck("Help")
deck_numbers = make_deck("Numbers")
deck_preguntar = make_deck("Preguntar (Questions)")
deck_responses = make_deck("Responses")
deck_saludar = make_deck("Saludar (Greetings)")
deck_despedirse = make_deck("Despedirse (Goodbyes)")
deck_dialogue = make_deck("Dialogue")
deck_original = make_deck("Original Cards")

# ---------- Instructions ----------
root_deck.add_note(genanki.Note(
    model=model,
    fields=[
        "How to use this Spanish Pronunciation Trainer",
        (
            "🇬🇧 English first → listen → repeat → check meaning<br><br>"
            "🧠 When a card appears:<br>"
            "1) Read the English on the front.<br>"
            "2) Say it in Spanish (out loud).<br>"
            "3) Flip the card — audio plays immediately (es_ES).<br>"
            "4) Repeat it several times, imitating rhythm and accent.<br>"
            "5) Read the Spanish and English together to reinforce meaning.<br><br>"
            "💡 Tips:<br>"
            "• Review 10–20 cards daily and speak every answer aloud.<br>"
            "• Use subdecks (Phrases, Numbers, etc.) to focus practice.<br>"
            "• Slow audio in Anki settings if needed and shadow the pronunciation."
        ),
        "instructions"
    ],
    tags=["instructions"]
))

# ---------- Phrases ----------
phrases = [
    ("the morning", "la mañana"),
    ("see you tomorrow", "hasta mañana"),
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
]
add_cards(deck_phrases, phrases, tag="phrases")

# ---------- Verb Conjugations (llamarse) ----------
verbs_llamarse = [
    ("My name", "Me llamo (yo)"),
    ("Your name", "Te llamas (tú)"),
    ("His/Her name", "Se llama (él / ella)"),
    ("Their names", "Se llaman (ellos / ellas)"),
    ("Our names", "Nos llamamos (nosotros)"),
    ("You all names", "Os llamáis (vosotros)"),
    ("Formal your name", "Se llama (usted)"),
]
add_cards(deck_verbs, verbs_llamarse, tag="verbs,llamarse")

# ---------- Help ----------
help_cards = [
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
]
add_cards(deck_help, help_cards, tag="help")

# ---------- Numbers ----------
nums = []
nums += [(f"{en} ({i})", es) for i, (en, es) in enumerate([
    ("one", "uno"), ("two", "dos"), ("three", "tres"), ("four", "cuatro"),
    ("five", "cinco"), ("six", "seis"), ("seven", "siete"), ("eight", "ocho"),
    ("nine", "nueve"), ("ten", "diez")
], start=1)]
nums += [
    ("eleven (11)", "once"), ("twelve (12)", "doce"), ("thirteen (13)", "trece"),
    ("fourteen (14)", "catorce"), ("fifteen (15)", "quince"), ("sixteen (16)", "dieciséis"),
    ("seventeen (17)", "diecisiete"), ("eighteen (18)", "dieciocho"), ("nineteen (19)", "diecinueve")
]
nums += [
    ("ten (10)", "diez"), ("twenty (20)", "veinte"), ("thirty (30)", "treinta"),
    ("forty (40)", "cuarenta"), ("fifty (50)", "cincuenta"), ("sixty (60)", "sesenta"),
    ("seventy (70)", "setenta"), ("eighty (80)", "ochenta"), ("ninety (90)", "noventa"),
    ("one hundred (100)", "cien"),
]
nums += [
    ("twenty-one (21)", "veintiuno"), ("twenty-two (22)", "veintidós"),
    ("thirty-three (33)", "treinta y tres"), ("thirty-four (34)", "treinta y cuatro"),
    ("forty-four (44)", "cuarenta y cuatro"), ("forty-five (45)", "cuarenta y cinco"),
    ("fifty-six (56)", "cincuenta y seis"), ("fifty-seven (57)", "cincuenta y siete"),
    ("sixty-eight (68)", "sesenta y ocho"), ("seventy-seven (77)", "setenta y siete"),
    ("eighty-eight (88)", "ochenta y ocho"), ("ninety-three (93)", "noventa y tres"),
]
add_cards(deck_numbers, nums, tag="numbers")

# ---------- Preguntar ----------
preguntar = [
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
]
add_cards(deck_preguntar, preguntar, tag="preguntar")

# ---------- Responses ----------
responses = [
    ("very well", "muy bien"), ("well", "bien"), ("great", "genial"),
    ("all good", "todo bien"), ("everything great", "todo genial"),
    ("well...", "bueno..."), ("getting by", "tirando"),
    ("so-so, and you?", "regular, ¿y tú?"), ("not very well", "no muy bien"),
    ("bad", "mal"), ("awful", "fatal")
]
add_cards(deck_responses, responses, tag="responses")

# ---------- Saludar ----------
saludar = [
    ("hello", "hola"), ("hi / hello (neutral)", "buenas"),
    ("good morning", "buenos días"), ("good afternoon", "buenas tardes"),
    ("good night", "buenas noches"), ("long time no see!", "¡cuánto tiempo!"),
    ("I'm glad to see you", "me alegro de verte"),
    ("nice to see you", "qué gusto verte"),
    ("so happy to see you", "qué alegría verte"),
]
add_cards(deck_saludar, saludar, tag="saludar")

# ---------- Despedirse ----------
despedirse = [
    ("goodbye", "adiós"), ("see you soon", "hasta pronto"),
    ("good night", "buenas noches"), ("see you later", "hasta luego"),
    ("see you tomorrow", "hasta mañana"), ("bye", "chao"),
    ("see you", "hasta la vista"), ("see you Monday/Tuesday", "hasta el lunes / martes"),
    ("see you another time", "hasta otra"), ("see you (soon)", "nos vemos (pronto)"),
    ("hope it goes well!", "¡que vaya bien!"),
]
add_cards(deck_despedirse, despedirse, tag="despedirse")

# ---------- Dialogue ----------
dialogue = [
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
]
add_cards(deck_dialogue, dialogue, tag="dialogue")

# ---------- Classroom Objects ----------
deck_classroom = make_deck("Classroom Objects")
classroom_objects = [
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
]
add_cards(deck_classroom, classroom_objects, tag="classroom")

# ---------- Grammar: Tener & Plurals ----------
deck_grammar = make_deck("Grammar (Tener & Plurals)")
grammar_cards = [
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
]
add_cards(deck_grammar, grammar_cards, tag="grammar")

# ---------- Requests & Needs ----------
deck_requests = make_deck("Requests & Needs")
requests = [
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
]
add_cards(deck_requests, requests, tag="requests")

# ---------- Feelings & Concepts ----------
deck_concepts = make_deck("Feelings & Concepts")
concepts = [
    ("sun", "sol"),
    ("star", "estrella"),
    ("truth", "verdad"),
    ("loyalty", "lealtad"),
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
    ("spirit", "espíritu"),
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
]
add_cards(deck_concepts, concepts, tag="concepts")

# ---------- Virtues & Abstract Words ----------
deck_virtues = make_deck("Virtues & Abstract Words")
virtues = [
    ("truth", "verdad"),
    ("loyalty", "lealtad"),
    ("solidarity", "solidaridad"),
    ("confidence", "confianza"),
    ("beauty", "belleza"),
    ("spirit", "espíritu"),
    ("joy", "alegría"),
    ("love", "amor"),
]
add_cards(deck_virtues, virtues, tag="virtues")

# ---------- Fun Phrases & Misc ----------
deck_misc = make_deck("Miscellaneous")
misc = [
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
]
add_cards(deck_misc, misc, tag="misc")

# ---------- Common Verbs & Phrases ----------
deck_verbs_common = make_deck("Common Verbs & Phrases")
verbs_common = [
    ("to leave / to let", "dejar"),
    ("I leave / I let", "dejo"),
    ("I leave you a pencil", "te dejo un lápiz"),
    ("to take / to drink", "tomar"),
    ("take (here you go)", "toma"),
]
add_cards(deck_verbs_common, verbs_common, tag="verbs_common")

# ---------- Math / Quantities ----------
deck_math = make_deck("Math & Quantities")
math_cards = [
    ("more", "más"),
    ("less / minus", "menos"),
    ("nine plus one equals ten", "nueve más uno = diez"),
]
add_cards(deck_math, math_cards, tag="math")


# ---------- Package ----------
package = genanki.Package([
    root_deck, deck_phrases, deck_verbs, deck_help, deck_numbers,
    deck_preguntar, deck_responses, deck_saludar,
    deck_despedirse, deck_dialogue, deck_original
])

package.write_to_file('collection-20251108135000_updated.colpkg')
print("✅ Generated: collection-20251008135001_updated.colpkg")
print("Import into Anki → overrides old deck → move existing cards into 'Original Cards'.")
