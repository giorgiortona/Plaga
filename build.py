#!/usr/bin/env python3
"""
Genera il sito PLAGA in site/ — italiano e inglese.

  site/index.html        italiano (lingua principale, sta nella radice)
  site/en/index.html     inglese

Header, burger menu, footer e switcher di lingua stanno qui una volta sola.
Modifica questo file e rilancia `python3 build.py`.
"""

import hashlib
import re
from pathlib import Path

OUT = Path(__file__).parent / "site"

TEL_HREF = "+393515721939"
TEL = "351 572 1939"
IG = "https://www.instagram.com/plaga.lounge/"
MAPS = "https://www.google.com/maps/place/Plaga+Lounge/@40.1478749,18.0728846,17z"
MENU_URL = "https://www.digitavolo.com/plaga/menu"

PAGES = ["index", "sale", "giardino", "forno", "menu", "contatti"]

TAGLINE = "#DOWHATYOULOVE"

LOGO_SVG = Path(__file__).parent / "logo" / "plaga-wordmark.svg"


LOGO_MASTER = Path(__file__).parent / "logo" / "logo_plaga.svg"

# Riquadri dei due gruppi dentro il viewBox 0 0 447 447 del file originale,
# misurati con getBBox() nel browser. Servono per ritagliare stretto:
# senza, il marchio si porterebbe dietro mezza tela vuota.
LOGO_BOX = {
    0: ("plaga-wordmark", "PLAGA", (79.44, 166.64, 293.31, 94.78)),
    1: ("plaga-tagline", "#DOWHATYOULOVE", (132.69, 277.94, 186.69, 11.61)),
}


def estrai_logo():
    """Ricava logo/*.svg dal vettoriale originale, se non ci sono già.

    Il file di partenza contiene marchio e payoff come due gruppi con colori
    fissi. Qui vengono separati, ritagliati e messi su currentColor, così nelle
    pagine prendono il colore dal CSS invece di averne uno cucito addosso.
    """
    out = Path(__file__).parent / "logo"
    if (out / "plaga-wordmark.svg").exists():
        return
    if not LOGO_MASTER.exists():
        print(f"  nota: manca {LOGO_MASTER.name}, uso il ripiego a caratteri")
        return
    src = LOGO_MASTER.read_text()
    out.mkdir(exist_ok=True)
    for i, (attr, inner) in enumerate(re.findall(r"<g([^>]*)>(.*?)</g>", src, re.S)):
        if i not in LOGO_BOX:
            continue
        nome, titolo, (x, y, w, h) = LOGO_BOX[i]
        tr = re.search(r'transform="([^"]+)"', attr)
        d = re.search(r'\sd="([^"]+)"', inner)
        if not (tr and d):
            continue
        (out / f"{nome}.svg").write_text(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x} {y} {w} {h}" '
            f'role="img" aria-label="{titolo}">'
            f'<g transform="{tr.group(1)}" fill="currentColor" stroke="none">'
            f'<path d="{d.group(1)}"/></g></svg>')
        print(f"  rigenerato logo/{nome}.svg")


def logo_parts():
    """viewBox, trasformazione e tracciato del marchio vettorializzato.

    Se logo/plaga-wordmark.svg non c'è ancora, torna None e il sito ripiega
    sulla parola composta a caratteri: meglio un ripiego onesto di un logo finto.
    Per generarlo:  python3 trace_logo.py /percorso/del/logo.jpeg
    """
    if not LOGO_SVG.exists():
        return None
    t = LOGO_SVG.read_text()
    vb = re.search(r'viewBox="([^"]+)"', t)
    tr = re.search(r'<g[^>]*transform="([^"]+)"', t)
    d = re.search(r'\sd="([^"]+)"', t)
    if not (vb and d):
        return None
    return {"vb": vb.group(1), "tr": tr.group(1) if tr else "", "d": d.group(1)}


estrai_logo()
LOGO = logo_parts()


def wordmark(cls):
    """Il marchio, inline, che prende il colore dal CSS via currentColor."""
    if not LOGO:
        return f'<span class="{cls} {cls}--text">PLAGA</span>'
    g = f' transform="{LOGO["tr"]}"' if LOGO["tr"] else ""
    return (f'<svg class="{cls}" viewBox="{LOGO["vb"]}" role="img" aria-label="PLAGA">'
            f'<g{g} fill="currentColor"><path d="{LOGO["d"]}"/></g></svg>')


