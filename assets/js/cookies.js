/* Versal-Dent — Cookie notice
 * Yandex.Metrika is loaded directly in the <head> of every page.
 * This script only shows a one-time informational cookie notice.
 */
(function () {
  'use strict';

  var STORAGE_KEY = 'ad_cookies_consent';

  // ----- Notice state helpers -----
  function getConsent() {
    try { return localStorage.getItem(STORAGE_KEY); } catch (e) { return null; }
  }
  function setConsent(value) {
    try { localStorage.setItem(STORAGE_KEY, value); } catch (e) { /* noop */ }
  }

  // Compute relative path to root assets. Pages live either in root or one subfolder deep (/doctors/, /services/, /blog/).
  function linkPath(file) {
    var depth = (window.location.pathname.replace(/\/[^\/]*$/, '/').match(/\//g) || []).length - 1;
    var prefix = depth > 0 ? '../'.repeat(depth) : '';
    return prefix + file;
  }

  // ----- DOM: notice -----
  function buildBanner() {
    var wrap = document.createElement('div');
    wrap.className = 'cookie-banner';
    wrap.setAttribute('role', 'dialog');
    wrap.setAttribute('aria-label', 'Уведомление об использовании cookies');
    wrap.innerHTML = ''
      + '<div class="cookie-banner__inner">'
      +   '<div class="cookie-banner__text">'
      +     'Мы используем cookies и Яндекс.Метрику, чтобы сайт работал корректно и мы понимали, '
      +     'как им пользуются. Продолжая пользоваться сайтом, вы соглашаетесь с этим. '
      +     'Подробнее — в <a href="' + linkPath('cookies.html') + '">Cookie-политике</a> и '
      +     '<a href="' + linkPath('privacy.html') + '">Политике конфиденциальности</a>.'
      +   '</div>'
      +   '<div class="cookie-banner__actions">'
      +     '<button type="button" class="btn btn--primary" data-cookie-accept>Принять</button>'
      +   '</div>'
      + '</div>';
    return wrap;
  }

  function buildToggle() {
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'cookie-toggle';
    btn.setAttribute('aria-label', 'Уведомление об использовании cookies');
    btn.title = 'Уведомление об использовании cookies';
    btn.innerHTML = ''
      + '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
      +   '<path d="M21.6 12.4c-1.3.3-2.6-.5-2.9-1.8-.1-.5-.5-.8-1-.8-1.4 0-2.5-1.1-2.5-2.5 0-.5-.3-.9-.8-1-1.3-.3-2.1-1.6-1.8-2.9.1-.5-.2-1-.7-1.1A9.7 9.7 0 0 0 12 2a10 10 0 1 0 10 10c0-.4-.4-.7-.4-.6Z"/>'
      +   '<circle cx="8" cy="13" r="1"/><circle cx="13" cy="17" r="1"/><circle cx="16" cy="11" r="1"/>'
      + '</svg>'
      + '<span>Cookies</span>';
    return btn;
  }

  // ----- Show / hide -----
  var bannerEl = null;
  var toggleEl = null;

  function showBanner() {
    if (!bannerEl) {
      bannerEl = buildBanner();
      // В начало <body>: тогда работает CSS-правило
      // .cookie-banner.is-visible ~ .sticky-cta (скрыть нижнюю панель,
      // пока баннер открыт и перекрывает её).
      document.body.insertBefore(bannerEl, document.body.firstChild);
      bannerEl.querySelector('[data-cookie-accept]').addEventListener('click', function () {
        setConsent('accepted');
        hideBanner();
      });
    }
    requestAnimationFrame(function () { bannerEl.classList.add('is-visible'); });
  }

  function hideBanner() {
    if (bannerEl) bannerEl.classList.remove('is-visible');
  }

  function ensureToggle() {
    if (toggleEl) return;
    toggleEl = buildToggle();
    document.body.appendChild(toggleEl);
    toggleEl.addEventListener('click', showBanner);
  }

  // ----- Bootstrap -----
  function init() {
    if (getConsent() === null) {
      showBanner();
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
