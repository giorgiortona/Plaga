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
from urllib.parse import quote

OUT = Path(__file__).parent / "site"

TEL_HREF = "+393515721939"
TEL = "351 572 1939"
IG = "https://www.instagram.com/plaga.lounge/"
MAPS = "https://www.google.com/maps/place/Plaga+Lounge/@40.1478749,18.0728846,17z"
MENU_URL = "https://www.digitavolo.com/plaga/menu"

# Il numero apre WhatsApp con il messaggio gia' pronto, non il dialer.
WA_NUM = "393515721939"
WA_TESTO = {"it": "Ciao, vorrei prenotare un tavolo da PLAGA. ",
            "en": "Hello, I would like to book a table at PLAGA. "}


def wa_href(lang):
    return f"https://wa.me/{WA_NUM}?text={quote(WA_TESTO[lang])}"


# Pagine legali: stanno fuori da PAGES, cosi' non entrano nel burger menu.
LEGAL_PAGES = ["privacy", "cookie"]

# Domini di terze parti contattati al caricamento di ogni pagina. Verificati
# sul sito vero, non dedotti: se cambiano gli script, va aggiornata la cookie
# policy che li elenca.
TERZE_PARTI = ["fonts.googleapis.com", "fonts.gstatic.com",
               "cdnjs.cloudflare.com", "cdn.jsdelivr.net"]

