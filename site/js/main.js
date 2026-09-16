/* ═══════════════════════════════════════════════════════════════
   PLAGA — motion
   Poco e coerente: scroll morbido, una sola animazione d'ingresso,
   il burger menu. Niente parallax, niente maschere, niente cursore.
   ═══════════════════════════════════════════════════════════════ */

gsap.registerPlugin(ScrollTrigger);

const EASE = 'power3.inOut';
const EASE_OUT = 'power3.out';
const REDUCED = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

/* Ritmo dell'intro. 1 = come progettata (~3,7s in tutto).
   Alza per accorciarla — 1.3 la porta a ~2,9s, 1.6 a ~2,3s. */
const INTRO_VELOCITA = 1;

let lenis = null;

/* ─────────────────────────── SCROLL MORBIDO ─────────────────────────── */

function initLenis() {
  if (REDUCED) return;
  lenis = new Lenis({ duration: 1.05, smoothWheel: true });
  lenis.on('scroll', ScrollTrigger.update);
  gsap.ticker.add((t) => lenis.raf(t * 1000));
  gsap.ticker.lagSmoothing(0);
}

/* ─────────────────────────── INGRESSO ───────────────────────────
   Una sola regola per tutto il sito: il blocco sale di poco e appare.
   Gli elementi vicini partono a scalare, così la pagina non "sfarfalla".
------------------------------------------------------------------ */

const REVEAL = [
  '.pageTitle', '.lead', '.card', '.g',
  '.slot', '.contact__row', '.cta', '.menuTabs',
  '.occhiello', '.trio__voce', '.cifra__k', '.quad__nome',
  '.dire__sotto', '.chiusa__piccola', '.eventi__k', '.eventi__testo'
].join(',');

/* le foto grandi non sfumano: si scoprono. Vedi velaFoto() */
const VELATE = '.bleed .pic, .quad .pic';

/* ───────── LE PAROLE CHE SALGONO ─────────
   Le dichiarazioni non compaiono: salgono da sotto, una parola dopo
   l'altra. Spezzo per parola e non per riga perché le parole si
   riadattano da sole quando cambia la larghezza — le righe andrebbero
   rimisurate a ogni resize, e a ogni rimisura l'animazione ripartirebbe.
--------------------------------------------------------------------- */

function saliParole() {
  const blocchi = gsap.utils.toArray('[data-sale]');
  if (!blocchi.length) return;

  blocchi.forEach((el) => {
    if (el.dataset.spezzato) return;
    el.dataset.spezzato = '1';
    const parole = el.textContent.trim().split(/\s+/);
    el.textContent = '';
    parole.forEach((parola, i) => {
      const guscio = document.createElement('span');
      guscio.className = 'parola';
      const dentro = document.createElement('i');
      dentro.textContent = parola;
      guscio.appendChild(dentro);
      el.appendChild(guscio);
      // lo spazio resta testo vero: così la riga va a capo dove deve
      if (i < parole.length - 1) el.appendChild(document.createTextNode(' '));
    });
  });

  const pezzi = (el) => el.querySelectorAll('.parola > i');

  if (REDUCED) return;

  blocchi.forEach((el) => {
    const righe = pezzi(el);
    gsap.set(righe, { yPercent: 115 });
    ScrollTrigger.create({
      trigger: el,
      start: 'top 88%',
      once: true,
      onEnter: () => gsap.to(righe, {
        yPercent: 0, duration: 0.9, ease: EASE_OUT, stagger: 0.035
      })
    });
  });
}

/* ───────── LA FRASE CHE SI SCRIVE ─────────
   Il manifesto non compare tutto insieme: si scrive mentre lo scorrimento
   lo attraversa, una lettera dopo l'altra. Niente resta nascosto dietro un
   gesto che quasi nessuno farebbe — basta passarci davanti.

   Le lettere ci sono già tutte e tengono il loro posto: cambia solo la
   trasparenza. Se sparissero davvero, la frase si riformerebbe a ogni
   carattere e le righe ballerebbero.

   Accendo con una classe invece di interpolare l'opacità: a ogni scatto
   dello scorrimento tocco solo le lettere fra il vecchio confine e il
   nuovo, non tutte e duecento.
--------------------------------------------------------------------- */

