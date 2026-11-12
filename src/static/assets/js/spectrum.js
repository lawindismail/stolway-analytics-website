/* Home page hero background: slowly drifting absorption spectra, drawn on a canvas.
   Still picture for visitors who prefer reduced motion; stops while the hero is off screen or paused. */
(function () {
  "use strict";
  var canvas = document.querySelector("canvas[data-spectrum]");
  if (!canvas || !canvas.getContext) return;
  var ctx = canvas.getContext("2d");
  var slider = canvas.closest(".slider");
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var w = 0, h = 0, dpr = 1, raf = 0, t0 = 0, last = 0, visible = true, paused = false;

  // Each trace: where it sits (share of height), colour, and its absorption lines (position, depth, width)
  var TRACES = [
    { y: 0.30, color: "rgba(201,206,242,.30)", width: 1.4, speed: 0.006, lines: [[0.06, 0.5, 9], [0.19, 0.95, 13], [0.31, 0.35, 7], [0.44, 0.7, 11], [0.58, 1, 15], [0.71, 0.45, 8], [0.83, 0.85, 12], [0.95, 0.4, 8]] },
    { y: 0.50, color: "rgba(255,141,128,.34)", width: 1.6, speed: -0.004, lines: [[0.11, 0.8, 16], [0.27, 0.45, 10], [0.39, 1, 20], [0.55, 0.55, 12], [0.68, 0.9, 18], [0.88, 0.6, 14]] },
    { y: 0.68, color: "rgba(201,206,242,.16)", width: 1.2, speed: 0.003, lines: [[0.15, 0.6, 22], [0.36, 0.9, 28], [0.62, 0.5, 20], [0.8, 1, 30]] }
  ];

  function size() {
    var r = canvas.getBoundingClientRect();
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    w = Math.max(1, Math.round(r.width)); h = Math.max(1, Math.round(r.height));
    canvas.width = w * dpr; canvas.height = h * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  function draw(time) {
    ctx.clearRect(0, 0, w, h);
    // faint wavelength grid
    ctx.strokeStyle = "rgba(255,255,255,.045)"; ctx.lineWidth = 1;
    var step = Math.max(64, Math.round(w / 16));
    ctx.beginPath();
    for (var gx = step / 2; gx < w; gx += step) { ctx.moveTo(gx + 0.5, 0); ctx.lineTo(gx + 0.5, h); }
    ctx.stroke();
    var scale = Math.max(0.6, Math.min(w / 1400, 1.25));
    TRACES.forEach(function (tr, k) {
      var depth = h * 0.2;
      var shift = (time * tr.speed) % 1;
      ctx.beginPath();
      for (var x = -2; x <= w + 2; x += 3) {
        var y = h * tr.y;
        for (var i = 0; i < tr.lines.length; i++) {
          var l = tr.lines[i];
          var c = ((l[0] + shift) % 1 + 1) % 1 * (w + 200) - 100;
          var g = l[2] * scale;
          var breathe = 0.72 + 0.28 * Math.sin(time * 0.35 + i * 1.7 + k);
          var dx = x - c;
          y += depth * l[1] * breathe * (g * g) / (dx * dx + g * g);
        }
        if (x === -2) ctx.moveTo(x, y); else ctx.lineTo(x, y);
      }
      ctx.strokeStyle = tr.color; ctx.lineWidth = tr.width; ctx.lineJoin = "round";
      ctx.stroke();
    });
  }

  function frame(now) {
    raf = requestAnimationFrame(frame);
    if (now - last < 33) return;           // about 30 frames a second is plenty
    last = now;
    draw((now - t0) / 1000);
  }
  function sync() {
    cancelAnimationFrame(raf); raf = 0;
    if (reduce || paused || !visible || document.hidden) return;
    raf = requestAnimationFrame(frame);
  }

  size(); draw(8);
  window.addEventListener("resize", function () { size(); draw((performance.now() - t0) / 1000 || 8); });
  document.addEventListener("visibilitychange", sync);
  if ("IntersectionObserver" in window) {
    new IntersectionObserver(function (en) { visible = en[0].isIntersecting; sync(); }, { threshold: 0.05 }).observe(canvas);
  }
  var btn = slider && slider.querySelector(".slider-pause");
  if (btn) btn.addEventListener("click", function () { paused = !paused; sync(); });
  t0 = performance.now() - 8000;
  sync();
})();