# ATTENZIONE — da completare prima della pubblicazione.
TITOLARE = {
    "nome": "[DA COMPLETARE: ragione sociale]",
    "piva": "[DA COMPLETARE: P. IVA / C.F.]",
    "sede": "[DA COMPLETARE: sede legale]",
    "email": "[DA COMPLETARE: indirizzo e-mail]",
}
CREATOR_URL = "https://www.instagram.com/dimana.digitalcreations/"

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
        "btn_back": "TORNA AL SITO",
        "btn_top": "TORNA SU",
        "call": "Chiama",
        "call_aria": "Scrivi su WhatsApp al 351 572 1939",
        "legal_updated_label": "Ultimo aggiornamento:",
        "legal_nav": "Informative legali",
        "leave": {
            "kicker": "Collegamento esterno",
            "titolo": "Stai per lasciare il sito di PLAGA",
            "testo": "Il menu digitale \u00e8 ospitato da <strong>digitavolo.com</strong>, "
                     "un servizio esterno non gestito da PLAGA, che applica proprie "
                     "condizioni d\u2019uso e informativa sulla privacy.",
            "url_label": "Destinazione",
            "annulla": "Annulla",
            "continua": "Apri digitavolo.com",
        },
        "titles": {
            "index": "PLAGA — Ristorante · Pizzeria · Lounge Bar · Galatone",
            "sale": "Le Sale — PLAGA",
            "giardino": "Il Giardino — PLAGA",
            "forno": "Il Forno — PLAGA",
            "menu": "Il Menu — PLAGA",
            "contatti": "Contatti — PLAGA",
            "privacy": "Privacy policy — PLAGA",
            "cookie": "Cookie policy — PLAGA",
        },
        "descs": {
            "index": "Ristorante, pizzeria e lounge bar sotto le volte in pietra leccese, con giardino a cielo aperto. Galatone, Salento.",
            "sale": "Le sale di Plaga: volte a stella in pietra leccese, marmo e velluto verde.",
            "giardino": "Il giardino di Plaga: una corte bianca a cielo aperto con cactus, palme e luci sospese.",
            "forno": "Il forno a legna di Plaga: impasti a lunga lievitazione, cereali e carbone vegetale.",
            "menu": "Antipasti, primi, secondi e pizze di Plaga a Galatone.",
            "contatti": "Prenota un tavolo da Plaga: Piazza Umberto I, Galatone (LE). Tel 351 572 1939.",
            "privacy": "Informativa privacy del sito Plaga, Galatone (LE).",
            "cookie": "Cookie policy e inventario tecnico del sito Plaga, Galatone (LE).",
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
        "contact": [("WhatsApp", TEL, wa_href("it")),
                    ("Telefono", TEL, "tel:" + TEL_HREF),
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
        "btn_back": "BACK TO SITE",
        "btn_top": "BACK TO TOP",
        "call": "Call",
        "call_aria": "Message us on WhatsApp at +39 351 572 1939",
        "legal_updated_label": "Last updated:",
        "legal_nav": "Legal notices",
        "leave": {
            "kicker": "External link",
            "titolo": "You are leaving the PLAGA website",
            "testo": "The digital menu is hosted on <strong>digitavolo.com</strong>, "
                     "an external service not operated by PLAGA, with its own terms "
                     "of use and privacy notice.",
            "url_label": "Destination",
            "annulla": "Cancel",
            "continua": "Open digitavolo.com",
        },
        "titles": {
            "index": "PLAGA — Restaurant · Pizzeria · Lounge Bar · Galatone",
            "sale": "The Rooms — PLAGA",
            "giardino": "The Garden — PLAGA",
            "forno": "The Oven — PLAGA",
            "menu": "The Menu — PLAGA",
            "contatti": "Contact — PLAGA",
            "privacy": "Privacy policy — PLAGA",
            "cookie": "Cookie policy — PLAGA",
        },
        "descs": {
            "index": "Restaurant, pizzeria and lounge bar under Lecce stone vaults, with an open-air garden. Galatone, Salento, Puglia.",
            "sale": "The rooms at Plaga: Lecce stone star vaults, marble and green velvet.",
            "giardino": "The garden at Plaga: a white open-air courtyard with cacti, palms and hanging lights.",
            "forno": "The wood-fired oven at Plaga: long-fermented dough, wholegrain and charcoal bases.",
            "menu": "Starters, pasta, mains and pizza at Plaga in Galatone, Puglia.",
            "contatti": "Book a table at Plaga: Piazza Umberto I, Galatone (LE), Italy. Tel +39 351 572 1939.",
            "privacy": "Privacy notice for the Plaga website, Galatone (LE), Italy.",
            "cookie": "Cookie policy and technical inventory of the Plaga website.",
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
        "contact": [("WhatsApp", TEL, wa_href("en")),
                    ("Phone", TEL, "tel:" + TEL_HREF),
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


def picture(root, name, alt, lazy=True, mobile=None):
    """<picture> con le due misure webp.

    `mobile` serve per le foto che su telefono vanno ritagliate diversamente,
    non solo rimpicciolite: un paesaggio 3:2 dentro uno schermo verticale
    perderebbe i lati e mostrerebbe una fascia centrale senza senso.
    """
    load = ' loading="lazy"' if lazy else ' fetchpriority="high"'
    piccola = mobile or f"{name}-sm"
    return (f'<picture class="pic">'
            f'<source media="(max-width:700px)" srcset="{root}assets/img/{piccola}.webp">'
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
        <a href="{wa_href(lang)}" target="_blank" rel="noopener" class="menuFoot__v" aria-label="{t["call_aria"]}">{TEL}</a>
        <a href="tel:{TEL_HREF}" class="menuFoot__call">{t["call"]}</a></div>
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


def footer(lang, sign=True):
    """Il footer, identico su tutte le pagine.

    L'insegna fa da fondo sotto un velo scuro. Lì il marchio
    PLAGA e la tagline sono gia' dentro la foto, quindi non si ripetono in
    sovrimpressione: restano il payoff e la firma. La foto e' decorativa —
    alt vuoto e aria-hidden — perche' il marchio e' gia' testo altrove.
    """
    t = T[lang]
    bg = (f'<div class="foot__bg" aria-hidden="true">'
          f'{picture(_root(lang), "insegna", "")}</div>') if sign else ""
    return f"""<footer class="foot{' foot--sign' if sign else ''}">
  {bg}
  <div class="foot__grid">
    <div class="foot__col"><span class="foot__k">{t["book"]}</span>
      <a href="{wa_href(lang)}" target="_blank" rel="noopener" class="foot__v" aria-label="{t["call_aria"]}">{TEL}</a>
      <a href="tel:{TEL_HREF}" class="foot__call">{t["call"]}</a></div>
    <div class="foot__col"><span class="foot__k">{t["where"]}</span>
      <a href="{MAPS}" target="_blank" rel="noopener" class="foot__v">{t["addr_foot"]}</a></div>
    <div class="foot__col"><span class="foot__k">{t["follow"]}</span>
      <a href="{IG}" target="_blank" rel="noopener" class="foot__v">@plaga.lounge</a></div>
  </div>
  <div class="foot__totop">
    <button class="btn-top" onclick="window.scrollTo(0, 0)">{t["btn_top"]}</button>
  </div>
  <div class="foot__bottom">
    <span class="foot__mark">{"" if sign else wordmark("footMark")}<em>{TAGLINE}</em></span>
    <div class="foot__right">
      {"" if sign else f'<p class="foot__tagline">{tagline_links(lang)}</p>'}
      <p class="foot__credit">created by <a href="{CREATOR_URL}" target="_blank" rel="noopener">Dimana.DigitalCreations</a></p>
      <nav class="foot__legal" aria-label="{t["legal_nav"]}"><a href="privacy.html">Privacy</a><a href="cookie.html">Cookie</a></nav>
    </div>
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
{leave_dialog(lang)}
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

# ═══════════════════════════ TESTI LEGALI ═══════════════════════════
# Adattati dalle informative di Bagno Maria: stessa impostazione, stessa
# struttura, stesso taglio. Le differenze non sono di stile ma di fatto —
# PLAGA non ha motore di prenotazione né selezione di date, ha il menu
# digitale esterno di digitavolo, e soprattutto carica caratteri e librerie
# da terze parti a ogni apertura di pagina. Bagno Maria serviva tutto in
# locale e poteva dichiararlo; qui no, e la cookie policy lo elenca.

LEGAL_UPDATED = {"it": "14 settembre 2026", "en": "14 September 2026"}

LEGAL = {
    "it": {
        "privacy": {
            "titolo": "Privacy policy",
            "kicker": "Informativa ai sensi dell’art. 13 GDPR",
            "intro": "Questa informativa descrive i trattamenti collegati alla consultazione del sito, alle richieste di contatto e alla prenotazione di un tavolo.",
            "indice": [("titolare", "Titolare"), ("dati-finalita", "Dati e finalità"),
                       ("servizi-esterni", "Servizi esterni"), ("destinatari", "Destinatari"),
                       ("conservazione", "Conservazione"), ("diritti", "Diritti")],
            "sezioni": [
                ("titolare", "Titolare del trattamento", """
<p>Il titolare del trattamento è <strong>{nome}</strong>, P. IVA e C.F. <strong>{piva}</strong>, con sede legale in {sede}. PLAGA ha sede operativa in Piazza Umberto I, 73044 Galatone (LE).</p>
<div class="legal__note">Per richieste relative alla protezione dei dati: <a href="mailto:{email}"><strong>{email}</strong></a> oppure <a href="{wa}" target="_blank" rel="noopener"><strong>{tel}</strong></a>.</div>"""),
                ("dati-finalita", "Dati trattati, finalità e basi giuridiche", """
<h3>Dati di navigazione</h3>
<p>I sistemi che rendono disponibile il sito possono registrare dati tecnici quali indirizzo IP, data e ora, pagina richiesta, esito della risposta, browser e sistema operativo. Sono utilizzati per erogare e proteggere il sito, diagnosticare anomalie e prevenire abusi.</p>
<div class="legal__note"><strong>Base giuridica:</strong> legittimo interesse del titolare alla sicurezza e al corretto funzionamento del servizio, art. 6, par. 1, lett. f) GDPR.</div>
<h3>Dati inviati volontariamente</h3>
<p>Quando l’utente scrive su WhatsApp, telefona o invia un’e-mail, i dati comunicati sono trattati per rispondere, fornire informazioni e gestire la prenotazione di un tavolo, nel rapporto precontrattuale o contrattuale che ne deriva. Il sito non contiene moduli di contatto: non raccoglie dati in proprio e non ne invia automaticamente.</p>
<div class="legal__note"><strong>Base giuridica:</strong> misure precontrattuali o contratto, art. 6, par. 1, lett. b) GDPR; adempimento di obblighi legali, lett. c); legittimo interesse alla gestione e tutela del rapporto, lett. f), quando applicabile.</div>"""),
                ("servizi-esterni", "Contatti e servizi esterni", """
<h3>Servizi attivati dall’utente</h3>
<p>Google Maps, Instagram e WhatsApp non sono incorporati nella pagina. Il collegamento al relativo fornitore avviene soltanto dopo il click dell’utente, che visita un servizio distinto soggetto alla propria informativa. I messaggi WhatsApp ed e-mail vengono effettivamente inviati solo mediante un’ulteriore azione nell’applicazione scelta dall’utente.</p>
<p>Il menu digitale è ospitato da <strong>digitavolo.com</strong>, servizio esterno non gestito da PLAGA. Prima di aprirlo il sito mostra un avviso che indica la destinazione e richiede una conferma esplicita. Dal momento dell’apertura il fornitore può ricevere dati tecnici di connessione e opera secondo la propria informativa.</p>
<h3>Risorse caricate automaticamente</h3>
<p>A differenza dei collegamenti sopra, alcune risorse tecniche necessarie alla resa delle pagine sono richieste a terze parti <strong>nel momento stesso in cui si apre il sito</strong>, senza alcuna azione dell’utente: i caratteri tipografici da <code>fonts.googleapis.com</code> e <code>fonts.gstatic.com</code> (Google) e le librerie di animazione da <code>cdnjs.cloudflare.com</code> (Cloudflare) e <code>cdn.jsdelivr.net</code>. Queste richieste comportano la comunicazione dell’indirizzo IP e dei dati tecnici di connessione ai rispettivi fornitori, che operano secondo le proprie informative. Non installano cookie e non sono usate per statistiche o profilazione.</p>
<div class="legal__note"><strong>Base giuridica:</strong> legittimo interesse del titolare alla resa tipografica e al corretto funzionamento del sito, art. 6, par. 1, lett. f) GDPR.</div>"""),
                ("destinatari", "Destinatari e trasferimenti", """
