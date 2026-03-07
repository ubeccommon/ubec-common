/**
 * ubec-nav.js — Universal Navigation Bar v3
 * Single unified bar: service identity + ecosystem links + language switcher + login.
 * Login: https://iot.ubec.network/login (Hub SSO — single login for all services)
 * License: GNU AGPL v3.0
 * This project uses the services of Claude and Anthropic PBC.
 */
(function () {
  'use strict';

  const SERVICES = [
    { id: 'portal',      label: 'UBEC Commons',  icon: '🌍', url: 'https://ubec.network' },
    { id: 'protocol',    label: 'UBEC Protocol', icon: '🔗', url: 'https://bioregional.ubec.network' },
    { id: 'maps',        label: 'UBEC Maps',     icon: '🗺️', url: 'https://mapservice.ubec.network' },
    { id: 'living-labs', label: 'Living Labs',   icon: '📡', url: 'https://living-labs.ubec.network' },
    { id: 'hub',         label: 'UBEC Hub',      icon: '⚙️', url: 'https://iot.ubec.network' },
    { id: 'erdpuls',     label: 'Erdpuls',       icon: '🌱', url: 'https://erdpuls.ubec.network' },
    { id: 'open',        label: 'UBEC Open',     icon: '💻', url: 'https://ubeccommon.github.io' },
    { id: 'learn',       label: 'UBEC Learn',    icon: '📚', url: 'https://ubeccommon.github.io/Pattern_Language_of_Place/' },
  ];

  const SUBTITLES = {
    'portal':      'Bioregional Commons',
    'protocol':    'Bioregional Protocol Network',
    'maps':        'Bioregional GIS',
    'living-labs': 'Citizen Science Network',
    'hub':         'Central API & IoT Integration',
    'erdpuls':     'Flagship Living Lab · Müllrose',
    'open':        'Developer Commons',
    'learn':       'Pattern Language of Place',
  };

  const LANGS = [
    { code: 'en', label: 'EN' },
    { code: 'de', label: 'DE' },
    { code: 'pl', label: 'PL' },
  ];

  const LOGIN_URL = 'https://iot.ubec.network/login';

  const LOGIN_LABEL = {
    'en': 'Sign\u00a0in',
    'de': 'Anmelden',
    'pl': 'Zaloguj',
  };

  function currentService() {
    var el = document.documentElement;
    return el ? el.getAttribute('data-ubec-service') : null;
  }

  function currentLang() {
    var m = window.location.pathname.match(/^\/(en|de|pl)(\/|$)/);
    return m ? m[1] : null;
  }

  function langUrl(code) {
    var path = window.location.pathname;
    var m = path.match(/^\/(en|de|pl)(\/.*)?$/);
    if (!m) return null;
    var rest = m[2] || '/';
    return '/' + code + rest + window.location.search;
  }

  function renderNav() {
    var nav = document.getElementById('ubec-nav');
    if (!nav) return;

    var activeId = currentService();
    var lang     = currentLang();
    var active   = SERVICES.find(function(s) { return s.id === activeId; });

    // Logo / service identity
    var logoHtml = active
      ? '<a href="' + active.url + '" class="ubec-nav__logo" aria-label="' + active.label + '">' +
          '<span class="ubec-nav__logo-icon">' + active.icon + '</span>' +
          '<span class="ubec-nav__logo-text">' +
            '<span class="ubec-nav__logo-name">' + active.label + '</span>' +
            '<span class="ubec-nav__logo-sub">' + (SUBTITLES[activeId] || '') + '</span>' +
          '</span>' +
        '</a>'
      : '<a href="https://ubec.network" class="ubec-nav__logo">' +
          '<span class="ubec-nav__logo-name">UBEC\u00a0Commons</span>' +
        '</a>';

    // Service links (exclude active service)
    var items = SERVICES
      .filter(function(s) { return s.id !== activeId; })
      .map(function(s) {
        return '<a href="' + s.url + '" class="ubec-nav__link">' +
          s.icon + '\u00a0' + s.label + '</a>';
      }).join('');

    // Language buttons
    var langItems = LANGS.map(function(l) {
      var isActive = l.code === lang;
      var url = langUrl(l.code);
      var cls = 'ubec-nav__lang' +
        (isActive ? ' ubec-nav__lang--active' : '') +
        (!url ? ' ubec-nav__lang--inactive' : '');
      if (url && !isActive) {
        return '<a href="' + url + '" class="' + cls + '" hreflang="' + l.code + '">' + l.label + '</a>';
      }
      return '<span class="' + cls + '">' + l.label + '</span>';
    }).join('');

    nav.innerHTML =
      '<button class="ubec-nav__hamburger" aria-label="Toggle navigation" aria-expanded="false">' +
        '<span></span><span></span><span></span>' +
      '</button>' +
      logoHtml +
      '<div class="ubec-nav__services" role="navigation" aria-label="UBEC services">' +
        items +
      '</div>' +
      '<div class="ubec-nav__lang-switcher" aria-label="Language">' +
        langItems +
      '</div>' +
      '<a href="' + LOGIN_URL + '" class="ubec-nav__login" aria-label="Sign in to UBEC">' + (LOGIN_LABEL[lang] || LOGIN_LABEL['en']) + '</a>';

    var btn      = nav.querySelector('.ubec-nav__hamburger');
    var services = nav.querySelector('.ubec-nav__services');
    btn.addEventListener('click', function() {
      var open = services.classList.toggle('ubec-nav__services--open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    services.querySelectorAll('.ubec-nav__link').forEach(function(a) {
      a.addEventListener('click', function() {
        services.classList.remove('ubec-nav__services--open');
        btn.setAttribute('aria-expanded', 'false');
      });
    });
  }

  document.addEventListener('DOMContentLoaded', renderNav);
})();