function scriviFrase() {
  const blocchi = gsap.utils.toArray('[data-scrive]');
  if (!blocchi.length) return;

  blocchi.forEach((el) => {
    if (el.dataset.scritto) return;
    el.dataset.scritto = '1';

    const testo = el.textContent.trim();
    el.textContent = '';
    const lettere = [];
    for (const segno of testo) {
      // gli spazi restano testo vero: sono lì che le righe vanno a capo
      if (segno === ' ') { el.appendChild(document.createTextNode(' ')); continue; }
      const s = document.createElement('span');
      s.className = 'scritta__l';
      s.textContent = segno;
      el.appendChild(s);
      lettere.push(s);
    }

    if (REDUCED) {
      lettere.forEach((s) => s.classList.add('is-on'));
      return;
    }

    let confine = 0;
    ScrollTrigger.create({
      trigger: el,
      start: 'top 85%',
      end: 'bottom 45%',
      scrub: true,
      onUpdate: (self) => {
        const quante = Math.round(self.progress * lettere.length);
        if (quante === confine) return;
        const avanti = quante > confine;
        const da = Math.min(confine, quante), a = Math.max(confine, quante);
        for (let i = da; i < a; i++) lettere[i].classList.toggle('is-on', avanti);
        confine = quante;
      }
    });
  });
}

/* ───────── IL TIMBRO ─────────
   Lo stemma della Dispensa non compare: si stampa. Arriva più grande e
   storto, poi scende in piano con un piccolo rimbalzo, come un timbro
   premuto sulla carta.

   La rotazione e la scala stanno solo qui, non nel CSS: così se il
   JavaScript non parte lo stemma resta dritto e al suo posto invece di
   restare storto per sempre.
--------------------------------------------------------------------- */

function timbro() {
  if (REDUCED) return;
  const bolli = gsap.utils.toArray('.card__stemma');
  if (!bolli.length) return;

  bolli.forEach((b) => {
    gsap.set(b, { opacity: 0, scale: 1.45, rotate: -9 });
    ScrollTrigger.create({
      trigger: b.closest('.card') || b,
      start: 'top 82%',
      once: true,
      onEnter: () => gsap.timeline()
        .to(b, { opacity: 1, duration: 0.3, ease: 'none' }, 0)
        .to(b, { scale: 1, rotate: 0, duration: 0.85, ease: 'back.out(1.7)' }, 0)
    });
  });
}

/* ───────── LA BOTTEGA ─────────
   Un negozio solo davanti. L'ordine vive nel browser di chi guarda, e il
   tasto finale apre WhatsApp con la lista già scritta: non c'è una cassa,
   quindi non c'è niente che finga di incassare.

   I prezzi stanno nel DOM (data-prezzo) e non in una copia qui: il
   generatore li scrive una volta sola, da DISPENSA, e qui si leggono.
--------------------------------------------------------------------- */

const CHIAVE_ORDINE = 'plaga-ordine';

function euro(n) {
  return n.toFixed(2).replace('.', ',') + ' \u20ac';
}