<p>Possono accedere ai dati, nei limiti delle rispettive funzioni, personale autorizzato, consulenti e fornitori tecnici o di hosting che operano per conto del titolare. I dati possono inoltre essere comunicati quando richiesto dalla legge o da un’autorità competente.</p>
<p>Il sito non invia dati a servizi analytics, pubblicitari o social. I trasferimenti collegati al provider di hosting, ai fornitori delle risorse tecniche indicate sopra o ai servizi esterni scelti dall’utente devono avvenire nel rispetto degli artt. 44 e seguenti del GDPR, sulla base di una decisione di adeguatezza o di garanzie appropriate quando necessarie.</p>"""),
                ("conservazione", "Conservazione", """
<p>I dati tecnici sono conservati per il tempo strettamente necessario all’erogazione, alla sicurezza e alla diagnosi del servizio, salvo esigenze di accertamento di abusi o obblighi di legge.</p>
<p>I dati delle richieste sono conservati per il tempo necessario a rispondere e gestire il rapporto; quelli relativi a prenotazioni, contratti e documenti amministrativi seguono i termini previsti dalla legge.</p>"""),
                ("diritti", "Diritti dell’interessato", """
<p>Nei casi previsti, l’interessato può chiedere accesso, rettifica, cancellazione, limitazione, portabilità e opposizione al trattamento ai sensi degli artt. 15–22 GDPR. Le richieste possono essere inviate ai contatti del titolare indicati sopra.</p>
<div class="legal__note">È inoltre possibile proporre reclamo al <a href="https://www.garanteprivacy.it/" target="_blank" rel="noopener"><strong>Garante per la protezione dei dati personali</strong></a> o all’autorità di controllo competente nello Stato SEE in cui si vive o lavora, o nel quale si ritiene sia avvenuta la violazione.</div>"""),
                (None, "Cookie e aggiornamenti", """