def loader_block():
    """Il marchio due volte: contorno e pieno, separati da un fronte morbido.

    Due maschere complementari scorrono insieme da sinistra a destra: dove è
    già passato il colore il contorno sparisce, davanti resta solo il contorno.
    Così il pieno non «appare», subentra — e non c'è nessuna dissolvenza secca.
    """
    if not LOGO:
        mark = '<span class="loaderLogo loaderLogo--text">PLAGA</span>'
        return _loader_wrap(mark)

    g = f' transform="{LOGO["tr"]}"' if LOGO["tr"] else ""
    x, y, w, h = (float(v) for v in LOGO["vb"].split())
    banda = w * 0.24                      # larghezza del fronte sfumato
    x0, x1 = x - banda, x                 # posizione iniziale: tutto da riempire
    # il rettangolo delle maschere deborda, così non taglia nulla ai bordi
    rx, ry, rw, rh = x - banda, y - h, w + 2 * banda, h * 3
    rect = f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}"'

    mark = (
        f'<svg class="loaderLogo" viewBox="{LOGO["vb"]}" aria-hidden="true">'
        f'<defs>'
        f'<linearGradient id="plagaFronte" gradientUnits="userSpaceOnUse" '
        f'x1="{x0}" y1="0" x2="{x1}" y2="0">'
        f'<stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient>'
        f'<linearGradient id="plagaFronteInv" gradientUnits="userSpaceOnUse" '
        f'x1="{x0}" y1="0" x2="{x1}" y2="0">'
        f'<stop offset="0" stop-color="#000"/><stop offset="1" stop-color="#fff"/></linearGradient>'
        # la regione della maschera va data per esteso: con userSpaceOnUse i
        # valori predefiniti (-10%/120%) si calcolano sulla dimensione del
        # viewport ma con origine 0,0, e qui cadrebbero fuori dal marchio
        f'<mask id="plagaPieno" maskUnits="userSpaceOnUse" '
        f'x="{rx}" y="{ry}" width="{rw}" height="{rh}">{rect} fill="url(#plagaFronte)"/></mask>'
        f'<mask id="plagaContorno" maskUnits="userSpaceOnUse" '
        f'x="{rx}" y="{ry}" width="{rw}" height="{rh}">{rect} fill="url(#plagaFronteInv)"/></mask>'
        f'</defs>'
        f'<g mask="url(#plagaContorno)"><g{g}>'
        f'<path class="loaderLogo__line" d="{LOGO["d"]}" fill="none" '
        f'stroke="currentColor" stroke-width="2.2" vector-effect="non-scaling-stroke"/>'
        f'</g></g>'
        f'<g mask="url(#plagaPieno)"><g{g}>'
        f'<path class="loaderLogo__fill" d="{LOGO["d"]}" fill="currentColor"/>'
        f'</g></g>'
        f'</svg>')
    return _loader_wrap(mark)


def _loader_wrap(mark):
    return f"""<div class="loader" id="loader" aria-hidden="true">
  <div class="loader__inner">
    {mark}
    <p class="loader__tag">{TAGLINE}</p>
  </div>
</div>"""

# ═══════════════════════════════ TESTI ═══════════════════════════════