function bottega() {
  const scaffale = document.querySelector('[data-bottega]');
  const pannello = document.getElementById('ordine');
  if (!scaffale || !pannello) return;

  const schede = [...scaffale.querySelectorAll('.art')];
  const righe = pannello.querySelector('[data-righe]');
  const vuoto = pannello.querySelector('[data-vuoto]');
  const invia = pannello.querySelector('[data-invia]');

  const catalogo = new Map(schede.map((a) => [a.dataset.slug, {
    nome: a.dataset.nome,
    prezzo: parseFloat(a.dataset.prezzo.replace(',', '.')),
    scheda: a
  }]));

  // Il carrello sopravvive al cambio pagina, ma è solo di chi guarda: sta
  // nel suo browser e non arriva a nessun altro finché non preme il tasto.
  let ordine = {};
  try {
    const salvato = JSON.parse(localStorage.getItem(CHIAVE_ORDINE) || '{}');
    for (const [slug, q] of Object.entries(salvato)) {
      if (catalogo.has(slug) && Number.isInteger(q) && q > 0) ordine[slug] = q;
    }
  } catch (e) { ordine = {}; }

  const salva = () => {
    try { localStorage.setItem(CHIAVE_ORDINE, JSON.stringify(ordine)); } catch (e) {}
  };

  const pezzi = () => Object.values(ordine).reduce((a, b) => a + b, 0);
  const somma = () => Object.entries(ordine)
    .reduce((t, [slug, q]) => t + catalogo.get(slug).prezzo * q, 0);

  function passo(slug, delta) {
    const q = (ordine[slug] || 0) + delta;
    if (q > 0) ordine[slug] = Math.min(q, 99);
    else delete ordine[slug];
    salva();
    // se aggiungi mentre la scheda è ritirata, torna in campo: il senso
    // di averla a lato è proprio vedere l'ordine crescere
    if (delta > 0) pannello.classList.remove('is-chiusa');
    disegna();
  }

  function disegna() {
    // le schede: tasto oppure selettore di quantità
    schede.forEach((a) => {
      const q = ordine[a.dataset.slug] || 0;
      a.querySelector('[data-agg]').hidden = q > 0;
      const sel = a.querySelector('.passo');
      sel.hidden = q === 0;
      sel.querySelector('[data-qta]').textContent = String(q);
    });

    const n = pezzi();
    pannello.hidden = n === 0;
    if (n === 0) pannello.classList.remove('is-chiusa');

    const testo = n === 1 ? pannello.dataset.uno : pannello.dataset.molti.replace('{n}', n);
    const tot = euro(somma());
    pannello.querySelectorAll('[data-conto],[data-conto-p]').forEach((e) => { e.textContent = testo; });
    pannello.querySelector('[data-tot-p]').textContent = tot;
    pannello.querySelector('[data-tot-foglio]').textContent = tot;

    // il riepilogo
    righe.textContent = '';
    for (const [slug, q] of Object.entries(ordine)) {
      const v = catalogo.get(slug);
      const li = document.createElement('li');
      li.className = 'riga';
      li.innerHTML =
        '<span class="riga__nome"></span>' +
        '<div class="passo">' +
        '<button type="button" class="passo__b" data-meno>\u2212</button>' +
        '<span class="passo__n"></span>' +
        '<button type="button" class="passo__b" data-piu>+</button>' +
        '</div><span class="riga__prezzo"></span>';
      li.querySelector('.riga__nome').textContent = v.nome;
      li.querySelector('.passo__n').textContent = String(q);
      li.querySelector('.riga__prezzo').textContent = euro(v.prezzo * q);
      li.querySelector('[data-meno]').addEventListener('click', () => passo(slug, -1));
      li.querySelector('[data-piu]').addEventListener('click', () => passo(slug, 1));
      righe.appendChild(li);
    }
    vuoto.hidden = n > 0;

    // Lenis intercetta la rotellina su tutta la pagina: questo attributo gli
    // dice di lasciar stare qui dentro. Lo metto solo quando la lista ha
    // davvero qualcosa da scorrere, altrimenti sopra al riepilogo corto la
    // rotellina non muoverebbe più niente.
    righe.toggleAttribute('data-lenis-prevent',
      righe.scrollHeight > righe.clientHeight + 1);

    invia.href = collegamento();
  }

  function collegamento() {
    const parti = [scaffale.dataset.intro, ''];
    for (const [slug, q] of Object.entries(ordine)) {
      const v = catalogo.get(slug);
      parti.push(`${q} \u00d7 ${v.nome} \u2014 ${euro(v.prezzo * q)}`);
    }
    parti.push('', `${scaffale.dataset.tot}: ${euro(somma())}`);
    return 'https://wa.me/' + scaffale.dataset.wa
         + '?text=' + encodeURIComponent(parti.join('\n'));
  }

  schede.forEach((a) => {
    const slug = a.dataset.slug;
    a.querySelector('[data-agg]').addEventListener('click', () => passo(slug, 1));
    a.querySelector('[data-meno]').addEventListener('click', () => passo(slug, -1));
    a.querySelector('[data-piu]').addEventListener('click', () => passo(slug, 1));
  });

  pannello.querySelector('[data-apri]').addEventListener('click', () => {
    pannello.classList.remove('is-chiusa');
  });
  pannello.querySelector('[data-chiudi]').addEventListener('click', () => {
    pannello.classList.add('is-chiusa');
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') pannello.classList.add('is-chiusa');
  });

  disegna();
}