<p>Per il dettaglio delle tecnologie utilizzate consulta la <a href="cookie.html"><strong>cookie policy</strong></a>. L’informativa potrà essere aggiornata quando cambiano servizi, finalità o obblighi normativi; la data in alto identifica la versione corrente.</p>"""),
            ],
        },
        "cookie": {
            "titolo": "Cookie policy",
            "kicker": "Tecnologie presenti nel sito",
            "intro": "Alla data dell’ultima verifica il sito non installa cookie, non utilizza strumenti analytics, pubblicitari o di profilazione e non salva nulla nel browser. Richiede però caratteri e librerie a fornitori terzi a ogni apertura di pagina.",
            "indice": [("scelta-banner", "Scelta del banner"), ("inventario", "Inventario"),
                       ("servizi", "Servizi esterni"), ("aggiornamenti", "Aggiornamenti"),
                       ("riferimenti", "Riferimenti")],
            "sezioni": [
                ("scelta-banner", "Perché non compare un banner", """
<div class="legal__note"><strong>Configurazione attuale: nessun consenso richiesto.</strong></div>
<p>Non sono presenti cookie né strumenti facoltativi di misurazione o profilazione. Per questo un banner “Accetta/Rifiuta” non offrirebbe una scelta reale. Quando sono utilizzati soltanto strumenti tecnici, il Garante prevede che l’informazione possa essere resa nella home page o nell’informativa generale.</p>
<p>Le richieste ai fornitori di caratteri e librerie descritte sotto non sono cookie e non leggono né scrivono informazioni sul dispositivo. Comportano però la comunicazione dell’indirizzo IP a terzi, ed è per questo che sono elencate apertamente invece di essere taciute.</p>"""),
                ("inventario", "Inventario tecnico", """