T = {
    "it": {
        "dir": "",                      # italiano nella radice
        "other": "en", "self_label": "IT",
        "nav": ["Home", "Le Sale", "Il Giardino", "Il Forno", "Il Menu", "Contatti"],
        "burger_open": "Apri il menu",
        "burger_close": "Chiudi il menu",
        "lang_label": "Lingua",
        "home_aria": "PLAGA — home",
        "tagline": "Ristorante <i>·</i> Pizzeria <i>·</i> Lounge Bar",
        "book": "Prenota", "where": "Dove", "follow": "Seguici",
        "addr_foot": "Piazza Umberto I<br>73044 Galatone (LE)",
        "addr_short": "Piazza Umberto I, Galatone (LE)",
        "titles": {
            "index": "PLAGA — Ristorante · Pizzeria · Lounge Bar · Galatone",
            "sale": "Le Sale — PLAGA",
            "giardino": "Il Giardino — PLAGA",
            "forno": "Il Forno — PLAGA",
            "menu": "Il Menu — PLAGA",
            "contatti": "Contatti — PLAGA",
        },
        "descs": {
            "index": "Ristorante, pizzeria e lounge bar sotto le volte in pietra leccese, con giardino a cielo aperto. Galatone, Salento.",
            "sale": "Le sale di Plaga: volte a stella in pietra leccese, marmo e velluto verde.",
            "giardino": "Il giardino di Plaga: una corte bianca a cielo aperto con cactus, palme e luci sospese.",
            "forno": "Il forno a legna di Plaga: impasti a lunga lievitazione, cereali e carbone vegetale.",
            "menu": "Antipasti, primi, secondi e pizze di Plaga a Galatone.",
            "contatti": "Prenota un tavolo da Plaga: Piazza Umberto I, Galatone (LE). Tel 351 572 1939.",
        },
        "leads": {
            "index": "Volte in pietra leccese, un giardino a cielo aperto e un forno a legna.",
            "sale": "Marmo, legno e velluto verde sotto volte a stella.",
            "giardino": "Una corte bianca a cielo aperto. Cactus, palme e luci sospese.",
            "forno": "Impasti a lunga lievitazione. Cereali, carbone vegetale.",
            "menu": "Cucina di mare e di terra, pizza a lunga lievitazione.",
            "contatti": "Chiamaci, ti troviamo posto.",
        },
        "h1": {"sale": "Le Sale", "giardino": "Il Giardino", "forno": "Il Forno",
               "menu": "Il Menu", "contatti": "Prenota"},
        "caps": {
            "volte": "La sala delle volte", "bancone": "Il bancone", "candele": "Le candele",
            "ingresso": "L'ingresso", "stelle": "Le volte a stella", "tamburelli": "I tamburelli",
            "tavolata": "La tavolata", "palme": "Le palme", "luci": "Le luci sospese",
            "due": "Il tavolo per due", "coperti": "I coperti",
        },
        "slots": ["Le pizze <i>—</i> in arrivo", "I piatti <i>—</i> in arrivo",
                  "La cucina <i>—</i> in arrivo"],
        "btn_menu": "Vedi il menu",
        "btn_drinks": "Vini, birre e cocktail",
        "note": "Prezzi in euro, coperto €2.",
        "contact": [("Telefono", TEL, "tel:" + TEL_HREF),
                    ("Indirizzo", "Piazza Umberto I, Galatone", MAPS),
                    ("Instagram", "@plaga.lounge", IG),
                    ("Menu digitale", "digitavolo.com", MENU_URL)],
        "alt": {
            "sala-volte": "La sala di Plaga sotto le volte in pietra leccese",
            "bar-arco": "Il bancone in pietra sotto l'arco",
            "giardino-cactus": "Il giardino con cactus e luci sospese",
            "forno": "Il forno a legna e il bancone verde salvia",
            "sala-candele": "Tavolo apparecchiato con candele",
            "sala-volte-b": "Sala principale con tavoli apparecchiati",
            "bar-arco-v": "Il bancone bar in pietra sotto l'arco",
            "ingresso": "Ingresso con lampadario di cristallo e scalinata",
            "sala-volte-v": "Sala vista dall'alto con le volte a stella",
            "tamburelli": "Tamburelli salentini con il marchio Plaga alle pareti",
            "giardino-pano": "Il giardino esterno di Plaga visto d'insieme",
            "giardino-tavolata": "Lunga tavolata in marmo nel giardino",
            "giardino-palme-v": "Palme e vasi in terracotta colorati",
            "giardino-lampada-v": "Tavolo per due sotto la lampada a raggiera",
            "giardino-tavolata-v": "Dettaglio dei coperti sulla tavolata in marmo",
            "insegna": "L'insegna luminosa PLAGA tra le piante",
        },
    },
    "en": {
        "dir": "en",
        "other": "it", "self_label": "EN",
        "nav": ["Home", "The Rooms", "The Garden", "The Oven", "The Menu", "Contact"],
        "burger_open": "Open menu",
        "burger_close": "Close menu",
        "lang_label": "Language",
        "home_aria": "PLAGA — home",
        "tagline": "Restaurant <i>·</i> Pizzeria <i>·</i> Lounge Bar",
        "book": "Book", "where": "Where", "follow": "Follow",
        "addr_foot": "Piazza Umberto I<br>73044 Galatone (LE), Italy",
        "addr_short": "Piazza Umberto I, Galatone (LE)",
        "titles": {
            "index": "PLAGA — Restaurant · Pizzeria · Lounge Bar · Galatone",
            "sale": "The Rooms — PLAGA",
            "giardino": "The Garden — PLAGA",
            "forno": "The Oven — PLAGA",
            "menu": "The Menu — PLAGA",
            "contatti": "Contact — PLAGA",
        },
        "descs": {
            "index": "Restaurant, pizzeria and lounge bar under Lecce stone vaults, with an open-air garden. Galatone, Salento, Puglia.",
            "sale": "The rooms at Plaga: Lecce stone star vaults, marble and green velvet.",
            "giardino": "The garden at Plaga: a white open-air courtyard with cacti, palms and hanging lights.",
            "forno": "The wood-fired oven at Plaga: long-fermented dough, wholegrain and charcoal bases.",
            "menu": "Starters, pasta, mains and pizza at Plaga in Galatone, Puglia.",
            "contatti": "Book a table at Plaga: Piazza Umberto I, Galatone (LE), Italy. Tel +39 351 572 1939.",
        },
        "leads": {
            "index": "Lecce stone vaults, an open-air garden and a wood-fired oven.",
            "sale": "Marble, wood and green velvet beneath star vaults.",
            "giardino": "A white open-air courtyard. Cacti, palms and hanging lights.",
            "forno": "Long-fermented dough. Wholegrain and charcoal bases.",
            "menu": "Sea and land cooking, long-fermented pizza.",
            "contatti": "Call us, we'll find you a table.",
        },
        "h1": {"sale": "The Rooms", "giardino": "The Garden", "forno": "The Oven",
               "menu": "The Menu", "contatti": "Book"},
        "caps": {
            "volte": "The vaulted room", "bancone": "The bar", "candele": "Candlelight",
            "ingresso": "The entrance", "stelle": "The star vaults", "tamburelli": "The tambourines",
            "tavolata": "The long table", "palme": "The palms", "luci": "The hanging lights",
            "due": "Table for two", "coperti": "The place settings",
        },
        "slots": ["Pizzas <i>—</i> coming soon", "Dishes <i>—</i> coming soon",
                  "The kitchen <i>—</i> coming soon"],
        "btn_menu": "See the menu",
        "btn_drinks": "Wines, beers and cocktails",
        "note": "Prices in euro, €2 cover charge.",
        "contact": [("Phone", TEL, "tel:" + TEL_HREF),
                    ("Address", "Piazza Umberto I, Galatone", MAPS),
                    ("Instagram", "@plaga.lounge", IG),
                    ("Digital menu", "digitavolo.com", MENU_URL)],
        "alt": {
            "sala-volte": "The dining room at Plaga beneath Lecce stone vaults",
            "bar-arco": "The stone bar counter under the arch",
            "giardino-cactus": "The garden with cacti and hanging lights",
            "forno": "The wood-fired oven and the sage green counter",
            "sala-candele": "Table laid with candles",
            "sala-volte-b": "Main dining room with laid tables",
            "bar-arco-v": "The stone bar counter under the arch",
            "ingresso": "Entrance with crystal chandelier and stone stairs",
            "sala-volte-v": "Dining room seen from above with star vaults",
            "tamburelli": "Salento tambourines branded Plaga on the wall",
            "giardino-pano": "Wide view of the outdoor garden at Plaga",
            "giardino-tavolata": "Long marble table in the garden",
            "giardino-palme-v": "Palms and colourful terracotta pots",
            "giardino-lampada-v": "Table for two beneath the starburst lamp",
            "giardino-tavolata-v": "Close-up of place settings on the marble table",
            "insegna": "The illuminated PLAGA sign among the plants",
        },
    },
}

