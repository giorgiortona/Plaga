# PLAGA — sito

## Avviare in locale
```
python3 -m http.server 4321 --directory site
```
poi apri http://localhost:4321

## Struttura
```
build.py            genera tutte le pagine, in italiano e in inglese
site/
  index.html        \
  sale.html          |
  giardino.html      |  italiano (lingua principale, sta nella radice)
  forno.html         |
  menu.html          |
  contatti.html     /
  en/…              le stesse sei pagine in inglese
  css/style.css     palette, tipografia, layout
  js/main.js        scroll morbido, ingresso, burger menu, tab del menu
  assets/img/       foto webp, due misure: -lg (1800px) e -sm (900px)
```

**Gli .html sono generati.** Testi, menu, header, footer e switcher di lingua
stanno tutti in `build.py`. Per cambiare qualcosa modifica quello e rilancia:
```
python3 build.py
```

## Lingue
Italiano e inglese sono **pagine vere**, non uno scambio di testi via
JavaScript: hanno indirizzi propri (`/menu.html` e `/en/menu.html`), l'attributo
`lang` corretto e i tag `hreflang`, così Google le indicizza entrambe.

Lo switcher **IT / EN** è in alto a destra e resta sulla stessa pagina: se sei
sul menu in italiano e premi EN, arrivi al menu in inglese.

I testi stanno nel dizionario `T` di `build.py`, uno per lingua. Il menu sta in
`MENU`: ogni piatto ha nome e descrizione nelle due lingue. I nomi delle pizze
restano in italiano anche in inglese — sono nomi propri.

**Per aggiungere una terza lingua** (tedesco, francese) basta copiare un blocco
di `T`, tradurlo, aggiungere le traduzioni dei piatti in `MENU` e rilanciare.

## Logo

Tutto quello che riguarda il marchio sta in `logo/`:

```
logo/logo_plaga.svg        originale vettoriale — è la sorgente
logo/logo_plaga.png        originale raster 4096px, sfondo trasparente
logo/plaga-wordmark.svg    generato: il marchio PLAGA
logo/plaga-tagline.svg     generato: la scritta #DOWHATYOULOVE
```

`build.py` ricava i due file generati dall'originale vettoriale.

Li separa, li ritaglia stretti e sostituisce i colori fissi con
`currentColor`. Così nelle pagine il marchio **prende il colore dal CSS**:
verde `--brand` sulle pagine chiare, avorio sopra la foto dell'hero, avorio nel
footer. Un file solo, nessuna variante di colore da mantenere.

I due SVG si rigenerano da soli se mancano. Per rifarli dopo aver cambiato il
logo originale, cancella la cartella `logo/` e rilancia `python3 build.py`.

Il verde esatto del marchio è `#728163` ed è il token `--brand`.

Nel loader il payoff `#DOWHATYOULOVE` è invece composto in Archivo, non
vettorializzato: serve testo vero per animarne la spaziatura.

## Intro

A ogni caricamento della home:

1. il marchio si disegna con **una penna sola**, da sinistra a destra;
2. il colore lo attraversa con un fronte sfumato, mentre il contorno si ritira;
3. `#DOWHATYOULOVE` appare stringendo la spaziatura;
4. tutto sale e scopre la pagina.

Dura circa 3,7 secondi. Per cambiarne il ritmo c'è `INTRO_VELOCITA` in cima a
`site/js/main.js`: 1 è il valore progettato, 1.3 la porta a ~2,9s, 1.6 a ~2,3s.
Si riscala tutto insieme, mantenendo le proporzioni.

Chi ha attivato «riduci animazioni» nelle impostazioni di sistema salta
direttamente alla pagina, senza intro.

### Come è fatta

Due accorgimenti, entrambi per la fluidità.

**Il tratto.** Il tratteggio SVG riparte a ogni sottotracciato, quindi le otto
parti del marchio vanno animate separatamente. Animandole come otto tween
distinti però ognuna aveva il suo ease: il tratto ripartiva e frenava a ogni
lettera. Ora la corsa è **una sola** — la somma delle lunghezze — e ogni parte
scopre la propria porzione quando il fronte la attraversa. La velocità resta
costante per tutta la parola.

**Il colore.** Non è una dissolvenza: sono due maschere complementari che
scorrono sullo stesso fronte sfumato. Dove il colore è già passato il contorno
sparisce, davanti resta solo il contorno. Il pieno non «appare», subentra.

## Cache

`build.py` mette in coda a css e js un'impronta del contenuto
(`style.css?v=86d600d1`). Quando il file cambia, cambia l'indirizzo: nessun
browser può continuare a servire la copia vecchia, né durante il lavoro né dopo
una pubblicazione.

Serve però che le impronte siano aggiornate: **dopo ogni modifica a
`style.css` o `main.js`, rilancia `python3 build.py`**. Non rigenera solo le
pagine, ricalcola anche le impronte.

## Font
**Archivo variabile** da Google Fonts — assi larghezza 62–125% e peso 100–900.
È il sostituto libero di Right Grotesk (il font di Puok Burger, a pagamento).
Titoli: `font-variation-settings:'wdth' 125` + `font-weight:800` maiuscolo.

## Palette
Pelle/sabbia calda dominante, verde scuro come **unico** accento.

| token | valore | uso |
|---|---|---|
| `--skin-050` | `#E8DBC7` | fondo pagina |
| `--skin-100` | `#DFCFB6` | overlay del menu, slot foto |
| `--ink` | `#1F1810` | testo e footer |
| `--green-500` | `#274F3A` | accento: foglia, numeri, lingua attiva, hover |
| `--green-900` | `#0E2018` | intro |
| `--sage` | `#6E8A76` | accento chiaro sui fondi scuri |

## Telefono
Lo stesso sito si adatta, con qualche accortezza in più:
- rientri di sicurezza per notch e barra home (`env(safe-area-inset-*)`);
- ogni cosa da toccare è alta almeno 44px;
- le tab del menu scorrono di lato, con una sfumatura a destra che lo segnala;
- nelle righe dei contatti l'etichetta va sopra e il valore sotto;
- gli effetti al passaggio del mouse sono spenti (su touch restano attaccati).

## Animazioni
Volutamente poche: scroll morbido, una sola animazione d'ingresso (il blocco
sale di 18px in 0,7s), il burger menu a tendina, e l'intro col logo, che parte
a ogni caricamento della home.

Per cambiarne il ritmo c'è `INTRO_VELOCITA` in cima a `site/js/main.js`:
1 è il valore progettato (~3,4s), 1.3 la porta a ~2,6s, 1.6 a ~2,1s.

Chi ha attivato «riduci animazioni» nelle impostazioni di sistema salta
direttamente alla pagina, senza intro.

## Aggiungere le foto di pizze e piatti
1. Converti in webp dentro `site/assets/img/`:
   ```
   cwebp -q 80 -resize 1800 0 pizza.jpg -o site/assets/img/pizza-01-lg.webp
   cwebp -q 78 -resize 900  0 pizza.jpg -o site/assets/img/pizza-01-sm.webp
   ```
2. In `build.py` aggiungi nome file e testo alternativo nel dizionario `alt`
   di **entrambe** le lingue.
3. Sempre in `build.py`, nella funzione `build_forno`, sostituisci gli slot
   grigi con `_fig(lang, "g--third", "pizza-01", "Nome della pizza")`.
4. Rilancia `python3 build.py`.

## Da completare
Gli **orari di apertura** non sono pubblicati da nessuna parte: quando me li dai
li aggiungo al footer e alla pagina Contatti, in entrambe le lingue.