<ul class="legal__inv">
  <li><strong>Cookie di prima parte</strong>Nessuno impostato dall’applicazione.</li>
  <li><strong>Cookie di terza parte</strong>Nessuno.</li>
  <li><strong>LocalStorage e SessionStorage</strong>Non utilizzati. La lingua non è una preferenza salvata: italiano e inglese sono pagine distinte, con indirizzi propri.</li>
  <li><strong>IndexedDB</strong>Non utilizzato.</li>
  <li><strong>Analytics, pixel e tag manager</strong>Non presenti.</li>
  <li><strong>Iframe</strong>Nessuno caricato all’apertura della pagina.</li>
  <li><strong>Immagini e video</strong>Serviti dallo stesso dominio del sito.</li>
  <li><strong>Caratteri tipografici</strong>Archivo, richiesto a <code>fonts.googleapis.com</code> e <code>fonts.gstatic.com</code> (Google) all’apertura di ogni pagina.</li>
  <li><strong>Librerie di animazione</strong>GSAP da <code>cdnjs.cloudflare.com</code> (Cloudflare) e Lenis da <code>cdn.jsdelivr.net</code>, richieste all’apertura di ogni pagina.</li>
</ul>
<div class="legal__note">I normali log del server non sono cookie e non leggono informazioni dal dispositivo; possono comunque contenere dati di navigazione e sono descritti nella <a href="privacy.html"><strong>privacy policy</strong></a>.</div>"""),
                ("servizi", "Collegamenti a servizi esterni", """
<p>I pulsanti verso Google Maps, Instagram e WhatsApp sono normali collegamenti. Prima del click non viene effettuata alcuna richiesta ai relativi domini: non ci sono mappe, pixel, iframe o script dei fornitori. Aprendo il collegamento si visita un servizio distinto, che può utilizzare cookie secondo la propria informativa.</p>
<p>Il menu digitale su <strong>digitavolo.com</strong> è un servizio esterno. Il sito non vi effettua alcuna richiesta finché l’utente non apre il collegamento e non conferma l’avviso di uscita. Da quel momento il fornitore può utilizzare tecnologie proprie secondo la sua informativa. Chi preferisce non aprirlo può consultare il menu nella pagina <a href="menu.html"><strong>Il Menu</strong></a> di questo sito.</p>"""),
                ("aggiornamenti", "Aggiornamenti della policy", """
<p>Se in futuro il sito adotterà nuovi servizi che utilizzano cookie o altre tecnologie facoltative, questa informativa verrà aggiornata prima della loro attivazione. Quando richiesto, tali servizi saranno disponibili solo dopo una scelta esplicita dell’utente.</p>"""),
                ("riferimenti", "Riferimenti ufficiali", """
<ul class="legal__refs">
  <li><a href="https://www.garanteprivacy.it/web/guest/home/docweb/-/docweb-display/docweb/9677876" target="_blank" rel="noopener">Garante — Linee guida cookie e altri strumenti di tracciamento, 10 giugno 2021</a></li>
  <li><a href="https://www.garanteprivacy.it/faq/cookie" target="_blank" rel="noopener">Garante — FAQ Cookie</a></li>
  <li><a href="https://eur-lex.europa.eu/eli/reg/2016/679/oj?locale=it" target="_blank" rel="noopener">EUR-Lex — Regolamento (UE) 2016/679</a></li>
</ul>"""),
            ],
        },
    },
    "en": {
        "privacy": {
            "titolo": "Privacy policy",
            "kicker": "Information notice under art. 13 GDPR",
            "intro": "This notice describes the processing connected with browsing the site, contact requests and table bookings.",
            "indice": [("titolare", "Controller"), ("dati-finalita", "Data and purposes"),
                       ("servizi-esterni", "External services"), ("destinatari", "Recipients"),
                       ("conservazione", "Retention"), ("diritti", "Rights")],
            "sezioni": [
                ("titolare", "Data controller", """
<p>The data controller is <strong>{nome}</strong>, VAT and tax code <strong>{piva}</strong>, registered office at {sede}. PLAGA operates from Piazza Umberto I, 73044 Galatone (LE), Italy.</p>
<div class="legal__note">For data protection requests: <a href="mailto:{email}"><strong>{email}</strong></a> or <a href="{wa}" target="_blank" rel="noopener"><strong>{tel}</strong></a>.</div>"""),
                ("dati-finalita", "Data processed, purposes and legal bases", """