# ═══════════════════════════════ MENU ═══════════════════════════════
# (nome_it, nome_en, descrizione_it, descrizione_en, prezzo, in_evidenza)
# I nomi delle pizze restano in italiano: sono nomi propri.

MENU = [
    ("antipasti", "Antipasti", "Starters", [
        ("Cuore di carciofo", "Artichoke heart",
         "Tartare di gambero rosso e spuma di burrata",
         "Red prawn tartare and burrata mousse", 18, True),
        ("Carpaccio di salmone", "Salmon carpaccio",
         "Gravlax agli agrumi, crema al mango e zest di limone",
         "Citrus gravlax, mango cream and lemon zest", 16, False),
        ("Antipasto del giorno", "Starter of the day",
         "Focaccia con tartare di tonno e maionese all'aglio nero",
         "Focaccia with tuna tartare and black garlic mayonnaise", 16, False),
        ("Capocollo, burrata e noci", "Capocollo, burrata and walnuts",
         "Capocollo di Martina Franca e burrata pugliese",
         "Martina Franca capocollo and Apulian burrata", 15, False),
        ("Gamberi in tempura", "Tempura prawns",
         "Con salsa agrodolce", "With sweet and sour sauce", 15, False),
        ("Polpette di vitello", "Veal meatballs",
         "Pomodoro fresco e crema al pecorino",
         "Fresh tomato and pecorino cream", 12, False),
        ("Fritto misto", "Mixed fry",
         "Polpette, crocchette di patate, melanzane e verdure pastellate",
         "Meatballs, potato croquettes, aubergine and battered vegetables", 12, False),
    ]),
    ("primi", "Primi", "Pasta", [
        ("Troccoli al gambero", "Troccoli with red prawn",
         "Crema di zucchine, tartare di gambero rosso e mandorle tostate",
         "Courgette cream, red prawn tartare and toasted almonds", 18, False),
        ("Troccoli al tonno", "Troccoli with tuna",
         "Crema di aglio nero, peperoncino e tartare di tonno",
         "Black garlic cream, chilli and tuna tartare", 18, False),
        ("Calamarata", "Calamarata",
         "Pesto di pistacchio e code di scampo",
         "Pistachio pesto and langoustine tails", 18, False),
        ("Primo del giorno", "Pasta of the day",
         "Fusilloni con demi-glace e tartufo nero estivo",
         "Fusilloni with demi-glace and summer black truffle", 17, False),
        ("Orecchiette e burrata", "Orecchiette and burrata",
         "Datterino giallo, crumble di tarallo e burrata",
         "Yellow datterino tomato, tarallo crumble and burrata", 15, False),
    ]),
    ("secondi", "Secondi", "Mains", [
        ("Pluma iberica", "Iberian pluma",
         "Demi-glace e finferli saltati al porro",
         "Demi-glace and chanterelles sautéed with leek", 30, False),
        ("Polpo", "Octopus",
         "Crema di patate viola e pomodorini in acqua di mare",
         "Purple potato cream and tomatoes in sea water", 18, True),
        ("Tagliata di tonno", "Sliced tuna",
         "Teriyaki, crema di avocado e porro saltato",
         "Teriyaki, avocado cream and sautéed leek", 18, False),
        ("Tagliata di scottona", "Sliced beef",
         "Patate novelle a spicchi e chimichurri",
         "New potato wedges and chimichurri", 18, False),
        ("Bombette", "Bombette",
         "Capocollo di Martina Franca e scamorza affumicata",
         "Martina Franca capocollo and smoked scamorza", 13, False),
    ]),
    ("special", "Plaga's Special", "Plaga's Special", [
        ("Iberica", "Iberica",
         "Prosciutto iberico 36 mesi e tartufo nero estivo",
         "36-month Iberian ham and summer black truffle", 18, False),
        ("Agrumata", "Agrumata",
         "Salmone marinato agli agrumi, rucola e pomodorini gialli",
         "Citrus-marinated salmon, rocket and yellow tomatoes", 15, True),
        ("Santa Maria", "Santa Maria",
         "Datterino giallo, tartare di tonno, stracciatella e polvere di capperi",
         "Yellow datterino, tuna tartare, stracciatella and caper powder", 15, False),
        ("Ariccia", "Ariccia",
         "Porchetta romana, cipolla caramellata e olive taggiasche",
         "Roman porchetta, caramelised onion and taggiasca olives", 15, False),
        ("Do what you love", "Do what you love",
         "Crema di patate, salsiccia a punta di coltello e pecorino",
         "Potato cream, hand-cut sausage and pecorino", 13, False),
    ]),
    ("rosse", "Pizze Rosse", "Red Pizzas", [
        ("Pugliese", "Pugliese",
         "Capocollo di Martina Franca e stracciatella",
         "Martina Franca capocollo and stracciatella", 13, False),
        ("Sara", "Sara",
         "Polpette di carne, cacioricotta e basilico",
         "Meatballs, cacioricotta and basil", 12, False),
        ("Pola", "Pola",
         "Pomodorini, gorgonzola e radicchio grigliato",
         "Cherry tomatoes, gorgonzola and grilled radicchio", 12, False),
        ("Crudaiola", "Crudaiola",
         "Prosciutto crudo, rucola e grana",
         "Prosciutto, rocket and grana", 10, False),
        ("Quattro formaggi", "Four cheeses",
         "Emmental, grana e gorgonzola",
         "Emmental, grana and gorgonzola", 9, False),
        ("Quattro stagioni", "Four seasons",
         "Funghi, carciofi, olive e prosciutto cotto",
         "Mushrooms, artichokes, olives and ham", 9, False),
        ("Diavola", "Diavola",
         "Salame piccante", "Spicy salami", 8, False),
        ("Margherita", "Margherita",
         "Pomodoro, fior di latte, basilico",
         "Tomato, fior di latte, basil", 6, False),
    ]),
    ("bianche", "Pizze Bianche", "White Pizzas", [
        ("Plaga", "Plaga",
         "Crema di ricotta e noci, guanciale croccante e pomodorino semi-dry",
         "Ricotta and walnut cream, crisp guanciale and semi-dried tomato", 13, True),
        ("Crocché", "Crocché",
         "Bufala, pancetta croccante, pesto e crocchette di patate",
         "Buffalo mozzarella, crisp pancetta, pesto and potato croquettes", 13, False),
        ("Scialabà", "Scialabà",
         "Salsiccia, scamorza affumicata e patate al forno",
         "Sausage, smoked scamorza and roast potatoes", 12, False),
        ("Dop", "Dop",
         "Mortadella, stracciatella e granella di pistacchio",
         "Mortadella, stracciatella and chopped pistachio", 12, False),
        ("Campana", "Campana",
         "Salsiccia e friarielli", "Sausage and friarielli greens", 9, False),
        ("Caprese", "Caprese",
         "Pomodorini, grana e rucola, tutto a crudo",
         "Cherry tomatoes, grana and rocket, all uncooked", 9, False),
    ]),
    ("dessert", "Dessert", "Desserts", [
        ("Tiramisù Lotus", "Lotus tiramisù",
         "Con biscotti e crema Lotus Biscoff",
         "With Lotus Biscoff biscuits and cream", 6, False),
        ("Delizia tropicale", "Tropical delight",
         "Cocco con cuore morbido al mango e passion fruit",
         "Coconut with a soft mango and passion fruit centre", 6, False),
    ]),
]

