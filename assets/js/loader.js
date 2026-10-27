/* A short, non-blocking welcome while page assets finish loading. */
(() => {
  'use strict';
  if (document.readyState === 'complete') return;
  const loader = document.createElement('div');
  loader.className = 'page-loader';
  loader.hidden = true;
  loader.setAttribute('role', 'status');
  loader.setAttribute('aria-label', 'Loading M&A Industries');
  const mark = document.createElement('div');
  mark.className = 'page-loader__mark';
  mark.setAttribute('aria-hidden', 'true');
  const logo = document.createElement('img');
  logo.src = new URL('../images/brand-logo.png', document.currentScript.src).href;
  logo.width = 1270;
  logo.height = 230;
  logo.alt = '';
  const caption = document.createElement('span');
  caption.className = 'page-loader__caption';
  caption.textContent = 'Thoughtful materials. Everyday possibilities.';
  caption.setAttribute('aria-hidden', 'true');
  loader.append(mark, logo, caption);
  document.body.append(loader);
  let finished = false;
  const reveal = window.setTimeout(() => { if (!finished) loader.hidden = false; }, 120);
  const safety = window.setTimeout(dismiss, 2500);
  function dismiss() {
    if (finished) return;
    finished = true;
    window.clearTimeout(reveal);
    window.clearTimeout(safety);
    loader.classList.add('page-loader--finished');
    loader.setAttribute('aria-hidden', 'true');
    window.setTimeout(() => loader.remove(), 360);
  }
  window.addEventListener('load', dismiss, { once: true });
  window.addEventListener('pagehide', dismiss, { once: true });
  window.addEventListener('pageshow', event => { if (event.persisted) dismiss(); });
})();