<h3>Browsing data</h3>
<p>The systems that make the site available may record technical data such as IP address, date and time, page requested, response status, browser and operating system. This data is used to deliver and protect the site, diagnose faults and prevent abuse.</p>
<div class="legal__note"><strong>Legal basis:</strong> the controller’s legitimate interest in the security and correct operation of the service, art. 6(1)(f) GDPR.</div>
<h3>Data submitted voluntarily</h3>
<p>When a user writes on WhatsApp, calls or sends an e-mail, the data communicated is processed to reply, provide information and handle a table booking, within the resulting pre-contractual or contractual relationship. The site contains no contact forms: it collects no data of its own and sends none automatically.</p>
<div class="legal__note"><strong>Legal basis:</strong> pre-contractual measures or contract, art. 6(1)(b) GDPR; compliance with legal obligations, (c); legitimate interest in managing and protecting the relationship, (f), where applicable.</div>"""),
                ("servizi-esterni", "Contacts and external services", """
<h3>Services activated by the user</h3>
<p>Google Maps, Instagram and WhatsApp are not embedded in the page. The connection to the relevant provider occurs only after the user clicks, thereby visiting a separate service subject to its own notice. WhatsApp and e-mail messages are actually sent only through a further action in the application chosen by the user.</p>
<p>The digital menu is hosted by <strong>digitavolo.com</strong>, an external service not operated by PLAGA. Before opening it the site displays a notice stating the destination and requires explicit confirmation. From the moment it opens, the provider may receive technical connection data and operates under its own notice.</p>
<h3>Resources loaded automatically</h3>
<p>Unlike the links above, some technical resources needed to render the pages are requested from third parties <strong>the moment the site is opened</strong>, without any user action: typefaces from <code>fonts.googleapis.com</code> and <code>fonts.gstatic.com</code> (Google) and animation libraries from <code>cdnjs.cloudflare.com</code> (Cloudflare) and <code>cdn.jsdelivr.net</code>. These requests involve disclosing the IP address and technical connection data to those providers, which operate under their own notices. They set no cookies and are not used for statistics or profiling.</p>
<div class="legal__note"><strong>Legal basis:</strong> the controller’s legitimate interest in the typographic rendering and correct operation of the site, art. 6(1)(f) GDPR.</div>"""),
                ("destinatari", "Recipients and transfers", """
<p>Authorised staff, consultants and technical or hosting providers acting on the controller’s behalf may access the data within the limits of their respective functions. Data may also be disclosed where required by law or by a competent authority.</p>
<p>The site sends no data to analytics, advertising or social services. Transfers connected with the hosting provider, with the providers of the technical resources listed above or with external services chosen by the user must comply with arts. 44 ff. GDPR, on the basis of an adequacy decision or appropriate safeguards where necessary.</p>"""),
                ("conservazione", "Retention", """
<p>Technical data is kept for as long as strictly necessary to deliver, secure and diagnose the service, save for the need to establish abuse or for legal obligations.</p>
<p>Request data is kept for as long as necessary to reply and manage the relationship; data relating to bookings, contracts and administrative documents follows the periods laid down by law.</p>"""),
                ("diritti", "Rights of the data subject", """
<p>Where applicable, the data subject may request access, rectification, erasure, restriction, portability and object to processing under arts. 15–22 GDPR. Requests may be sent to the controller’s contacts given above.</p>
<div class="legal__note">It is also possible to lodge a complaint with the <a href="https://www.garanteprivacy.it/" target="_blank" rel="noopener"><strong>Italian Data Protection Authority</strong></a> or with the supervisory authority of the EEA State where you live or work, or where you believe the infringement occurred.</div>"""),
                (None, "Cookies and updates", """
<p>For details of the technologies used see the <a href="cookie.html"><strong>cookie policy</strong></a>. This notice may be updated when services, purposes or legal obligations change; the date at the top identifies the current version.</p>"""),
            ],
        },
        "cookie": {
            "titolo": "Cookie policy",
            "kicker": "Technologies present on the site",
            "intro": "As at the last check the site sets no cookies, uses no analytics, advertising or profiling tools and stores nothing in the browser. It does, however, request typefaces and libraries from third-party providers each time a page opens.",
            "indice": [("scelta-banner", "Why no banner"), ("inventario", "Inventory"),
                       ("servizi", "External services"), ("aggiornamenti", "Updates"),
                       ("riferimenti", "References")],
            "sezioni": [
                ("scelta-banner", "Why no banner appears", """