# ═══════════════════════════════ PEZZI ═══════════════════════════════


def impronta(rel):
    """Poche cifre ricavate dal contenuto del file.

    Finiscono in coda a css e js come ?v=…: quando il file cambia cambia anche
    l'indirizzo, e nessun browser può continuare a servire la copia vecchia.
    Va rilanciato build.py dopo ogni modifica a style.css o main.js.
    """
    f = OUT / rel
    if not f.exists():
        return "0"
    return hashlib.md5(f.read_bytes()).hexdigest()[:8]


def picture(root, name, alt, lazy=True):
    load = ' loading="lazy"' if lazy else ' fetchpriority="high"'
    return (f'<picture class="pic">'
            f'<source media="(max-width:700px)" srcset="{root}assets/img/{name}-sm.webp">'
            f'<img src="{root}assets/img/{name}-lg.webp" alt="{alt}"{load}>'
            f'</picture>')


def lang_switch(lang, name):
    """IT / EN — la lingua attiva non è un link."""
    t = T[lang]
    other = T[t["other"]]
    href = f'en/{name}.html' if t["dir"] == "" else f'../{name}.html'
    return (f'<div class="lang" role="group" aria-label="{t["lang_label"]}">'
            f'<span class="lang__on" aria-current="true">{t["self_label"]}</span>'
            f'<span class="lang__sep" aria-hidden="true">/</span>'
            f'<a class="lang__off" href="{href}" hreflang="{t["other"]}" '
            f'lang="{t["other"]}">{other["self_label"]}</a></div>')


