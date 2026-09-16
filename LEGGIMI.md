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

## Le pagine

`PAGES` in `build.py` decide l'ordine, e lo stesso ordine vale per le voci
del burger menu (`nav`): i due elenchi vanno tenuti allineati, indice per
indice. Dal settembre 2026 sono otto — con l'aggiunta di **La Cucina** e
**La Dispensa** — e il numero conta: `overlay()` lo scrive nel CSS come
`--voci`, e le voci del menu si dimensionano dividendo l'altezza per quel
numero. Aggiungerne altre le rimpicciolisce da sola; toglierne le rialza.

I testi del locale stanno nel dizionario `T`, uno per lingua: `manifesto`,
`chiusa_grande`, `chiusa_piccola`, `eventi`, `cucina`, `pizzeria`,
`dispensa`. Sono le parole del ristorante, non riscritte: se cambiano, si
cambia lì e si rilancia `build.py`.

## La vetrina della Dispensa

I sette prodotti stanno in `DISPENSA`, in cima a `build.py`: nome, formato e
descrizione vengono dalle **etichette vere** fotografate, non sono testi
scritti per il sito. Ogni prodotto porta la sua `tinta` — il rosso del
pomodoro, il verde dell'oliva — e la sezione ci si accorda intorno mentre
scorri: `vetrinaDispensa()` in `main.js` scambia la foto e riscrive `--tinta`
sulla sezione, tutto il resto lo fanno le transizioni CSS.

Il bersaglio è il centro dello schermo, non un bordo: con onEnter/onEnterBack
servirebbero due soglie diverse per i due versi, e tornando indietro il
cambio arriverebbe sfasato.

Da telefono la foto ferma sparisce e ogni scheda si porta dietro la sua
immagine. Le due copie non convivono mai — quella spenta è `display:none`,
quindi esce anche dalla lettura assistita.

## Lo stemma della Dispensa

`site/assets/img/stemma-dispensa.webp` è il marchio stampato sulle etichette,
**ritagliato dalla foto dello scaffale**: lì era sovrapposto come grafica
piatta, quindi i bordi sono netti. Il ritaglio è stato fatto riempiendo lo
sfondo dai bordi dell'immagine e fermandosi al bordo dello stemma, che è
verde (G ≥ R) mentre il mobile e la pelle sono bruni (R > G di parecchio) —
la luminanza da sola non sarebbe bastata, il bordo scuro si sarebbe confuso
col legno.

**È un ritaglio da una foto a 520px**, non l'originale. Va bene alla misura in
cui lo usiamo, ma se serve più grande — o in stampa — bisogna farsi dare il
file vero dal grafico delle etichette.

Sulla home fa da titolo della scheda al posto della parola, e `timbro()` in
`main.js` lo fa scendere in piano da più grande e storto, come un timbro
premuto. Rotazione e scala di partenza stanno solo nel JavaScript: se non
parte, lo stemma resta dritto invece di restare storto per sempre.

## La Bottega

`bottega.html` è un negozio solo davanti: si riempie l'ordine e il tasto apre
WhatsApp con la lista già scritta. **Non c'è cassa e non si paga lì**, ed è
voluto — un carrello che finge di incassare metterebbe i clienti davanti a
una promessa che il sito non può mantenere.

Articoli e **prezzi** vengono da `DISPENSA` in `build.py`, un posto solo da
aggiornare. Attenzione: dallo scaffale fotografato si leggevano solo 7,50 e
11,00; gli altri cinque prezzi sono messi a occhio e **vanno confermati dal
locale prima di pubblicare**.

L'ordine vive nel browser di chi guarda (`localStorage`, chiave
`plaga-ordine`) e non arriva a nessuno finché non preme il tasto. `bottega()`
in `main.js` legge i prezzi dal DOM invece di tenerne una copia: il
generatore li scrive una volta, il codice li rilegge.

