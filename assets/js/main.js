(function () {
  'use strict';

  // ---------------------------------------------------------------------------
  // Яндекс.Метрика — цели для интеграции с Яндекс.Директом.
  //
  // Счётчик 00000000 инициализируется в <head> каждой HTML-страницы
  // (см. блок «Yandex.Metrika counter»). Здесь — только программная
  // отправка целей через ym(...,'reachGoal',...).
  //
  // Список целей (ИДЕНТИФИКАТОРЫ в кабинете Метрики → Цели → JavaScript-событие):
  //
  //   lead_submit     — МАКРО. Успешная отправка любой формы заявки
  //                     (главная цель, по ней оптимизируем кампании Директа).
  //   call_click      — МАКРО. Клик по любому номеру телефона (a[href^="tel:"]).
  //                     Считаем звонком — на мобильных это и есть звонок,
  //                     на десктопе показатель намерения позвонить.
  //   whatsapp_click  — МАКРО. Клик по ссылке WhatsApp (wa.me/...).
  //   telegram_click  — МАКРО. Клик по ссылке Telegram (t.me/versaldent).
  //   modal_open      — МИКРО. Открытие модалки «Записаться» ([data-modal-open]).
  //                     Считаем «дошёл до формы»; для разогрева look-alike.
  //   form_start      — МИКРО. Пользователь начал заполнять форму
  //                     (первый фокус в любом поле формы [data-form]).
  //                     Срабатывает один раз на форму на загрузку страницы.
  //
  // ВАЖНО: те же имена нужно завести в кабинете Метрики как JavaScript-цели
  // (Настройка счётчика → Цели → Добавить цель → JavaScript-событие →
  // в поле «Идентификатор цели» — точно такая же строка, например call_click).
  // Без этого они не будут учитываться Директом для оптимизации.
  // ---------------------------------------------------------------------------
  var YM_COUNTER_ID = 0; // TODO: вставить реальный id Яндекс.Метрики
  function trackGoal(name, params) {
    if (typeof window.ym !== 'function') return;
    try {
      if (params) {
        window.ym(YM_COUNTER_ID, 'reachGoal', name, params);
      } else {
        window.ym(YM_COUNTER_ID, 'reachGoal', name);
      }
    } catch (e) { /* счётчик ещё не загрузился / заблокирован — игнорим */ }
  }

  // UTM-метки и идентификаторы кликов: запоминаем при первом заходе на сайт
  // (sessionStorage), потом подкидываем в каждую заявку, чтобы менеджер видел,
  // из какой рекламной кампании пришёл лид. yclid — клик-ID Яндекс.Директа
  // (нужен для офлайн-конверсий в Метрике), gclid — Google Ads.
  var TRACKED_PARAMS = [
    'utm_source', 'utm_medium', 'utm_campaign',
    'utm_term', 'utm_content',
    'yclid', 'gclid', 'ym_uid'
  ];
  function captureTrackingParams() {
    if (!window.sessionStorage) return;
    var url;
    try { url = new URL(window.location.href); } catch (e) { return; }
    TRACKED_PARAMS.forEach(function (key) {
      var value = url.searchParams.get(key);
      if (value && !sessionStorage.getItem('ad_' + key)) {
        try { sessionStorage.setItem('ad_' + key, value); } catch (e) {}
      }
    });
  }
  function getTrackingParams() {
    var out = {};
    if (!window.sessionStorage) return out;
    TRACKED_PARAMS.forEach(function (key) {
      var value;
      try { value = sessionStorage.getItem('ad_' + key); } catch (e) { value = null; }
      if (value) out[key] = value;
    });
    return out;
  }
  captureTrackingParams();

  // Скрипт подключают в разных местах: на одних страницах FAB-разметка
  // стоит выше <script src="main.js">, на других — ниже. Чтобы не зависеть
  // от порядка тегов, ждём готовности DOM перед инициализацией.
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  function init() {

  // Mobile nav toggle
  var burger = document.querySelector('[data-burger]');
  var nav = document.querySelector('[data-nav]');
  if (burger && nav) {
    burger.addEventListener('click', function () {
      nav.classList.toggle('is-open');
    });
  }

  // Phone input mask: +7 (XXX) XXX-XX-XX
  function maskPhone(input) {
    input.addEventListener('input', function (e) {
      var digits = e.target.value.replace(/\D/g, '');
      if (digits.startsWith('8')) digits = '7' + digits.slice(1);
      if (!digits.startsWith('7')) digits = '7' + digits;
      digits = digits.slice(0, 11);
      var out = '+7';
      if (digits.length > 1) out += ' (' + digits.slice(1, 4);
      if (digits.length >= 5) out += ') ' + digits.slice(4, 7);
      if (digits.length >= 8) out += '-' + digits.slice(7, 9);
      if (digits.length >= 10) out += '-' + digits.slice(9, 11);
      e.target.value = out;
    });
    input.addEventListener('focus', function (e) {
      if (!e.target.value) e.target.value = '+7 (';
    });
  }
  document.querySelectorAll('input[type="tel"]').forEach(maskPhone);

  // Lead submission — POST в собственный PHP-эндпоинт на хостинге,
  // оттуда уже идёт серверный fetch в Telegram Bot API.
  // Токен бота лежит только на сервере (api/config.php, в .gitignore).
  function sendLead(form) {
    var fd = new FormData(form);
    fd.append('_page', location.origin + (location.pathname || '/'));
    fd.append('_referrer', document.referrer || '');
    // Прикладываем UTM/yclid из sessionStorage — менеджер увидит источник
    // лида, а в Метрике можно загрузить офлайн-конверсии по yclid.
    var tracking = getTrackingParams();
    Object.keys(tracking).forEach(function (key) {
      fd.append('_' + key, tracking[key]);
    });
    return fetch('/api/lead.php', { method: 'POST', body: fd })
      .then(function (r) {
        return r.json().then(function (d) {
          return d && d.ok ? d : Promise.reject(d);
        });
      });
  }

  document.querySelectorAll('form[data-form]').forEach(function (form) {
    // Микроцель form_start — фиксируем один раз на форму, когда пользователь
    // впервые ставит фокус в любое поле. По этой метрике видно, сколько
    // людей дошли до формы, но не отправили (потенциал для ретаргета).
    var formStarted = false;
    form.addEventListener('focusin', function (e) {
      if (formStarted) return;
      if (!e.target.matches('input, textarea, select')) return;
      formStarted = true;
      trackGoal('form_start', { form: form.getAttribute('data-form') || 'default' });
    });

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var success = form.querySelector('[data-form-success]');
      var submitBtn = form.querySelector('button[type="submit"]');
      var origLabel = submitBtn ? submitBtn.textContent : 'Отправить';

      var done = function (ok, label) {
        if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = origLabel; }
        if (success) {
          success.textContent = label;
          success.classList.add('is-active');
          // Note: notification stays visible until modal close / page reload,
          // so a distracted user always sees it when they come back.
        }
        if (ok) {
          form.reset();
          trackGoal('lead_submit', { form: form.getAttribute('data-form') || 'default' });
        }
      };

      if (submitBtn) { submitBtn.disabled = true; submitBtn.textContent = 'Отправляем…'; }

      sendLead(form).then(
        function () { done(true,  'Спасибо! Мы перезвоним за 15 минут.'); },
        function (err) {
          console.warn('[lead] failed', err);
          done(false, 'Не удалось отправить. Позвоните, пожалуйста: +7 (000) 000-00-00');
        }
      );
    });
  });

  // Цели на клики по контактам. Делегирование на document — ссылки
  // разбросаны по шапке, футеру, FAB-виджету, секциям контактов, и
  // навешивать на каждую вручную нерационально. Достаточно одного слушателя.
  document.addEventListener('click', function (e) {
    var link = e.target.closest && e.target.closest('a[href]');
    if (!link) return;
    var href = link.getAttribute('href') || '';
    if (href.indexOf('tel:') === 0) {
      trackGoal('call_click', { source: linkSource(link) });
    } else if (/^https?:\/\/(?:api\.)?wa\.me\//i.test(href) || /wa\.me\/70000000000/i.test(href)) {
      trackGoal('whatsapp_click', { source: linkSource(link) });
    } else if (/^https?:\/\/t\.me\//i.test(href)) {
      trackGoal('telegram_click', { source: linkSource(link) });
    }
  });

  // Откуда был клик — для отчёта по «Параметрам визита» в Метрике.
  // Помогает понять, какой блок страницы работает лучше: FAB, шапка, футер.
  function linkSource(link) {
    if (link.closest('[data-fab]')) return 'fab';
    if (link.closest('header, .site-header, .topbar')) return 'header';
    if (link.closest('footer, .site-footer')) return 'footer';
    if (link.closest('[data-modal]')) return 'modal';
    return 'content';
  }

  // Modal (callback request)
  var modal = document.querySelector('[data-modal]');
  function closeModal() {
    if (!modal) return;
    modal.classList.remove('is-open');
    // Clear any leftover success notification so next open starts fresh.
    modal.querySelectorAll('[data-form-success].is-active').forEach(function (el) {
      el.classList.remove('is-active');
    });
  }
  // Делегирование на document, а не привязка к каждой кнопке при загрузке:
  // ловит и статические [data-modal-open], и те, что добавляются в DOM
  // позже из JS (например, CTA «Записаться на консультацию» в лайтбоксе
  // портфолио — portfolio.js). Иначе у динамической кнопки не было бы
  // обработчика, и ссылка href="#" просто прокручивала бы страницу вверх
  // вместо открытия формы.
  document.addEventListener('click', function (e) {
    var btn = e.target.closest && e.target.closest('[data-modal-open]');
    if (!btn) return;
    e.preventDefault();
    if (modal) modal.classList.add('is-open');
    // Микроцель: показывает воронку «дошёл до формы записи».
    // Считаем намерение записаться — даже если форму не отправят.
    trackGoal('modal_open', { source: linkSource(btn) });
  });
  if (modal) {
    modal.addEventListener('click', function (e) {
      if (e.target === modal || e.target.matches('[data-modal-close]') || e.target.closest('[data-modal-close]')) {
        closeModal();
      }
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closeModal();
    });
  }

  // Highlight active nav link (compare resolved pathnames so relative hrefs work)
  var path = location.pathname.replace(/\/+$/, '') || '/';
  document.querySelectorAll('[data-nav] a').forEach(function (a) {
    try {
      var linkPath = new URL(a.href).pathname.replace(/\/+$/, '') || '/';
      if (linkPath === path) a.classList.add('is-active');
    } catch (e) {}
  });

  // Smooth-scroll for in-page anchors only
  document.querySelectorAll('a[href^="#"]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      var id = a.getAttribute('href').slice(1);
      if (!id) return;
      var el = document.getElementById(id);
      if (!el) return;
      e.preventDefault();
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      if (nav && nav.classList.contains('is-open')) nav.classList.remove('is-open');
    });
  });

  // Русские сообщения нативной валидации форм (вместо англ. по локали браузера)
  (function () {
    function ruMessage(el) {
      var v = el.validity;
      if (v.valueMissing) {
        if (el.type === 'checkbox') return 'Пожалуйста, поставьте эту галочку, чтобы продолжить.';
        if (el.type === 'tel') return 'Пожалуйста, укажите номер телефона.';
        return 'Пожалуйста, заполните это поле.';
      }
      if (v.typeMismatch || v.patternMismatch) {
        if (el.type === 'tel') return 'Введите телефон в формате +7 (XXX) XXX-XX-XX.';
        if (el.type === 'email') return 'Введите корректный адрес электронной почты.';
        return 'Проверьте правильность ввода.';
      }
      return 'Пожалуйста, заполните это поле правильно.';
    }
    // invalid не всплывает — слушаем в фазе перехвата
    document.addEventListener('invalid', function (e) {
      var el = e.target;
      if (el && typeof el.setCustomValidity === 'function') el.setCustomValidity(ruMessage(el));
    }, true);
    function clear(e) {
      var el = e.target;
      if (el && typeof el.setCustomValidity === 'function') el.setCustomValidity('');
    }
    document.addEventListener('input', clear, true);
    document.addEventListener('change', clear, true);
  })();

  // Doctors carousel (главная) — горизонтальный скролл строки врачей
  document.querySelectorAll('[data-doctors-carousel]').forEach(function (root) {
    var track = root.querySelector('[data-dc-track]');
    var prev = root.querySelector('[data-dc-prev]');
    var next = root.querySelector('[data-dc-next]');
    if (!track) return;
    function stepBy() {
      var card = track.querySelector('.doctor-card');
      var w = card ? card.getBoundingClientRect().width + 22 : 240;
      return w * 2;
    }
    function update() {
      var max = track.scrollWidth - track.clientWidth - 2;
      if (prev) prev.disabled = track.scrollLeft <= 2;
      if (next) next.disabled = track.scrollLeft >= max;
    }
    if (prev) prev.addEventListener('click', function () { track.scrollBy({ left: -stepBy(), behavior: 'smooth' }); });
    if (next) next.addEventListener('click', function () { track.scrollBy({ left: stepBy(), behavior: 'smooth' }); });
    track.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update);
    update();
  });

  // Hero promotions carousel
  document.querySelectorAll('[data-carousel]').forEach(function (root) {
    var slides = Array.prototype.slice.call(root.querySelectorAll('.hero__slide'));
    var dots = Array.prototype.slice.call(root.querySelectorAll('[data-carousel-dot]'));
    var prevBtn = root.querySelector('[data-carousel-prev]');
    var nextBtn = root.querySelector('[data-carousel-next]');
    var track = root.querySelector('[data-carousel-slides]');
    if (slides.length < 2) return;

    var idx = 0;
    var INTERVAL = 7000;
    var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var timer = null;
    var paused = false;

    function show(i) {
      idx = (i + slides.length) % slides.length;
      slides.forEach(function (s, k) {
        var active = k === idx;
        s.classList.toggle('is-active', active);
        s.setAttribute('aria-hidden', active ? 'false' : 'true');
      });
      dots.forEach(function (d, k) {
        var active = k === idx;
        d.classList.toggle('is-active', active);
        d.setAttribute('aria-selected', active ? 'true' : 'false');
      });
    }
    function next() { show(idx + 1); }
    function prev() { show(idx - 1); }
    function start() {
      if (reduceMotion || paused) return;
      stop();
      timer = setInterval(next, INTERVAL);
    }
    function stop() { if (timer) { clearInterval(timer); timer = null; } }
    function restart() { stop(); start(); }

    dots.forEach(function (d, k) {
      d.addEventListener('click', function () { show(k); restart(); });
    });
    if (nextBtn) nextBtn.addEventListener('click', function () { next(); restart(); });
    if (prevBtn) prevBtn.addEventListener('click', function () { prev(); restart(); });

    root.addEventListener('mouseenter', function () { paused = true; stop(); });
    root.addEventListener('mouseleave', function () { paused = false; start(); });
    root.addEventListener('focusin', function () { paused = true; stop(); });
    root.addEventListener('focusout', function () { paused = false; start(); });

    document.addEventListener('visibilitychange', function () {
      if (document.hidden) stop(); else if (!paused) start();
    });

    root.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowLeft') { e.preventDefault(); prev(); restart(); }
      if (e.key === 'ArrowRight') { e.preventDefault(); next(); restart(); }
    });

    var touchX = null;
    if (track) {
      track.addEventListener('touchstart', function (e) {
        touchX = e.touches[0].clientX;
        paused = true; stop();
      }, { passive: true });
      track.addEventListener('touchend', function (e) {
        if (touchX === null) return;
        var dx = e.changedTouches[0].clientX - touchX;
        if (Math.abs(dx) > 40) { (dx < 0 ? next : prev)(); }
        touchX = null;
        paused = false; start();
      });
    }

    start();
  });

  // Scroll reveal animations (no library, no jank)
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if ('IntersectionObserver' in window && !reduceMotion) {
    var revealTargets = document.querySelectorAll(
      '.section h2, .section__lead, .service-card, .doctor-card, .review-quote, .rating-card, .usp, .faq__item, .pf-card, .related__card, .prices-table'
    );
    revealTargets.forEach(function (el) { el.classList.add('js-reveal'); });

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -10% 0px', threshold: 0.08 });

    revealTargets.forEach(function (el) { io.observe(el); });
  }

  // Reading progress bar (top of viewport)
  var progress = document.querySelector('[data-scroll-progress]');
  if (progress) {
    var ticking = false;
    var updateProgress = function () {
      var h = document.documentElement;
      var max = h.scrollHeight - h.clientHeight;
      var pct = max > 0 ? (h.scrollTop / max) * 100 : 0;
      progress.style.width = pct.toFixed(1) + '%';
      ticking = false;
    };
    window.addEventListener('scroll', function () {
      if (!ticking) { window.requestAnimationFrame(updateProgress); ticking = true; }
    }, { passive: true });
    updateProgress();
  }

  // Floating contact widget (WhatsApp / Telegram / Phone)
  var fab = document.querySelector('[data-fab]');
  if (fab) {
    var fabToggle = fab.querySelector('[data-fab-toggle]');
    var openFab = function () { fab.classList.add('is-open'); fabToggle.setAttribute('aria-expanded', 'true'); };
    var closeFab = function () { fab.classList.remove('is-open'); fabToggle.setAttribute('aria-expanded', 'false'); };
    if (fabToggle) {
      fabToggle.addEventListener('click', function (e) {
        e.preventDefault();
        if (fab.classList.contains('is-open')) closeFab(); else openFab();
      });
    }
    document.addEventListener('click', function (e) {
      if (!fab.contains(e.target)) closeFab();
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closeFab();
    });
    // Show after small delay (less intrusive on first impression)
    setTimeout(function () { fab.classList.add('is-ready'); }, 800);
  }

  } // init
})();
