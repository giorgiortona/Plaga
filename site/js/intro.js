/* Decide prima del primo disegno: nessun lampo dell'intro nei passaggi interni. */
(() => {
  const url = new URL(location.href);
  const navigation = performance.getEntriesByType('navigation')[0];
  const fromLogo = url.searchParams.get('intro') === 'logo';
  let internal = false;
  try { internal = new URL(document.referrer).origin === url.origin; } catch (_) {}
  const show = !matchMedia('(prefers-reduced-motion: reduce)').matches
    && (navigation?.type === 'reload'
      || (navigation?.type !== 'back_forward' && (fromLogo || !internal)));
  document.documentElement.classList.toggle('has-intro', show);
  if (fromLogo) {
    url.searchParams.delete('intro');
    history.replaceState(history.state, '', url.pathname + url.search + url.hash);
  }
})();