<div class="legal__note"><strong>Current configuration: no consent required.</strong></div>
<p>There are no cookies and no optional measurement or profiling tools. An “Accept/Reject” banner would therefore offer no real choice. Where only technical tools are used, the Italian Data Protection Authority allows the information to be given on the home page or in the general notice.</p>
<p>The requests to typeface and library providers described below are not cookies and neither read nor write information on the device. They do, however, disclose the IP address to third parties, which is why they are listed openly rather than passed over.</p>"""),
                ("inventario", "Technical inventory", """
<ul class="legal__inv">
  <li><strong>First-party cookies</strong>None set by the application.</li>
  <li><strong>Third-party cookies</strong>None.</li>
  <li><strong>LocalStorage and SessionStorage</strong>Not used. Language is not a stored preference: Italian and English are separate pages with their own addresses.</li>
  <li><strong>IndexedDB</strong>Not used.</li>
  <li><strong>Analytics, pixels and tag managers</strong>Not present.</li>
  <li><strong>Iframes</strong>None loaded when the page opens.</li>
  <li><strong>Images and video</strong>Served from the site’s own domain.</li>
  <li><strong>Typefaces</strong>Archivo, requested from <code>fonts.googleapis.com</code> and <code>fonts.gstatic.com</code> (Google) whenever a page opens.</li>
  <li><strong>Animation libraries</strong>GSAP from <code>cdnjs.cloudflare.com</code> (Cloudflare) and Lenis from <code>cdn.jsdelivr.net</code>, requested whenever a page opens.</li>
</ul>
<div class="legal__note">Ordinary server logs are not cookies and read no information from the device; they may nonetheless contain browsing data and are described in the <a href="privacy.html"><strong>privacy policy</strong></a>.</div>"""),
                ("servizi", "Links to external services", """
<p>The buttons to Google Maps, Instagram and WhatsApp are ordinary links. No request is made to those domains before the click: there are no maps, pixels, iframes or provider scripts. Opening the link takes you to a separate service, which may use cookies under its own notice.</p>
<p>The digital menu on <strong>digitavolo.com</strong> is an external service. The site makes no request to it until the user opens the link and confirms the exit notice. From that point the provider may use its own technologies under its own notice. Anyone who prefers not to open it can read the menu on the <a href="menu.html"><strong>The Menu</strong></a> page of this site.</p>"""),
                ("aggiornamenti", "Policy updates", """
<p>If the site adopts new services in future that use cookies or other optional technologies, this notice will be updated before they are activated. Where required, such services will be available only after an explicit choice by the user.</p>"""),
                ("riferimenti", "Official references", """
<ul class="legal__refs">
  <li><a href="https://www.garanteprivacy.it/web/guest/home/docweb/-/docweb-display/docweb/9677876" target="_blank" rel="noopener">Garante — Guidelines on cookies and other tracking tools, 10 June 2021</a></li>
  <li><a href="https://www.garanteprivacy.it/faq/cookie" target="_blank" rel="noopener">Garante — Cookie FAQ</a></li>
  <li><a href="https://eur-lex.europa.eu/eli/reg/2016/679/oj" target="_blank" rel="noopener">EUR-Lex — Regulation (EU) 2016/679</a></li>
</ul>"""),
            ],
        },
    },
}


def build_legal(lang, quale):
    """Compone una pagina legale dai testi in LEGAL."""
    d = LEGAL[lang][quale]
    campi = dict(TITOLARE, wa=wa_href(lang), tel=TEL)
    indice = "".join(f'<a href="#{a}">{etichetta}</a>'
                     for a, etichetta in d["indice"])
    sezioni = []
    for i, (ancora, titolo, corpo) in enumerate(d["sezioni"], start=1):
        attr = f' id="{ancora}"' if ancora else ""
        sezioni.append(
            f'<section class="legal__section"{attr}>'
            f'<span class="legal__num">{i:02d}</span>'
            f'<div class="legal__copy"><h2>{titolo}</h2>'
            f'{corpo.format(**campi)}</div></section>')
    return f"""<section class="pageHead">
  <p class="legal__kicker">{d["kicker"]}</p>
  <h1 class="pageTitle">{d["titolo"]}</h1>
  <p class="lead">{d["intro"]}</p>
  <p class="legal__updated">{T[lang]["legal_updated_label"]} {LEGAL_UPDATED[lang]}</p>