/* ───────── LA VETRINA DELLA DISPENSA ─────────
   La foto resta ferma e cambia insieme alla scheda che le scorre accanto,
   e con lei cambia la tinta di tutta la sezione.

   Il bersaglio è il centro dello schermo: il prodotto attivo è quello la
   cui scheda ci sta sopra. Con onEnter/onEnterBack invece servirebbero due
   soglie diverse per i due versi, e scorrendo all'indietro il cambio
   arriverebbe sfasato.
------------------------------------------------------------------- */

function vetrinaDispensa() {
  const scena = document.querySelector('.disp');
  if (!scena) return;

  const schede = gsap.utils.toArray('.prod', scena);
  const foto = gsap.utils.toArray('.disp__img', scena);
  if (!schede.length || !foto.length) return;

  let attivo = -1;
  const mostra = (i) => {
    if (i === attivo || !foto[i]) return;
    attivo = i;
    foto.forEach((f, k) => f.classList.toggle('is-on', k === i));
    scena.style.setProperty('--tinta', schede[i].dataset.tinta);
  };

  mostra(0);

  schede.forEach((scheda, i) => {
    ScrollTrigger.create({
      trigger: scheda,
      start: 'top center',
      end: 'bottom center',
      onToggle: (self) => { if (self.isActive) mostra(i); }
    });
  });
}

/* ───────── LE FOTO CHE SI SCOPRONO ─────────
   Un velo che si alza dal basso, e dentro l'immagine che rientra dalla
   sua scala: due tempi sovrapposti, così non è uno stacco secco.
   Alla fine tolgo la trasformazione, altrimenti lo stile in linea
   lasciato da GSAP batte lo zoom al passaggio del mouse.
------------------------------------------------------------------- */

function velaFoto() {
  if (REDUCED) return;
  const foto = gsap.utils.toArray(VELATE);
  if (!foto.length) return;

  foto.forEach((velo) => {
    const img = velo.querySelector('img');
    if (!img) return;

    gsap.set(velo, { clipPath: 'inset(0% 0% 100% 0%)' });
    gsap.set(img, { scale: 1.14 });

    ScrollTrigger.create({
      trigger: velo,
      start: 'top 88%',
      once: true,
      onEnter: () => gsap.timeline()
        .to(velo, { clipPath: 'inset(0% 0% 0% 0%)', duration: 1.1, ease: EASE })
        .to(img, {
          scale: 1, duration: 1.5, ease: EASE_OUT,
          onComplete: () => gsap.set(img, { clearProps: 'transform' })
        }, 0)
    });
  });
}

function reveals() {
  const els = gsap.utils.toArray(REVEAL);
  if (!els.length) return;

  els.forEach((el) => el.setAttribute('data-up', ''));

  if (REDUCED) {
    gsap.set(els, { opacity: 1, y: 0 });
    return;
  }

  gsap.set(els, { opacity: 0, y: 18 });

  ScrollTrigger.batch(els, {
    start: 'top 92%',
    once: true,
    onEnter: (batch) => gsap.to(batch, {
      opacity: 1,
      y: 0,
      duration: 0.7,
      stagger: 0.07,
      ease: EASE_OUT,
      overwrite: true
    })
  });
}

/* ───────── LE VOCI DEL MENU, GRANDI QUANTO LO SPAZIO CONSENTE ─────────
   "Il Giardino" e "The Garden" hanno larghezze diverse, e un corpo fisso o
   va a capo o esce dal riquadro. Qui si misura la voce più lunga e si
   riduce quel tanto che basta: mai oltre il valore del CSS.

   Vale a ogni larghezza. Prima no — da desktop l'elenco era unico e
   larghissimo, e ci stava comunque. Adesso le colonne sono tre: lo spazio
   per voce è un terzo, e la misura va fatta anche lì. Il fattore è uno
   solo per tutte, altrimenti le colonne avrebbero corpi diversi e l'indice
   si sfalderebbe.
---------------------------------------------------------------------- */

