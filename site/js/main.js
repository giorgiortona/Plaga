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
  '.pageTitle', '.lead', '.card', '.g', '.bleed img',
  '.slot', '.contact__row', '.cta', '.menuTabs'
].join(',');

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
  const inner = overlay.querySelector('.menuOverlay__inner');
  const items = overlay.querySelectorAll('.menuNav__item a');
  const foots = overlay.querySelectorAll('.menuFoot__col');

  let open = false;
  let anim = null;

  // vedi sopra: neutralizzo la y che GSAP ricava dal transform del CSS
  gsap.set(items, { y: 0, yPercent: 105 });
  gsap.set(foots, { opacity: 0, y: 14 });

  function openMenu() {
    if (open) return;
    open = true;
    document.body.classList.add('is-menu-open');
    overlay.classList.add('is-open');
    overlay.setAttribute('aria-hidden', 'false');
    burger.setAttribute('aria-expanded', 'true');
    burger.setAttribute('aria-label', burger.dataset.close || 'Chiudi il menu');
    nav.classList.remove('is-hidden');
    if (lenis) lenis.stop();

    anim && anim.kill();
    anim = gsap.timeline();
    anim.set(inner, { opacity: 1 })
      .to(panels, { scaleY: 1, duration: 0.8, stagger: 0.06, ease: 'power4.inOut', transformOrigin: 'top' }, 0)
      .fromTo(items, { y: 0, yPercent: 105 }, { yPercent: 0, duration: 0.9, stagger: 0.06, ease: EASE_OUT }, 0.38)
      .to(foots, { opacity: 1, y: 0, duration: 0.5, stagger: 0.05, ease: EASE_OUT }, 0.68);
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
        gsap.set(items, { y: 0, yPercent: 105 });
        gsap.set(foots, { opacity: 0, y: 14 });
      }
    });
    anim.to(items, { yPercent: -105, duration: 0.5, stagger: 0.035, ease: EASE }, 0)
      .to(foots, { opacity: 0, duration: 0.25, ease: EASE }, 0)
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
  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(allineaMarchioHero);   // le metriche vere arrivano col font
  }

  runLoader(start);
});

let rt;
window.addEventListener('resize', () => {
  allineaMarchioHero();
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
