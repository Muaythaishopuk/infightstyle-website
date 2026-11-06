/* Shared header, footer and event rendering. Edit events in /events.js, not here. */
(function () {
  "use strict";

  var SITE = {
    shopUrl: "https://www.themuaythaishop.co.uk/",
    juniorRangeUrl: "https://www.themuaythaishop.co.uk/collections/junior",
    facebook: "https://www.facebook.com/profile.php?id=61576369900462&locale=en_GB",
    instagram: "https://www.instagram.com/ifsjuniorleagueuk",
    instagramLeague: "https://www.instagram.com/infightstylefightleague",
    email: "info@infightstylefightleague.co.uk",
    sponsorEmail: "infightjuniors@gmail.com",
  };

  var NAV = [
    ["Home", "/"],
    ["Gallery", "/gallery/"],
    ["Next events", "/next-events/"],
    ["Past events", "/past-events/"],
    ["News", "/news/"],
    ["Muay Thai Shop", SITE.shopUrl],
    ["Sponsors", "/sponsors/"],
    ["Contact", "/contact-us/"],
  ];

  var ICONS = {
    facebook:
      '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M13.5 22v-8.2h2.8l.4-3.2h-3.2V8.5c0-.9.3-1.6 1.6-1.6h1.7V4.1c-.3 0-1.3-.1-2.5-.1-2.5 0-4.2 1.5-4.2 4.3v2.4H7.3v3.2h2.8V22h3.4z"/></svg>',
    instagram:
      '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 7a5 5 0 100 10 5 5 0 000-10zm0 8.2a3.2 3.2 0 110-6.4 3.2 3.2 0 010 6.4zM17.3 5.5a1.2 1.2 0 100 2.4 1.2 1.2 0 000-2.4zM21.9 7.9c-.1-1.6-.4-3-1.6-4.2S17.7 2.2 16.1 2.1C14.5 2 9.5 2 7.9 2.1 6.3 2.2 4.9 2.5 3.7 3.7S2.2 6.3 2.1 7.9C2 9.5 2 14.5 2.1 16.1c.1 1.6.4 3 1.6 4.2s2.6 1.5 4.2 1.6c1.6.1 6.6.1 8.2 0 1.6-.1 3-.4 4.2-1.6s1.5-2.6 1.6-4.2c.1-1.6.1-6.6 0-8.2zm-2.1 10a3.3 3.3 0 01-1.8 1.8c-1.3.5-4.3.4-5.9.4s-4.6.1-5.9-.4a3.3 3.3 0 01-1.8-1.8c-.5-1.3-.4-4.3-.4-5.9s-.1-4.6.4-5.9a3.3 3.3 0 011.8-1.8c1.3-.5 4.3-.4 5.9-.4s4.6-.1 5.9.4a3.3 3.3 0 011.8 1.8c.5 1.3.4 4.3.4 5.9s.1 4.6-.4 5.9z"/></svg>',
  };

  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function isExternal(href) {
    return /^https?:/.test(href);
  }

  function link(label, href, cls) {
    var ext = isExternal(href) ? ' target="_blank" rel="noopener"' : "";
    return '<a href="' + esc(href) + '"' + (cls ? ' class="' + cls + '"' : "") + ext + ">" + label + "</a>";
  }

  function socials() {
    return (
      '<div class="socials">' +
      '<a href="' + SITE.facebook + '" target="_blank" rel="noopener" aria-label="Facebook">' + ICONS.facebook + "</a>" +
      '<a href="' + SITE.instagramLeague + '" target="_blank" rel="noopener" aria-label="Instagram: INFIGHTSTYLE Fight League" title="@infightstylefightleague">' + ICONS.instagram + "</a>" +
      '<a href="' + SITE.instagram + '" target="_blank" rel="noopener" aria-label="Instagram: IFS Junior League" title="@ifsjuniorleagueuk">' + ICONS.instagram + "</a>" +
      "</div>"
    );
  }

  function currentPath() {
    var p = location.pathname.replace(/index\.html$/, "");
    return p.endsWith("/") ? p : p + "/";
  }

  function renderHeader() {
    var el = document.getElementById("site-header");
    if (!el) return;
    var here = currentPath();
    var items = NAV.map(function (n) {
      var active = n[1] === here ? ' aria-current="page"' : "";
      var ext = isExternal(n[1]) ? ' target="_blank" rel="noopener"' : "";
      return '<li><a href="' + n[1] + '"' + active + ext + ">" + n[0] + "</a></li>";
    }).join("");
    el.innerHTML =
      '<a class="promo" href="' + SITE.juniorRangeUrl + '" target="_blank" rel="noopener">Shop the Infightstyle junior range now →</a>' +
      '<div class="bar wrap">' +
      '<a class="brand" href="/"><span>Infightstyle</span> Fight League</a>' +
      '<button class="menu-btn" aria-expanded="false" aria-controls="nav">Menu</button>' +
      '<nav id="nav"><ul>' + items + "</ul></nav>" +
      "</div>";
    var btn = el.querySelector(".menu-btn");
    btn.addEventListener("click", function () {
      var open = el.classList.toggle("open");
      btn.setAttribute("aria-expanded", String(open));
    });
  }

  function renderFooter() {
    var el = document.getElementById("site-footer");
    if (!el) return;
    el.innerHTML =
      '<div class="wrap footer-inner">' +
      socials() +
      "<p>© " + new Date().getFullYear() + " Infightstyle Fight League. All rights reserved.</p>" +
      "</div>";
  }

  /* ---------- events ---------- */

  var MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
  var DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

  function parseDate(s) {
    var p = s.split("-");
    return new Date(+p[0], +p[1] - 1, +p[2]);
  }

  function ordinal(n) {
    var s = ["th", "st", "nd", "rd"], v = n % 100;
    return n + (s[(v - 20) % 10] || s[v] || s[0]);
  }

  function prettyDate(s) {
    var d = parseDate(s);
    return DAYS[d.getDay()] + " " + ordinal(d.getDate()) + " " + MONTHS[d.getMonth()] + " " + d.getFullYear();
  }

  function splitEvents() {
    var all = (window.IFS_EVENTS || []).slice();
    // Preview the site as if it were another day: add ?today=2026-10-01 to the address.
    var forced = new URLSearchParams(location.search).get("today");
    var today = forced ? parseDate(forced) : new Date();
    today.setHours(0, 0, 0, 0);
    var next = all.filter(function (e) { return parseDate(e.date) >= today; })
      .sort(function (a, b) { return parseDate(a.date) - parseDate(b.date); });
    var past = all.filter(function (e) { return parseDate(e.date) < today; })
      .sort(function (a, b) { return parseDate(b.date) - parseDate(a.date); });
    return { next: next, past: past };
  }

  function paragraphs(list) {
    return (list || []).map(function (p) { return "<p>" + esc(p) + "</p>"; }).join("");
  }

  function eventCard(e, isPast) {
    var text = isPast && e.writeUp && e.writeUp.length ? e.writeUp : e.preview;
    var meta = '<p class="meta">' + esc(prettyDate(e.date)) + (e.venue ? " · " + esc(e.venue) : "") + "</p>";
    var prices = !isPast && e.prices && e.prices.length
      ? '<ul class="prices">' + e.prices.map(function (p) { return "<li>" + esc(p) + "</li>"; }).join("") + "</ul>"
      : "";
    var cta = !isPast && e.entryUrl ? link(esc(e.entryLabel || "Sign up on Kihapp"), e.entryUrl, "btn") : "";
    var poster = e.poster
      ? '<a class="poster" href="/images/' + esc(e.poster) + '" target="_blank" rel="noopener"><img src="/images/' + esc(e.poster) + '" alt="' + esc(e.title) + ' poster" loading="lazy"></a>'
      : "";
    return (
      '<article class="event' + (poster ? "" : " no-poster") + '">' +
      '<div class="event-body">' +
      (e.tag ? '<span class="tag">' + esc(e.tag) + "</span>" : "") +
      "<h3>" + esc(e.title) + "</h3>" + meta + paragraphs(text) + prices + cta +
      "</div>" + poster + "</article>"
    );
  }

  function comingSoon() {
    return (
      '<div class="panel center">' +
      "<h3>Next event announced soon</h3>" +
      "<p>Follow us for dates, fight cards and sign-up links the moment they go live.</p>" +
      socials() +
      "</div>"
    );
  }

  function renderList(id, events, isPast) {
    var el = document.getElementById(id);
    if (!el) return;
    if (!events.length) {
      el.innerHTML = isPast ? "<p>No past events yet.</p>" : comingSoon();
      return;
    }
    el.innerHTML = events.map(function (e) { return eventCard(e, isPast); }).join("");
  }

  function renderHero(split) {
    var el = document.getElementById("hero");
    if (!el) return;
    var e = split.next[0];
    var label = "Next event";
    if (!e) {
      e = split.past.filter(function (x) { return x.poster; })[0];
      label = "Latest event";
    }
    var body;
    if (split.next[0]) {
      body =
        '<p class="eyebrow">' + label + " · " + esc(prettyDate(e.date)) + "</p>" +
        "<h1>" + esc(e.title) + "</h1>" +
        (e.venue ? '<p class="lead">' + esc(e.venue) + "</p>" : "") +
        '<div class="actions">' +
        (e.entryUrl ? link(esc(e.entryLabel || "Click here to enter"), e.entryUrl, "btn") : "") +
        '<a class="btn ghost" href="/next-events/">All upcoming events</a></div>';
    } else {
      body =
        '<p class="eyebrow">Junior Muay Thai · UK</p>' +
        "<h1>Infightstyle Junior Fight League</h1>" +
        '<p class="lead">Professional junior Muay Thai shows and tournaments. Our next event will be announced soon. Follow us so you don\'t miss sign-ups.</p>' +
        '<div class="actions"><a class="btn" href="/past-events/">See past events</a>' +
        '<a class="btn ghost" href="/contact-us/">Get in touch</a></div>';
    }
    var img = e && e.poster
      ? '<img src="/images/' + esc(e.poster) + '" alt="' + esc(e.title) + ' poster">'
      : "";
    if (!img && split.next[0] && e.prices && e.prices.length) {
      img = '<div class="panel hero-tickets"><p class="eyebrow">Tickets</p><ul class="prices">' +
        e.prices.map(function (p) { return "<li>" + esc(p) + "</li>"; }).join("") + "</ul>" +
        paragraphs(e.preview.slice(0, 1)) + "</div>";
    }
    el.innerHTML = '<div class="wrap hero-inner"><div class="hero-text">' + body + "</div>" +
      (img ? '<figure class="hero-img" style="margin:0">' + img +
        (split.next[0] ? "" : '<figcaption>Latest event: ' + esc(e.title) + ' · <a href="/past-events/">see all past events</a></figcaption>') +
        "</figure>" : "") + "</div>";
  }

  /* ---------- news ---------- */

  function postsSorted() {
    return (window.IFS_POSTS || []).slice().sort(function (a, b) { return parseDate(b.date) - parseDate(a.date); });
  }

  function renderNewsList() {
    var el = document.getElementById("news-list");
    if (!el) return;
    var posts = postsSorted();
    if (!posts.length) { el.innerHTML = "<p>No news yet.</p>"; return; }
    el.innerHTML = posts.map(function (p) {
      return '<article class="card news-card"><p class="meta">' + esc(prettyDate(p.date)) + "</p>" +
        '<h3><a href="/news/post/?p=' + encodeURIComponent(p.slug) + '">' + esc(p.title) + "</a></h3>" +
        "<p>" + esc(p.summary) + "</p>" +
        '<a class="btn ghost" href="/news/post/?p=' + encodeURIComponent(p.slug) + '">Read more</a></article>';
    }).join("");
  }

  function block(b) {
    if (typeof b === "string") return "<p>" + esc(b) + "</p>";
    if (b.h) return "<h2>" + esc(b.h) + "</h2>";
    if (b.list) return "<ul>" + b.list.map(function (i) { return "<li>" + esc(i) + "</li>"; }).join("") + "</ul>";
    if (b.img) return '<img class="post-img" src="/images/' + esc(b.img) + '" alt="' + esc(b.alt || "") + '" loading="lazy">';
    if (b.button) return '<div class="actions">' + link(esc(b.button), b.url, "btn") + "</div>";
    return "";
  }

  function renderPost() {
    var el = document.getElementById("post");
    if (!el) return;
    var slug = new URLSearchParams(location.search).get("p");
    var post = postsSorted().filter(function (p) { return p.slug === slug; })[0];
    if (!post) {
      el.innerHTML = '<h1>Post not found</h1><p><a href="/news/">Back to all news</a></p>';
      return;
    }
    document.title = post.title + " | INFIGHTSTYLE Fight League";
    var d = document.querySelector('meta[name="description"]');
    if (d) d.setAttribute("content", post.summary);
    el.innerHTML = '<p class="eyebrow">' + esc(prettyDate(post.date)) + "</p><h1>" + esc(post.title) + "</h1>" +
      '<p class="lead">' + esc(post.summary) + "</p>" + post.body.map(block).join("") +
      '<p class="back"><a href="/news/">← All news</a></p>';
  }

  document.addEventListener("DOMContentLoaded", function () {
    renderNewsList();
    renderPost();
    renderHeader();
    renderFooter();
    var split = splitEvents();
    renderHero(split);
    renderList("next-events", split.next, false);
    renderList("past-events", split.past, true);
    var home = document.getElementById("home-next");
    if (home) renderList("home-next", split.next.slice(0, 2), false);
    document.querySelectorAll("[data-email]").forEach(function (a) {
      var addr = SITE[a.getAttribute("data-email")];
      a.href = "mailto:" + addr;
      if (!a.textContent.trim()) a.textContent = addr;
    });
    document.querySelectorAll("[data-socials]").forEach(function (s) { s.innerHTML = socials(); });
  });
})();