function adattaVociMenu() {
  const voci = document.querySelectorAll('.menuNav__item a');
  if (!voci.length) return;

  const etichette = [...voci].map((a) => a.querySelector('.menuNav__label'));
  etichette.forEach((et) => et && et.style.removeProperty('font-size'));

  let fattore = 1;
  voci.forEach((a) => {
    const et = a.querySelector('.menuNav__label');
    const num = a.querySelector('.menuNav__num');
    if (!et) return;
    const gap = parseFloat(getComputedStyle(a).columnGap) || 0;
    const spazio = a.clientWidth - (num ? num.offsetWidth : 0) - gap;
    const larga = larghezzaTesto(et).width;
    if (larga > 0 && spazio > 0) fattore = Math.min(fattore, spazio / larga);
  });
  if (fattore >= 1) return;

  etichette.forEach((et) => {
    if (!et) return;
    const corpo = parseFloat(getComputedStyle(et).fontSize);
    et.style.fontSize = (corpo * fattore).toFixed(2) + 'px';
  });
}

/* ───────── IL MARCHIO GRANDE, LARGO QUANTO LA RIGA SOTTO ─────────
   La riga cambia testo tra italiano e inglese, si blocca oltre i 1410px e usa
   una spaziatura diversa sui telefoni: nessun valore fisso combacia in tutti i
   casi. Quindi si misura il testo davvero disegnato.

   Serve un Range: i due elementi sono blocchi, e getBoundingClientRect()
   restituirebbe la larghezza della colonna, non quella delle lettere.
------------------------------------------------------------------------ */

function larghezzaTesto(el) {
  const r = document.createRange();
  r.selectNodeContents(el);
  return r.getBoundingClientRect();
}

function allineaMarchioHero() {
  const parola = document.querySelector('.hero__word');
  const riga = document.querySelector('.hero__sub');
  if (!parola || !riga) return;

  const rigaRect = larghezzaTesto(riga);
  const interlinea = parseFloat(getComputedStyle(riga).lineHeight) || 0;

  const corpo = parseFloat(getComputedStyle(parola).fontSize);
  const larga = larghezzaTesto(parola).width;
  if (!corpo || !larga) return;

  // Sui telefoni la riga va a capo: la sua larghezza non è più un riferimento.
  // Lì il marchio si allinea alla colonna, così il bordo destro resta a filo.
  let obiettivo = rigaRect.width;
  if (interlinea && rigaRect.height > interlinea * 1.5) {
    const col = parola.parentElement;
    const cs = getComputedStyle(col);
    obiettivo = col.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
  }

  // il rapporto larghezza/corpo è costante, quindi il calcolo si autocorregge
  parola.style.fontSize = (obiettivo / (larga / corpo)).toFixed(2) + 'px';
}

/* ─────────────────────── DISEGNO DEL MARCHIO ───────────────────────
   Un tracciato solo contiene tutte le lettere (e i loro occhielli) come
   sottotracciati. Il tratteggio SVG però riparte a ogni sottotracciato:
   animarli insieme li completerebbe tutti nel primo istante. Quindi li
   separo in tracciati distinti, ordinati da sinistra a destra, e li faccio
   partire uno dopo l'altro — come una mano che scrive.
------------------------------------------------------------------------ */

function separaLettere(percorso) {
  const d = percorso.getAttribute('d') || '';
  const pezzi = d.match(/[Mm][^Mm]*/g);
  if (!pezzi || pezzi.length < 2) return [percorso];

  const padre = percorso.parentNode;
  const nuovi = pezzi.map((sub) => {
    const p = percorso.cloneNode(false);
    p.setAttribute('d', sub);
    padre.insertBefore(p, percorso);
    return p;
  });
  padre.removeChild(percorso);

  // da sinistra a destra
  nuovi.sort((a, b) => a.getBBox().x - b.getBBox().x);
  return nuovi;
}

/* ─────────────────────────── PRELOADER ───────────────────────────
   Solo in home e solo alla prima visita della sessione.
------------------------------------------------------------------ */

