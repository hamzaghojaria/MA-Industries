/* Progressive motion: content stays visible if animation support is absent. */
(() => {
  'use strict';
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const running = new Set();
  let observer;

  function enter(element, delay = 0, distance = 10) {
    if (reducedMotion.matches || !element?.animate) return;
    const animation = element.animate([
      { opacity: 0, transform: `translateY(${distance}px)` },
      { opacity: 1, transform: 'translateY(0)' }
    ], { duration: 320, delay, easing: 'cubic-bezier(.2,.7,.2,1)', fill: 'backwards' });
    running.add(animation);
    animation.finished.catch(() => {}).finally(() => running.delete(animation));
  }

  function enterDialog(dialog) {
    enter(dialog, 0, 12);
  }
  function confirmEnquiry(status) {
    status.classList.add('enquiry-ready');
    enter(status, 0, 6);
  }
  window.MAExperience = Object.freeze({ enterDialog, confirmEnquiry });

  const progress = document.createElement('div');
  progress.className = 'reading-progress';
  progress.setAttribute('aria-hidden', 'true');
  document.body.append(progress);
  let framePending = false;
  function updateProgress() {
    framePending = false;
    const available = document.documentElement.scrollHeight - window.innerHeight;
    const value = available > 0 ? Math.max(0, Math.min(1, window.scrollY / available)) : 0;
    progress.style.transform = `scaleX(${value})`;
  }
  function scheduleProgress() {
    if (framePending) return;
    framePending = true;
    window.requestAnimationFrame(updateProgress);
  }
  window.addEventListener('scroll', scheduleProgress, { passive: true });
  window.addEventListener('resize', scheduleProgress);
  if ('ResizeObserver' in window) new ResizeObserver(scheduleProgress).observe(document.body);
  updateProgress();

  // A media preference change cancels active motion immediately.
  reducedMotion.addEventListener('change', () => {
    if (!reducedMotion.matches) return;
    observer?.disconnect();
    for (const animation of running) animation.cancel();
  });
  if (reducedMotion.matches || !('IntersectionObserver' in window)) return;

  observer = new IntersectionObserver(entries => {
    let stagger = 0;
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      observer.unobserve(entry.target);
      // A small stagger groups related content without delaying entry.
      if (!entry.target.contains?.(document.activeElement)) enter(entry.target, Math.min(stagger++ * 40, 100));
    }
  }, { threshold: .15 });
  document.querySelectorAll('.founder-card,.steps article,.about-value-grid article,.enquiry>div,.brand-card')
    .forEach(element => observer.observe(element));

  document.addEventListener('toggle', event => {
    if (event.target.tagName === 'DETAILS' && event.target.open) enter(event.target.querySelector('p'), 0, 6);
  }, true);
  const dialog = document.querySelector('dialog[open]');
  if (dialog) enterDialog(dialog);
})();