def overlay(lang, name):
    t = T[lang]
    items = []
    for i, slug in enumerate(PAGES):
        cur = ' aria-current="page"' if slug == name else ""
        items.append(
            f'<li class="menuNav__item"><a href="{slug}.html"{cur}>'
            f'<span class="menuNav__num">{i + 1:02d}</span>'
            f'<span class="menuNav__label">{t["nav"][i]}</span></a></li>')
    return f"""<nav class="menuOverlay" id="menuOverlay" aria-hidden="true">
  <div class="menuOverlay__bg"><i></i><i></i><i></i><i></i></div>
  <div class="menuOverlay__inner">
    <ul class="menuNav">
      {"".join(items)}
    </ul>
    <div class="menuFoot">
      <div class="menuFoot__col"><span class="menuFoot__k">{t["book"]}</span>
        <a href="tel:{TEL_HREF}" class="menuFoot__v">{TEL}</a></div>
      <div class="menuFoot__col"><span class="menuFoot__k">{t["where"]}</span>
        <a href="{MAPS}" target="_blank" rel="noopener" class="menuFoot__v">{t["addr_short"]}</a></div>
      <div class="menuFoot__col"><span class="menuFoot__k">{t["follow"]}</span>
        <a href="{IG}" target="_blank" rel="noopener" class="menuFoot__v">@plaga.lounge</a></div>
    </div>
  </div>
</nav>"""


def header(lang, name, light=False):
    t = T[lang]
    return f"""<header class="nav{' is-light' if light else ''}" id="nav">
  <a href="index.html" class="nav__brand" aria-label="{t["home_aria"]}">{wordmark("navMark")}</a>
  <div class="nav__right">
    {lang_switch(lang, name)}
    <button class="burger" id="burger" aria-label="{t["burger_open"]}" aria-expanded="false"
            aria-controls="menuOverlay" data-open="{t["burger_open"]}" data-close="{t["burger_close"]}">
      <span class="burger__box"><i class="burger__line burger__line--1"></i><i class="burger__line burger__line--2"></i></span>
    </button>
  </div>
</header>
{overlay(lang, name)}"""