Il riepilogo è una **scheda in basso a destra**, aperta per default: si vede
crescere mentre scegli, senza doverla aprire. Chiusa si ritira in una
pastiglia allo stesso angolo. In basso e non centrata perché centrata
coprirebbe il titolo a chi torna con l'ordine già pieno. Sotto gli 860px non
c'è larghezza per una colonna a lato: lì la stessa scheda arriva dal basso.

La pagina **non sta nel burger menu** — le voci sono già otto e questa è una
figlia della Dispensa, non una sezione a sé. Ci si arriva dal tasto pieno in
fondo a `dispensa.html`.

## La trama di fondo

Dietro a tutto c'è il marchio ripetuto, verde, quasi invisibile. La
piastrella la genera `trama()` in `build.py` dal tracciato vero del logo e
finisce in `site/assets/img/trama-plaga.svg`: due righe sfalsate di mezza
parola, con quella di sotto disegnata a sinistra e a destra perché le metà
combacino quando la piastrella si affianca a se stessa.

La rotazione la mette il CSS sull'intero strato (`body::before`), non sulla
piastrella: ruotata, la piastrella non si incastrerebbe più ai bordi. Lo
strato sta fisso e sborda del 30% per lato, così i tagli restano fuori campo.

Quanto si vede è una riga sola: `opacity` in `body::before`. Ora è `.045`.

## Le animazioni delle sezioni nuove

Due, in `main.js`, oltre al `reveals()` che c'era:

- `saliParole()` spezza i blocchi con `data-sale` parola per parola e le fa
  salire da sotto. Spezza per parola e non per riga perché le parole si
  riadattano da sole quando cambia la larghezza.
- `velaFoto()` scopre le foto grandi (`.bleed`, `.quad`) con un velo che si
  alza, mentre l'immagine rientra dalla sua scala.
- `scriviFrase()` scrive il manifesto della home una lettera alla volta,
  mentre lo scorrimento attraversa la frase. Le lettere ci sono già tutte e
  tengono il loro posto — cambia solo la trasparenza — altrimenti la frase si
  riformerebbe a ogni carattere e le righe ballerebbero. La trasparenza sta
  sulle singole lettere, non sul paragrafo: quegli involucri li crea la
  funzione stessa, quindi senza JavaScript il testo si vede tutto.

Entrambe si spengono con `prefers-reduced-motion`, e se il JavaScript non
parte il testo resta leggibile: l'involucro delle parole lo crea `saliParole()`
stessa, non il generatore.

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

Non è il sito desktop ristretto: la composizione cambia.

**Le gallerie** non sono una colonna di foto uguali. Seguono un ritmo di
cinque: una a tutta pagina fuori dai margini, due affiancate con la seconda
sfalsata verso il basso, una rientrata a destra, una rientrata a sinistra.

**Le schede della home** si alternano: una alta a tutta pagina, una quadrata
rientrata. Sulla stretta il titolo si accorcia per restare su una riga.

**L'hero** usa una foto ritagliata apposta (`sala-volte-mob.webp`): un
paesaggio 3:2 dentro uno schermo verticale perderebbe i lati e mostrerebbe una
fascia centrale senza senso. La riga sotto il marchio resta obbligatoriamente
su una riga sola, altrimenti il blocco si sfalda.

**Le voci del burger** riempiono la colonna come da desktop. Il corpo non è
fisso: `adattaVociMenu()` misura la voce più lunga — «Il Giardino» in italiano,
«The Garden» in inglese — e riduce quel tanto che basta perché stia su una
riga. Sui telefoni bassi le voci si accorciano ancora, così lista e contatti
ci stanno insieme; in ultima istanza il pannello scorre.

Altre accortezze: rientri di sicurezza per notch e barra home, bersagli da
almeno 44px, tab del menu che scorrono di lato con una sfumatura a segnalarlo,
effetti al passaggio del mouse disattivati.

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