function runLoader(done) {
  const loader = document.getElementById('loader');
  if (!loader) return done();

  // L'intro parte a ogni caricamento della home. Unica eccezione: chi ha
  // chiesto al sistema operativo di ridurre le animazioni.
  if (REDUCED) {
    loader.remove();
    return done();
  }

  document.body.classList.add('is-locked');
  const line = loader.querySelector('.loaderLogo__line');
  const fill = loader.querySelector('.loaderLogo__fill');
  const testo = loader.querySelector('.loaderLogo--text');
  const tag = loader.querySelector('.loader__tag');

  const tl = gsap.timeline({
    onComplete: () => {
      loader.remove();
      document.body.classList.remove('is-locked');
      ScrollTrigger.refresh();
    }
  });
  tl.timeScale(INTRO_VELOCITA);

  if (line && fill) {
    // ── il tratto ──────────────────────────────────────────────────────
    // Una penna sola. La corsa è la somma dei sottotracciati e ogni lettera
    // scopre la propria porzione quando il fronte la attraversa: la velocità
    // resta costante per tutta la parola. Otto tween separati, ognuno col suo
    // ease, facevano ripartire e frenare il tratto a ogni lettera.
    const tratti = separaLettere(line).map((el) => ({ el, len: el.getTotalLength() }));
    let somma = 0;
    tratti.forEach((t) => { t.da = somma; somma += t.len; });
    tratti.forEach((t) => gsap.set(t.el, { strokeDasharray: t.len, strokeDashoffset: t.len }));

    const penna = { avanzamento: 0 };
    tl.to(penna, {
      avanzamento: 1,
      duration: 1.6,
      ease: 'sine.inOut',
      onUpdate: () => {
        const corsa = penna.avanzamento * somma;
        for (const t of tratti) {
          const fatto = Math.min(Math.max(corsa - t.da, 0), t.len);
          t.el.style.strokeDashoffset = String(t.len - fatto);
        }
      }
    }, 0);

    // ── il colore ──────────────────────────────────────────────────────
    // Due maschere complementari sullo stesso fronte sfumato: il pieno entra
    // mentre il contorno si ritira, alla stessa ascissa. Niente dissolvenza.
    const fronte = loader.querySelector('#plagaFronte');
    const fronteInv = loader.querySelector('#plagaFronteInv');
    const svg = loader.querySelector('.loaderLogo');
    if (fronte && fronteInv && svg) {
      const [vx, , vw] = svg.getAttribute('viewBox').split(/\s+/).map(Number);
      const banda = vw * 0.24;
      const colore = { x: vx - banda };
      tl.to(colore, {
        x: vx + vw,
        duration: 1.25,
        ease: 'sine.inOut',
        onUpdate: () => {
          for (const g of [fronte, fronteInv]) {
            g.setAttribute('x1', colore.x);
            g.setAttribute('x2', colore.x + banda);
          }
        }
      }, 0.8);
    }
  } else if (testo) {
    // ripiego finché il logo non è vettorializzato
    gsap.set(testo, { opacity: 0, y: 26 });
    tl.to(testo, { opacity: 1, y: 0, duration: 0.9, ease: EASE_OUT });
  }

  if (tag) {
    gsap.set(tag, { opacity: 0, letterSpacing: '1.05em' });
    tl.to(tag, {
      opacity: 1, letterSpacing: '0.3em',
      duration: 1.05, ease: 'power2.out'
    }, 1.45);
  }

  tl.to(loader.querySelector('.loader__inner'), { opacity: 0, duration: 0.4, ease: EASE }, '+=0.15')
    .to(loader, { yPercent: -100, duration: 0.9, ease: 'power4.inOut' }, '-=0.2')
    .add(done, '-=0.6');
}

/* ─────────────────────────── BURGER + OVERLAY ─────────────────────────── */