def footer(lang):
    t = T[lang]
    return f"""<footer class="foot">
  <div class="foot__grid">
    <div class="foot__col"><span class="foot__k">{t["book"]}</span>
      <a href="tel:{TEL_HREF}" class="foot__v">{TEL}</a></div>
    <div class="foot__col"><span class="foot__k">{t["where"]}</span>
      <a href="{MAPS}" target="_blank" rel="noopener" class="foot__v">{t["addr_foot"]}</a></div>
    <div class="foot__col"><span class="foot__k">{t["follow"]}</span>
      <a href="{IG}" target="_blank" rel="noopener" class="foot__v">@plaga.lounge</a></div>
  </div>
  <div class="foot__bottom">
    <span class="foot__mark">{wordmark("footMark")}<em>{TAGLINE}</em></span>
    <p>{t["tagline"]}</p>
  </div>
</footer>"""


def page(lang, name, body, light_nav=False, loader=False):
    t = T[lang]
    root = "" if t["dir"] == "" else "../"
    it_url = f"{name}.html" if t["dir"] == "" else f"../{name}.html"
    en_url = f"en/{name}.html" if t["dir"] == "" else f"{name}.html"

    html = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{t["titles"][name]}</title>
<meta name="description" content="{t["descs"][name]}">
<meta name="theme-color" content="#E8DBC7">
<link rel="alternate" hreflang="it" href="{it_url}">
<link rel="alternate" hreflang="en" href="{en_url}">
<link rel="alternate" hreflang="x-default" href="{it_url}">
<meta property="og:title" content="{t["titles"][name]}">
<meta property="og:description" content="{t["descs"][name]}">
<meta property="og:image" content="{root}assets/img/sala-volte-lg.webp">
<meta property="og:locale" content="{'it_IT' if lang == 'it' else 'en_GB'}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,300..900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}css/style.css?v={impronta("css/style.css")}">
</head>
<body>
{loader_block() if loader else ""}
{header(lang, name, light_nav)}
<main id="top">
{body}
</main>
{footer(lang)}
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/lenis@1.1.18/dist/lenis.min.js"></script>
<script src="{root}js/main.js?v={impronta("js/main.js")}"></script>
</body>
</html>
"""
    folder = OUT / t["dir"] if t["dir"] else OUT
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{name}.html").write_text(html, encoding="utf-8")


# ═══════════════════════════════ PAGINE ═══════════════════════════════

def _root(lang):
    return "" if T[lang]["dir"] == "" else "../"


def build_home(lang):
    t = T[lang]
    r = _root(lang)
    cards = [("sale", 1, "bar-arco"), ("giardino", 2, "giardino-cactus"),
             ("forno", 3, "forno"), ("menu", 4, "sala-candele")]
    html_cards = "".join(
        f'<a class="card" href="{slug}.html">'
        f'<div class="card__media">{picture(r, img, t["alt"][img])}</div>'
        f'<span class="card__title">{t["nav"][i]}</span></a>'
        for slug, i, img in cards)

    return f"""<section class="hero">
  <div class="hero__media">{picture(r, "sala-volte", t["alt"]["sala-volte"], lazy=False)}</div>
  <div class="hero__scrim"></div>
  <div class="hero__content">
    <h1 class="hero__word">PLAGA</h1>
    <p class="hero__sub">{t["tagline"]}</p>
  </div>
</section>

<section class="intro">
  <p class="lead">{t["leads"]["index"]}</p>
</section>

<section class="cards">{html_cards}</section>"""


def _fig(lang, cls, img, cap):
    t = T[lang]
    return (f'<figure class="g {cls}">{picture(_root(lang), img, t["alt"][img])}'
            f'<figcaption>{cap}</figcaption></figure>')


def build_sale(lang):
    t = T[lang]
    c = t["caps"]
    return f"""<section class="pageHead">
  <h1 class="pageTitle">{t["h1"]["sale"]}</h1>
  <p class="lead">{t["leads"]["sale"]}</p>
</section>

<section class="gallery">
  {_fig(lang, "g--wide", "sala-volte-b", c["volte"])}
  {_fig(lang, "g--tall", "bar-arco-v", c["bancone"])}
  {_fig(lang, "g--half", "sala-candele", c["candele"])}
  {_fig(lang, "g--half", "ingresso", c["ingresso"])}
  {_fig(lang, "g--tall", "sala-volte-v", c["stelle"])}
  {_fig(lang, "g--wide", "tamburelli", c["tamburelli"])}
</section>"""


def build_giardino(lang):
    t = T[lang]
    c = t["caps"]
    return f"""<section class="pageHead">
  <h1 class="pageTitle">{t["h1"]["giardino"]}</h1>
  <p class="lead">{t["leads"]["giardino"]}</p>
</section>

<section class="bleed">{picture(_root(lang), "giardino-pano", t["alt"]["giardino-pano"], lazy=False)}</section>