</section>

<nav class="legal__index" aria-label="{d["titolo"]}">{indice}</nav>

<div class="legal">{"".join(sezioni)}</div>

<section class="cta">
  <a class="btn" href="index.html"><span>{T[lang]["btn_back"]}</span></a>
</section>"""


def tagline_links(lang):
    """La tagline con le tre voci cliccabili.

    Ristorante e Pizzeria portano alla pagina Menu del sito; Lounge Bar va
    dritto al menu digitale su digitavolo. Le voci si ricavano dalla tagline
    gia' tradotta, cosi' il testo resta scritto una volta sola in T.

    `menu.html` senza prefisso vale in entrambe le lingue: ogni lingua ha la
    propria menu.html nella stessa cartella delle pagine che la linkano.
    """
    parts = [p.strip() for p in T[lang]["tagline"].split("<i>·</i>")]
    assert len(parts) == 3, f"tagline inattesa in {lang}: {T[lang]['tagline']}"
    ristorante, pizzeria, lounge = parts
    return (f'<a href="menu.html">{ristorante}</a> <i>·</i> '
            f'<a href="menu.html">{pizzeria}</a> <i>·</i> '
            f'<a href="{MENU_URL}" target="_blank" rel="noopener">{lounge}</a>')


def leave_dialog(lang):
    """Avviso prima di aprire digitavolo.

    Non dice all\u2019utente che il collegamento e\u2019 sicuro — non e\u2019 una cosa che
    il sito possa garantire per conto di terzi. Dice cosa e\u2019 digitavolo,
    che non e\u2019 gestito da PLAGA, e mostra l\u2019indirizzo per intero.
    """
    d = T[lang]["leave"]
    return f"""<dialog class="leave" id="leaveDialog" aria-labelledby="leaveTitle">
  <div class="leave__box">
    <p class="leave__kicker">{d["kicker"]}</p>
    <h2 class="leave__title" id="leaveTitle">{d["titolo"]}</h2>
    <p class="leave__text">{d["testo"]}</p>
    <p class="leave__dest"><span>{d["url_label"]}</span><code id="leaveUrl"></code></p>
    <div class="leave__actions">
      <button type="button" class="leave__btn leave__btn--ghost" id="leaveCancel">{d["annulla"]}</button>
      <button type="button" class="leave__btn" id="leaveGo">{d["continua"]}</button>
    </div>
  </div>
</dialog>"""


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
  <div class="hero__media">{picture(r, "sala-volte", t["alt"]["sala-volte"], lazy=False, mobile="sala-volte-mob")}</div>
  <div class="hero__scrim"></div>
  <div class="hero__content">
    <h1 class="hero__word">PLAGA</h1>
    <p class="hero__sub">{tagline_links(lang)}</p>
  </div>
</section>

<section class="intro">
  <p class="lead">{t["leads"]["index"]}</p>
</section>

<section class="cards" id="esplora">{html_cards}</section>"""


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
</section>

<section class="cta">
  <a class="btn" href="{_root(lang)}index.html#esplora"><span>{t["btn_back"]}</span></a>
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
</section>

<section class="cta">
  <a class="btn" href="{_root(lang)}index.html#esplora"><span>{t["btn_back"]}</span></a>
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
  <a class="btn" href="{_root(lang)}index.html#esplora"><span>{t["btn_back"]}</span></a>
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
    <a class="btn" href="{_root(lang)}index.html#esplora"><span>{t["btn_back"]}</span></a>
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

<section class="cta">
  <a class="btn" href="{_root(lang)}index.html#esplora"><span>{t["btn_back"]}</span></a>
</section>"""


BUILDERS = {"index": build_home, "sale": build_sale, "giardino": build_giardino,
            "forno": build_forno, "menu": build_menu, "contatti": build_contatti}

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for lang in T:
        for name in PAGES:
            page(lang, name, BUILDERS[name](lang),
                 light_nav=(name == "index"), loader=(name == "index"))
        for quale in LEGAL_PAGES:
            page(lang, quale, build_legal(lang, quale))
        print(f"{lang}: {len(PAGES) + len(LEGAL_PAGES)} pagine in "
              f"{T[lang]['dir'] or 'site'}/")