function burgerMenu() {
  const burger = document.getElementById('burger');
  const overlay = document.getElementById('menuOverlay');
  const nav = document.getElementById('nav');
  if (!burger || !overlay) return;

  const panels = overlay.querySelectorAll('.menuOverlay__bg i');
  const trama = overlay.querySelector('.menuOverlay__trama');
  const inner = overlay.querySelector('.menuOverlay__inner');
  const top = overlay.querySelector('.menuTop');
  const teste = overlay.querySelectorAll('.menuGroup__k');
  const items = overlay.querySelectorAll('.menuNav__item a');
  const foots = overlay.querySelectorAll('.menuFoot__col');

  let open = false;
  let anim = null;

  // Gli stati di partenza, tutti insieme: l'overlay resta montato tra
  // un'apertura e l'altra, quindi vanno rimessi anche alla chiusura.
  // Sono gli stessi valori, e stanno scritti una volta sola.
  function azzera() {
    // vedi sopra: neutralizzo la y che GSAP ricava dal transform del CSS
    gsap.set(items, { y: 0, yPercent: 105 });
    gsap.set(foots, { opacity: 0, y: 14 });
    gsap.set(top, { opacity: 0, y: -12 });
    gsap.set(teste, { opacity: 0, y: 10 });
    gsap.set(trama, { opacity: 0 });
  }
  azzera();

  function openMenu() {
    if (open) return;
    open = true;
    // All'avvio il font non è ancora quello definitivo e le voci risultano
    // più strette di quanto saranno: la misura buona è questa. Un frame
    // dopo, però — a pannello aperto, quando il testo è davvero disegnato.
    requestAnimationFrame(adattaVociMenu);
    document.body.classList.add('is-menu-open');
    overlay.classList.add('is-open');
    overlay.setAttribute('aria-hidden', 'false');
    burger.setAttribute('aria-expanded', 'true');
    burger.setAttribute('aria-label', burger.dataset.close || 'Chiudi il menu');
    nav.classList.remove('is-hidden');
    if (lenis) lenis.stop();

    // L'ordine è quello della lettura: prima il fondo, poi il marchio che
    // raccoglie il testimone da quello della barra, poi gli occhielli dei
    // gruppi e le voci sotto, infine i contatti.
    anim && anim.kill();
    anim = gsap.timeline();
    anim.set(inner, { opacity: 1 })
      .to(panels, { scaleY: 1, duration: 0.8, stagger: 0.06, ease: 'power4.inOut', transformOrigin: 'top' }, 0)
      .to(trama, { opacity: 1, duration: 1, ease: EASE_OUT }, 0.3)
      .to(top, { opacity: 1, y: 0, duration: 0.6, ease: EASE_OUT }, 0.34)
      .to(teste, { opacity: 1, y: 0, duration: 0.5, stagger: 0.07, ease: EASE_OUT }, 0.44)
      .fromTo(items, { y: 0, yPercent: 105 }, { yPercent: 0, duration: 0.9, stagger: 0.05, ease: EASE_OUT }, 0.5)
      .to(foots, { opacity: 1, y: 0, duration: 0.5, stagger: 0.05, ease: EASE_OUT }, 0.74);
  }

  function closeMenu() {
    if (!open) return;
    open = false;
    document.body.classList.remove('is-menu-open');
    burger.setAttribute('aria-expanded', 'false');
    burger.setAttribute('aria-label', burger.dataset.open || 'Apri il menu');
    if (lenis) lenis.start();

    anim && anim.kill();
    anim = gsap.timeline({
      onComplete: () => {
        overlay.classList.remove('is-open');
        overlay.setAttribute('aria-hidden', 'true');
        gsap.set(inner, { opacity: 0 });
        azzera();
      }
    });
    anim.to(items, { yPercent: -105, duration: 0.5, stagger: 0.035, ease: EASE }, 0)
      .to([top, ...teste, ...foots], { opacity: 0, duration: 0.25, ease: EASE }, 0)
      .to(trama, { opacity: 0, duration: 0.4, ease: EASE }, 0)
      .to(panels, { scaleY: 0, duration: 0.7, stagger: 0.05, ease: 'power4.inOut', transformOrigin: 'bottom' }, 0.18);
  }

  burger.addEventListener('click', () => (open ? closeMenu() : openMenu()));
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && open) closeMenu(); });
}

/* ─────────────────────────── NAV ───────────────────────────
   Chiara sopra la foto dell'hero (solo in home), scura appena la supera.
   E si ritrae scendendo, torna salendo.
------------------------------------------------------------ */

function navBehaviour() {
  const nav = document.getElementById('nav');
  const hero = document.querySelector('.hero');

  if (hero) {
    ScrollTrigger.create({
      trigger: hero,
      start: 'top 60px',
      end: 'bottom 60px',
      onToggle: (self) => nav.classList.toggle('is-light', self.isActive)
    });
  }

  let last = 0;
  ScrollTrigger.create({
    start: 0,
    end: 'max',
    onUpdate: (self) => {
      if (document.body.classList.contains('is-menu-open')) return;
      const y = self.scroll();
      nav.classList.toggle('is-hidden', y > 240 && y > last);
      last = y;
    }
  });
}