<section class="gallery">
  {_fig(lang, "g--wide", "giardino-tavolata", c["tavolata"])}
  {_fig(lang, "g--tall", "giardino-palme-v", c["palme"])}
  {_fig(lang, "g--half", "giardino-cactus", c["luci"])}
  {_fig(lang, "g--half", "giardino-lampada-v", c["due"])}
  {_fig(lang, "g--tall", "giardino-tavolata-v", c["coperti"])}
</section>"""


def build_forno(lang):
    t = T[lang]
    slot = ('<figure class="slot"><div class="slot__box">'
            '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/>'
            '<circle cx="12" cy="12" r="3.2"/></svg></div><figcaption>{}</figcaption></figure>')
    return f"""<section class="pageHead">
  <h1 class="pageTitle">{t["h1"]["forno"]}</h1>
  <p class="lead">{t["leads"]["forno"]}</p>
</section>

<section class="bleed">{picture(_root(lang), "forno", t["alt"]["forno"], lazy=False)}</section>

<!-- SLOT FOTO IN ARRIVO — pizze, piatti, cucina.
     Quando avrai le foto: convertile in webp in assets/img/ e qui in build.py
     sostituisci i tre slot con delle figure vere, per esempio
       _fig(lang, "g--third", "pizza-01", "Nome della pizza")
     ricordando di aggiungere nome file e testo alternativo nel dizionario "alt"
     di entrambe le lingue. Poi rilancia: python3 build.py -->
<section class="slots">
  {slot.format(t["slots"][0])}
  {slot.format(t["slots"][1])}
  {slot.format(t["slots"][2])}
</section>

<section class="cta">
  <a class="btn" href="menu.html"><span>{t["btn_menu"]}</span>
    <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a>
</section>"""


def build_menu(lang):
    t = T[lang]
    ni, di = (1, 3) if lang == "en" else (0, 2)   # indice nome / descrizione
    ci = 2 if lang == "en" else 1                  # indice etichetta categoria

    tabs = "".join(
        f'<button class="menuTab{" is-active" if i == 0 else ""}" role="tab" '
        f'aria-selected="{"true" if i == 0 else "false"}" data-tab="{cat[0]}">{cat[ci]}</button>'
        for i, cat in enumerate(MENU))

    panels = ""
    for i, cat in enumerate(MENU):
        rows = "".join(
            f'<article class="dish{" is-featured" if d[5] else ""}">'
            f'<h3>{d[ni]}</h3><p>{d[di]}</p>'
            f'<span class="dish__price">{d[4]}</span></article>'
            for d in cat[3])
        panels += (f'<div class="menuPanel{" is-active" if i == 0 else ""}" data-panel="{cat[0]}" '
                   f'role="tabpanel"{"" if i == 0 else " hidden"}>{rows}</div>')

    return f"""<section class="pageHead">
  <h1 class="pageTitle">{t["h1"]["menu"]}</h1>
  <p class="lead">{t["leads"]["menu"]}</p>
</section>

<section class="menu">
  <div class="menuTabs" role="tablist" aria-label="{t["h1"]["menu"]}">
    {tabs}<span class="menuTabs__ink" data-tab-ink></span>
  </div>
  <div class="menuPanels">{panels}</div>
  <div class="cta">
    <a class="btn" href="{MENU_URL}" target="_blank" rel="noopener"><span>{t["btn_drinks"]}</span>
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a>
    <p class="note">{t["note"]}</p>
  </div>
</section>"""


def build_contatti(lang):
    t = T[lang]
    rows = "".join(
        f'<a class="contact__row" href="{href}"'
        f'{" target=" + chr(34) + "_blank" + chr(34) + " rel=" + chr(34) + "noopener" + chr(34) if href.startswith("http") else ""}>'
        f'<span class="contact__k">{k}</span><span class="contact__v">{v}</span></a>'
        for k, v, href in t["contact"])
    return f"""<section class="pageHead">
  <h1 class="pageTitle">{t["h1"]["contatti"]}</h1>
  <p class="lead">{t["leads"]["contatti"]}</p>
</section>

<section class="contact">{rows}</section>

<section class="bleed">{picture(_root(lang), "insegna", t["alt"]["insegna"])}</section>"""


BUILDERS = {"index": build_home, "sale": build_sale, "giardino": build_giardino,
            "forno": build_forno, "menu": build_menu, "contatti": build_contatti}

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for lang in T:
        for name in PAGES:
            page(lang, name, BUILDERS[name](lang),
                 light_nav=(name == "index"), loader=(name == "index"))
        print(f"{lang}: {len(PAGES)} pagine in {T[lang]['dir'] or 'site'}/")
