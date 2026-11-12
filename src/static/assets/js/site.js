/* Stolway site behaviour: mobile menu, header state, hero video and slider, product gallery, enquiry form. No dependencies. */
(function () {
  "use strict";

  // Footer year
  document.querySelectorAll("[data-year]").forEach(function (el) { el.textContent = String(new Date().getFullYear()); });

  // Header shadow once the page scrolls
  var header = document.querySelector(".site-header");
  if (header) {
    var onScroll = function () { header.classList.toggle("is-scrolled", window.scrollY > 8); };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  // Mobile menu: opens under the header, closes on Escape, on a tap outside, or when a link is followed
  var toggle = document.querySelector(".menu-toggle");
  var nav = document.getElementById("site-nav");
  if (toggle && nav) {
    var label = toggle.querySelector("span");
    var setMenu = function (open) {
      toggle.setAttribute("aria-expanded", String(open));
      nav.classList.toggle("is-open", open);
      document.documentElement.classList.toggle("menu-open", open);
      if (label) label.textContent = open ? "Close" : "Menu";
    };
    toggle.addEventListener("click", function () { setMenu(toggle.getAttribute("aria-expanded") !== "true"); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.classList.contains("is-open")) { setMenu(false); toggle.focus(); }
    });
    document.addEventListener("click", function (e) {
      if (!nav.classList.contains("is-open")) return;
      if (e.target.closest("#site-nav a")) { setMenu(false); return; }
      if (!e.target.closest("#site-nav, .menu-toggle")) setMenu(false);
    });
    if (window.matchMedia) {
      var wide = window.matchMedia("(min-width: 1081px)");
      var onWide = function () { if (wide.matches) setMenu(false); };
      if (wide.addEventListener) wide.addEventListener("change", onWide); else if (wide.addListener) wide.addListener(onWide);
    }
  }

  // Submenu toggles (touch and small screens)
  document.querySelectorAll(".sub-toggle").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var li = btn.closest(".has-sub");
      var open = btn.getAttribute("aria-expanded") === "true";
      btn.setAttribute("aria-expanded", String(!open));
      li.classList.toggle("is-open", !open);
    });
  });

  // Product gallery thumbnails
  document.querySelectorAll("[data-gallery]").forEach(function (gallery) {
    var main = gallery.querySelector(".gallery-main img");
    var thumbs = gallery.querySelectorAll(".thumb");
    thumbs.forEach(function (t) {
      t.addEventListener("click", function () {
        main.removeAttribute("srcset");
        main.src = t.getAttribute("data-src");
        main.alt = t.getAttribute("data-alt") || "";
        thumbs.forEach(function (o) { o.setAttribute("aria-pressed", String(o === t)); });
      });
    });
  });


  // Hero slider: auto-advances, pauses on hover/focus, stops for reduced motion.
  // The first slide plays the hero video (assets/video/hero.*) over its poster photo.
  document.querySelectorAll("[data-slider]").forEach(function (slider) {
    var slides = slider.querySelectorAll(".slide");
    var dots = slider.querySelectorAll(".slider-dot");
    var pauseBtn = slider.querySelector(".slider-pause");
    var video = slider.querySelector("video.slide-video");
    // -1 when the video is the shared background behind every banner, otherwise the one slide it belongs to
    var videoSlide = video && video.closest(".slide") ? Array.prototype.indexOf.call(slides, video.closest(".slide")) : -1;
    var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var conn = navigator.connection || {};
    var lite = !!conn.saveData || /(^|-)2g$/.test(conn.effectiveType || "");
    var i = 0, timer = null, paused = false, held = false, inView = true, videoReady = false;
    var single = slides.length < 2;
    var PAUSE = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M5 3v10M11 3v10" stroke="currentColor" stroke-width="2" fill="none"/></svg>';
    var PLAY = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M5 3l8 5-8 5z" fill="currentColor"/></svg>';

    function syncVideo() {
      if (!video || !videoReady) return;
      var want = (videoSlide < 0 || i === videoSlide) && !paused && inView && !document.hidden;
      if (want) { var pr = video.play(); if (pr && pr.catch) pr.catch(function () {}); }
      else video.pause();
    }
    // Load the video and the other slide photos only after the page itself has finished loading
    function loadRest() {
      slider.querySelectorAll("img[data-srcset]").forEach(function (im) { im.srcset = im.getAttribute("data-srcset"); im.removeAttribute("data-srcset"); });
      if (!video || reduce || lite || !video.canPlayType) return;
      [["webm", 'video/webm; codecs="vp9"'], ["mp4", 'video/mp4; codecs="avc1.64001f"']].forEach(function (f) {
        var src = video.getAttribute("data-" + f[0]);
        if (!src) return;
        var el = document.createElement("source");
        el.src = src; el.type = f[1];
        video.appendChild(el);
      });
      video.muted = true; video.defaultMuted = true;
      video.addEventListener("canplay", function () { videoReady = true; syncVideo(); }, { once: true });
      video.addEventListener("playing", function () { video.classList.add("is-playing"); if (pauseBtn && single) pauseBtn.hidden = false; }, { once: true });
      // Thin bar along the bottom of the hero follows the video itself, so changing banner never resets it
      var bar = slider.querySelector(".slider-progress"), fill = bar && bar.querySelector("span"), raf = 0;
      if (fill) {
        var tick = function () {
          if (video.duration) fill.style.transform = "scaleX(" + Math.min(video.currentTime / video.duration, 1).toFixed(4) + ")";
          raf = requestAnimationFrame(tick);
        };
        video.addEventListener("playing", function () { bar.classList.add("is-on"); cancelAnimationFrame(raf); raf = requestAnimationFrame(tick); });
        video.addEventListener("pause", function () { cancelAnimationFrame(raf); });
      }
      video.preload = "auto";
      video.load();
    }
    if (document.readyState === "complete") setTimeout(loadRest, 200); else window.addEventListener("load", function () { setTimeout(loadRest, 200); });
    document.addEventListener("visibilitychange", syncVideo);
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (en) { inView = en[0].isIntersecting; syncVideo(); if (inView) start(); else stop(); }, { threshold: 0.05 }).observe(slider);
    }
    // With one slide the button only controls the video, so it appears once the video is actually playing
    if (pauseBtn) pauseBtn.hidden = reduce || single;
    function label() { return (paused ? "Play " : "Pause ") + (video ? (single ? "video" : "slideshow and video") : "slideshow"); }
    if (pauseBtn) {
      pauseBtn.addEventListener("click", function () {
        paused = !paused;
        pauseBtn.innerHTML = paused ? PLAY : PAUSE;
        pauseBtn.setAttribute("aria-label", label());
        syncVideo();
        if (paused) stop(); else start();
      });
    }
    if (single) return;

    function dwell() { return parseInt(slides[i].getAttribute("data-dwell"), 10) || 7000; }
    function show(n) {
      var prev = i;
      i = (n + slides.length) % slides.length;
      slides.forEach(function (s, k) {
        var on = k === i;
        s.classList.toggle("is-active", on);
        if (on) s.removeAttribute("aria-hidden"); else s.setAttribute("aria-hidden", "true");
        s.querySelectorAll("a").forEach(function (a) { if (on) a.removeAttribute("tabindex"); else a.setAttribute("tabindex", "-1"); });
      });
      dots.forEach(function (d, k) { if (k === i) d.setAttribute("aria-current", "true"); else d.removeAttribute("aria-current"); });
      if (video && videoReady && videoSlide >= 0 && i === videoSlide && prev !== i) { try { video.currentTime = 0; } catch (e) {} }
      syncVideo();
    }
    function start() {
      stop();
      if (single || paused || held || reduce || !inView) return;
      slider.style.setProperty("--dwell", dwell() + "ms");
      slider.classList.add("is-running");
      timer = setTimeout(function () { show(i + 1); start(); }, dwell());
    }
    function stop() { if (timer) clearTimeout(timer); timer = null; slider.classList.remove("is-running"); }
    dots.forEach(function (d, k) { d.addEventListener("click", function () { show(k); start(); }); });
    // Previous / next arrows
    slider.querySelectorAll(".slider-arrow").forEach(function (btn) {
      btn.addEventListener("click", function () { show(i + (btn.classList.contains("slider-arrow--prev") ? -1 : 1)); start(); });
    });
    // Left / right arrow keys while the hero has keyboard focus
    slider.addEventListener("keydown", function (e) {
      if (e.key !== "ArrowLeft" && e.key !== "ArrowRight") return;
      show(i + (e.key === "ArrowLeft" ? -1 : 1)); start();
    });
    // Swipe between slides on touch screens
    var x0 = null, y0 = null;
    slider.addEventListener("touchstart", function (e) { x0 = e.touches[0].clientX; y0 = e.touches[0].clientY; }, { passive: true });
    slider.addEventListener("touchend", function (e) {
      if (x0 === null) return;
      var dx = e.changedTouches[0].clientX - x0, dy = e.changedTouches[0].clientY - y0;
      x0 = null;
      if (Math.abs(dx) > 48 && Math.abs(dx) > Math.abs(dy) * 1.5) { show(i + (dx < 0 ? 1 : -1)); start(); }
    }, { passive: true });
    var canHover = window.matchMedia && window.matchMedia("(hover: hover)").matches;
    if (canHover) {
      slider.addEventListener("mouseenter", function () { held = true; stop(); });
      slider.addEventListener("mouseleave", function () { held = false; start(); });
    }
    slider.addEventListener("focusin", function (e) { if (e.target.matches && e.target.matches(":focus-visible")) { held = true; stop(); } });
    slider.addEventListener("focusout", function () { if (held && !slider.matches(":hover")) { held = false; start(); } });
    start();
  });

  // Tabs (capabilities): arrow keys move between tabs
  document.querySelectorAll("[data-tabs]").forEach(function (box) {
    var tabs = Array.prototype.slice.call(box.querySelectorAll('[role="tab"]'));
    function select(t, focus) {
      tabs.forEach(function (o) {
        var on = o === t;
        o.setAttribute("aria-selected", String(on));
        o.tabIndex = on ? 0 : -1;
        document.getElementById(o.getAttribute("aria-controls")).hidden = !on;
      });
      if (focus) t.focus();
    }
    tabs.forEach(function (t, k) {
      t.addEventListener("click", function () { select(t, false); });
      t.addEventListener("keydown", function (e) {
        var n = null;
        if (e.key === "ArrowDown" || e.key === "ArrowRight") n = tabs[(k + 1) % tabs.length];
        if (e.key === "ArrowUp" || e.key === "ArrowLeft") n = tabs[(k - 1 + tabs.length) % tabs.length];
        if (e.key === "Home") n = tabs[0];
        if (e.key === "End") n = tabs[tabs.length - 1];
        if (n) { e.preventDefault(); select(n, true); }
      });
    });
  });

  /* ---------- Motion: scroll reveals, counters, parallax, progress ---------- */
  (function () {
    var root = document.documentElement;
    if (!root.classList.contains("motion") || !("IntersectionObserver" in window)) { root.classList.remove("motion"); return; }
    root.classList.add("motion-ready");

    var groups = {
      up: ".why-lead, .film, .center-head, .feature-card, .custom-box, .cta-inner, .cap, .accordion, .intro-grid, .split > .stack, .contact-grid > .stack, .about-block > .stack, .aus-text, .footer-certs, .project-list > *, .slider-foot .quick-links",
      wipe: ".about-media, .why-media, .split-media, .feature-media",
      stagger: ".why-grid, .office-grid, .quick-contact, .contact-aside, .timeline, .mini-grid, .app-grid, .project-grid, .card-grid, .spec-cols, .aus-points, .contact-side, .product-grid, .industry-list, .stats, .footer-top",
      draw: ".aus-mark"
    };
    var targets = [];
    Object.keys(groups).forEach(function (kind) {
      document.querySelectorAll(groups[kind]).forEach(function (el) {
        if (el.closest(".slider, .banner, .product-hero") || el.hasAttribute("data-reveal")) return;
        el.setAttribute("data-reveal", kind);
        if (kind === "stagger") Array.prototype.forEach.call(el.children, function (c, i) { c.style.setProperty("--i", Math.min(i, 8)); });
        targets.push(el);
      });
    });

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        e.target.classList.add("is-in");
        if (e.target.matches(".stats")) countUp(e.target);
        io.unobserve(e.target);
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.12 });
    targets.forEach(function (el) { io.observe(el); });

    // Count-up statistics
    function countUp(box) {
      box.querySelectorAll("dd").forEach(function (dd) {
        var end = parseInt(dd.textContent, 10); if (isNaN(end)) return;
        var start = end > 1000 ? end - 33 : 0, t0 = null, dur = 1400;
        dd.style.minWidth = dd.offsetWidth + "px";
        function step(t) {
          if (!t0) t0 = t;
          var k = Math.min((t - t0) / dur, 1), ease = 1 - Math.pow(1 - k, 4);
          dd.textContent = String(Math.round(start + (end - start) * ease));
          if (k < 1) requestAnimationFrame(step);
        }
        requestAnimationFrame(step);
      });
    }

    // Fade in lazy images as they load
    document.querySelectorAll('img[loading="lazy"]').forEach(function (img) {
      if (img.complete && img.naturalWidth) return;
      img.classList.add("img-fade");
      img.addEventListener("load", function () { img.classList.add("is-loaded"); }, { once: true });
      img.addEventListener("error", function () { img.classList.add("is-loaded"); }, { once: true });
    });

    // Scroll progress bar and banner parallax
    var bar = document.createElement("div");
    bar.className = "scroll-progress"; bar.setAttribute("aria-hidden", "true");
    document.body.appendChild(bar);
    var para = Array.prototype.slice.call(document.querySelectorAll(".banner-media img, .slide-media img"));
    var ticking = false;
    function frame() {
      ticking = false;
      var y = window.scrollY, h = document.documentElement.scrollHeight - window.innerHeight;
      bar.style.transform = "scaleX(" + (h > 0 ? Math.min(y / h, 1) : 0) + ")";
      if (y < window.innerHeight * 1.2) para.forEach(function (img) { img.style.setProperty("--py", (y * 0.22).toFixed(1) + "px"); });
    }
    window.addEventListener("scroll", function () { if (!ticking) { ticking = true; requestAnimationFrame(frame); } }, { passive: true });
    frame();
  })();

  // Product films: the poster's play button starts the video with its normal controls; starting one pauses any other
  var films = Array.prototype.slice.call(document.querySelectorAll("[data-film]"));
  films.forEach(function (film) {
    var v = film.querySelector("video"), btn = film.querySelector(".film-play");
    if (!v || !btn) return;
    btn.addEventListener("click", function () {
      film.classList.add("is-started");
      v.controls = true;
      var pr = v.play(); if (pr && pr.catch) pr.catch(function () {});
      v.focus();
    });
    v.addEventListener("play", function () {
      films.forEach(function (o) { var ov = o.querySelector("video"); if (ov && ov !== v) ov.pause(); });
    });
  });

  // Product pages on phones: a quote bar pinned to the bottom once the page's own quote buttons have scrolled away
  var buyBar = document.querySelector("[data-buy-bar]");
  if (buyBar) {
    var heroBtns = document.querySelector(".product-summary .btn-row"), foot = document.querySelector(".site-footer"), barTick = false;
    var syncBar = function () {
      barTick = false;
      var past = heroBtns ? heroBtns.getBoundingClientRect().bottom < 60 : window.scrollY > 600;
      var atFoot = foot ? foot.getBoundingClientRect().top < window.innerHeight : false;
      var on = past && !atFoot;
      buyBar.classList.toggle("is-on", on);
      document.documentElement.classList.toggle("buy-bar-on", on);
    };
    window.addEventListener("scroll", function () { if (!barTick) { barTick = true; requestAnimationFrame(syncBar); } }, { passive: true });
    window.addEventListener("resize", syncBar);
    syncBar();
  }

  // Back-to-top button appears once the visitor is well down the page
  var toTop = document.querySelector(".to-top");
  if (toTop) {
    toTop.hidden = false;
    var onTop = function () { toTop.classList.toggle("is-visible", window.scrollY > 900); };
    onTop();
    window.addEventListener("scroll", onTop, { passive: true });
    toTop.addEventListener("click", function (e) {
      e.preventDefault();
      var calm = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      window.scrollTo({ top: 0, behavior: calm ? "auto" : "smooth" });
    });
  }

  // Enquiry form
  var form = document.getElementById("enquiry-form");
  if (!form) return;

  // Preselect enquiry type and system from the link that brought the visitor here (?type=quote&system=chillers)
  try {
    var params = new URLSearchParams(window.location.search);
    var type = params.get("type");
    var system = params.get("system");
    if (type && form.elements.type) {
      var opt = form.elements.type.querySelector('option[value="' + type.replace(/[^a-z-]/g, "") + '"]');
      if (opt) form.elements.type.value = opt.value;
    }
    if (system && form.elements.system) {
      var sopt = form.elements.system.querySelector('option[value="' + system.replace(/[^a-z-]/g, "") + '"]');
      if (sopt) form.elements.system.value = sopt.value;
    }
  } catch (e) { /* older browsers: leave defaults */ }

  var status = form.querySelector(".form-status");
  var submit = form.querySelector('button[type="submit"]');

  function setError(field, message) {
    var wrap = field.closest(".field");
    var err = wrap && wrap.querySelector(".error");
    field.setAttribute("aria-invalid", message ? "true" : "false");
    if (err) { err.textContent = message || ""; err.hidden = !message; }
  }

  function validate() {
    var ok = true;
    var first = null;
    [["name", "Enter your name."], ["email", "Enter your email address."], ["message", "Tell us a little about your requirement."]].forEach(function (pair) {
      var f = form.elements[pair[0]];
      if (!f) return;
      var val = (f.value || "").trim();
      var msg = val ? "" : pair[1];
      if (!msg && pair[0] === "email" && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val)) msg = "Enter an email address like name@company.com.";
      setError(f, msg);
      if (msg) { ok = false; if (!first) first = f; }
    });
    if (first) first.focus();
    return ok;
  }

  function show(kind, html) {
    status.className = "form-status form-status--" + kind;
    status.innerHTML = html;
    status.hidden = false;
    status.focus();
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    if (form.elements.company_website && form.elements.company_website.value) return; // spam trap
    if (!validate()) return;

    var endpoint = form.getAttribute("data-endpoint");
    var to = form.getAttribute("data-fallback-email") || "info@stolway.com.au";
    if (!endpoint) {
      // No form service connected: open the visitor's email app with the enquiry already written out
      var val = function (n) { var f = form.elements[n]; return f ? (f.value || "").trim() : ""; };
      var text = function (n) { var f = form.elements[n]; return f && f.selectedIndex >= 0 && f.value ? f.options[f.selectedIndex].text : ""; };
      var lines = [["Name", val("name")], ["Email", val("email")], ["Phone", val("phone")], ["Company", val("company")],
        ["I need", text("type")], ["System", text("system")], ["Project location", val("location")], ["Hazardous area classification", val("classification")]]
        .filter(function (r) { return r[1]; }).map(function (r) { return r[0] + ": " + r[1]; });
      var body = lines.join("\r\n") + "\r\n\r\n" + val("message") + "\r\n";
      var subject = "Website enquiry: " + (text("type") || "General") + (val("company") ? " (" + val("company") + ")" : "");
      window.location.href = "mailto:" + to + "?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(body);
      show("ok", "Your email app should now open with your enquiry ready to send. If it doesn't, email <a href=\"mailto:" + to + "\"><strong>" + to + "</strong></a> or call <a href=\"tel:+61242623000\"><strong>+61 2 4262 3000</strong></a>.");
      return;
    }
    submit.disabled = true;
    submit.textContent = "Sending…";
    fetch(endpoint, { method: "POST", headers: { "Accept": "application/json" }, body: new FormData(form) })
      .then(function (r) { if (!r.ok) throw new Error(String(r.status)); })
      .then(function () {
        form.reset();
        show("ok", "Thanks, your enquiry has been sent. A Stolway engineer will reply by email.");
      })
      .catch(function () {
        show("warn", "Your enquiry couldn't be sent. Please email <strong>" + to + "</strong> instead.");
      })
      .then(function () { submit.disabled = false; submit.textContent = "Send enquiry"; });
  });

})();