/* ─────────────────────────── MENU: TABS ─────────────────────────── */

function menuTabs() {
  const tabs = Array.from(document.querySelectorAll('.menuTab'));
  const panels = Array.from(document.querySelectorAll('.menuPanel'));
  const ink = document.querySelector('[data-tab-ink]');
  if (!tabs.length || !ink) return;

  function moveInk(tab) {
    const bar = tab.parentElement.getBoundingClientRect();
    const r = tab.getBoundingClientRect();
    ink.style.width = r.width + 'px';
    ink.style.transform = 'translateX(' + (r.left - bar.left) + 'px)';
  }

  function activate(tab) {
    tabs.forEach((t) => {
      const on = t === tab;
      t.classList.toggle('is-active', on);
      t.setAttribute('aria-selected', on ? 'true' : 'false');
    });
    panels.forEach((p) => {
      const on = p.dataset.panel === tab.dataset.tab;
      p.hidden = !on;
      p.classList.toggle('is-active', on);
      if (on && !REDUCED) {
        gsap.fromTo(p.querySelectorAll('.dish'),
          { opacity: 0, y: 14 },
          { opacity: 1, y: 0, duration: 0.5, stagger: 0.035, ease: EASE_OUT, overwrite: true });
      }
    });
    moveInk(tab);
    ScrollTrigger.refresh();
  }

  tabs.forEach((t) => t.addEventListener('click', () => activate(t)));

  const first = tabs.find((t) => t.classList.contains('is-active')) || tabs[0];
  requestAnimationFrame(() => moveInk(first));
  window.addEventListener('resize', () => {
    const active = tabs.find((t) => t.classList.contains('is-active'));
    if (active) moveInk(active);
  });
}

/* ─────────────────────────── BOOT ─────────────────────────── */

function start() {
  saliParole();
  scriviFrase();
  vetrinaDispensa();
  timbro();
  bottega();
  velaFoto();
  reveals();
  navBehaviour();
  menuTabs();
  ScrollTrigger.refresh();
}

document.addEventListener('DOMContentLoaded', () => {
  // Per prima, e prima di tutto cio' che dipende da GSAP o Lenis: se una
  // libreria dal CDN non arriva, l'avviso di uscita deve restare in piedi.
  // Altrimenti i link a digitavolo si aprirebbero senza conferma.
  leaveNotice();
  initLenis();
  burgerMenu();

  // subito, non alla fine dell'intro: il titolo deve avere la misura giusta
  // anche su chi salta l'intro (riduci animazioni) o ricarica a metà
  allineaMarchioHero();
  adattaVociMenu();
  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(() => {                // le metriche vere arrivano col font
      allineaMarchioHero();
      adattaVociMenu();
    });
  }

  runLoader(start);
});

let rt;
window.addEventListener('resize', () => {
  allineaMarchioHero();
  adattaVociMenu();
  clearTimeout(rt);
  rt = setTimeout(() => ScrollTrigger.refresh(), 200);
});


/* ------------------------------------------------------------------
   Avviso prima di uscire verso digitavolo.
   Un solo listener sul documento: vale anche per i link nel footer e
   nel burger menu, che esistono su ogni pagina.
------------------------------------------------------------------ */

function leaveNotice() {
  const dlg = document.getElementById('leaveDialog');
  if (!dlg || typeof dlg.showModal !== 'function') return;

  const out = dlg.querySelector('#leaveUrl');
  const go = dlg.querySelector('#leaveGo');
  const cancel = dlg.querySelector('#leaveCancel');
  let atteso = null;

  document.addEventListener('click', (e) => {
    const a = e.target.closest('a[href^="https://www.digitavolo.com"]');
    if (!a) return;
    e.preventDefault();
    atteso = a.href;
    out.textContent = a.href;
    dlg.showModal();
    if (lenis) lenis.stop();
  });

  // window.open sta nel gestore del click, non nell'evento close:
  // serve il gesto dell'utente, altrimenti il browser blocca la scheda.
  go.addEventListener('click', () => {
    if (atteso) window.open(atteso, '_blank', 'noopener');
    dlg.close();
  });

  cancel.addEventListener('click', () => dlg.close());
  dlg.addEventListener('close', () => {
    atteso = null;
    if (lenis) lenis.start();
  });
}
