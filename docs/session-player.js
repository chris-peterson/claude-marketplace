/* Session player — animated transcript playback for bridge.ai surfaces.
   A suite asset: lives with the marketplace and is loaded by the marketplace
   hub and by each plugin's docs site (not by the generic project portal). One
   renderer, two consumers:
     • the hub calls window.mountSession(el, frames) directly;
     • a plugin's docsify site loads this file with a plain <script> tag; any
       <div class="cw-session" data-cw-session="..."> on the page is hydrated
       from that site's plugin-docs.json after each render.
   Frame data is the suite.{examples,session} shape from each plugin.yml. */
(function () {
  "use strict";

  // Build one frame's DOM node. Frame types mirror a Claude Code transcript:
  // chat (you/claude/note), structural (thought/event/sep/status), a shell
  // command, ClaudeWatch's block (watch) / ask prompts, and a moor diff.
  function frameEl(f) {
    var el = document.createElement("div");
    el.className = "fr";
    if (f.t === "you") { el.classList.add("fr-you"); el.innerHTML = '<span class="lbl">❯</span>' + f.text; }
    else if (f.t === "claude") { el.classList.add("fr-claude"); el.innerHTML = '<span class="lbl">⏺</span>' + f.text; }
    else if (f.t === "note") { el.classList.add("fr-note"); el.textContent = f.text; }
    else if (f.t === "thought") { el.classList.add("fr-break"); el.innerHTML = '<span class="bk">thought</span> ⟨' + f.text + '⟩'; }
    else if (f.t === "event") { el.classList.add("fr-break"); el.innerHTML = '<span class="bk">event</span> (' + f.text + ')'; }
    else if (f.t === "sep") { el.classList.add("fr-sep"); }
    else if (f.t === "status") { el.classList.add("fr-status"); el.textContent = f.text; }
    else if (f.t === "cmd") { var skill = /^\//.test(f.cmd) ? " skill" : ""; var stub = f.stub ? ' data-stub="' + f.stub + '"' : ""; el.innerHTML = '<span class="fr-cmd' + skill + '"><span class="cue">›</span><span class="cmdtext"' + stub + '>' + f.cmd + '</span></span>' + (f.out ? '<div class="fr-out">' + f.out + '</div>' : ""); }
    else if (f.t === "watch") { el.innerHTML = '<div class="fr-tool"><div class="t-call"><span class="t-dot">●</span> Bash(<span class="t-cmd">' + f.cmd + '</span>)</div><div class="t-err"><span class="t-branch">⎿</span> Error: ' + f.err + (f.link ? ' — <a href="' + f.link + '" target="_blank" rel="noopener">' + f.link + '</a>' : "") + '</div></div>'; }
    else if (f.t === "ask") { el.innerHTML = '<div class="fr-tool fr-ask"><div class="t-call"><span class="t-dot">●</span> Bash(<span class="t-cmd">' + f.cmd + '</span>)</div><div class="t-conf"><span class="t-branch">⎿</span> PreToolUse:Bash requires confirmation</div><div class="t-reason">' + f.reason + ' — <a href="' + f.link + '" target="_blank" rel="noopener">' + f.link + '</a> <span class="t-plug">[plugin:' + (f.plugin || "ClaudeWatch") + ']</span></div><div class="t-choices"><span class="t-cursor">❯</span> 1. Yes &nbsp;&nbsp; 2. No</div></div>'; }
    else if (f.t === "moor") { el.innerHTML = '<div class="fr-moor"><div class="mbar">moor · reviewing</div><div class="ml del">- ' + f.del + '</div><div class="ml add">+ ' + f.add + '</div><div class="ml rej">' + f.rej + '</div></div>'; }
    else if (f.t === "link") { el.innerHTML = '<span class="lbl">⏺</span><a class="fr-link" href="' + f.href + '" target="_blank" rel="noopener">' + f.text + '</a>'; }
    return el;
  }

  var delayFor = function (f) { if (!f) return 1000; if (f.t === "sep") return 550; if (f.t === "thought" || f.t === "event") return 1200; if (f.t === "cmd") return 1500; if (f.t === "moor") return 1700; if (f.t === "watch") return 1500; if (f.t === "ask") return 2000; if (f.t === "status") return 1300; return 1150; };

  // Autostarts on scroll-in, pauses off-screen, plays once then pins the final
  // state (no loop). Reduced-motion shows every frame at once.
  function buildControls(container) {
    var bar = document.createElement("div");
    bar.className = "sp-controls";
    function btn(cls, glyph, aria) {
      var b = document.createElement("button");
      b.type = "button"; b.className = "sp-btn " + cls; b.textContent = glyph;
      b.setAttribute("aria-label", aria); return b;
    }
    var play = btn("sp-play", "▶", "Play"),
        step = btn("sp-step", "⏭", "Step forward"),
        restart = btn("sp-restart", "↻", "Restart"),
        speed = btn("sp-speed", "1×", "Toggle speed");
    var count = document.createElement("span"); count.className = "sp-count";
    [play, step, restart, count, speed].forEach(function (n) { bar.appendChild(n); });
    container.appendChild(bar);
    return { play: play, step: step, restart: restart, count: count, speed: speed,
      setPlaying: function (p) { play.textContent = p ? "⏸" : "▶"; play.setAttribute("aria-label", p ? "Pause" : "Play"); } };
  }

  // opts.controls adds a play/pause/step/restart bar with a step counter and a
  // 1x/2x speed toggle; opts.typewriter types command frames out char by char.
  // With no opts this is the inline auto-player the per-plugin previews use.
  function mountSession(container, frames, opts) {
    opts = opts || {};
    container.innerHTML = '<div class="tape"></div>';
    var tape = container.querySelector(".tape");
    var els = frames.map(function (f) { var e = frameEl(f); tape.appendChild(e); return e; });
    var reduce = matchMedia("(prefers-reduced-motion:reduce)").matches;
    if (reduce) {
      els.forEach(function (e) { e.classList.add("show"); });
      if (opts.controls) buildControls(container).count.textContent = frames.length + " / " + frames.length;
      return;
    }
    var i = 0, playing = false, timer = null, typing = null, typingEl = null,
        thinkTimer = null, thinkBubble = null, thinkEl = null, speed = 1, userTouched = false;
    var ctl = opts.controls ? buildControls(container) : null;
    function count() { if (ctl) ctl.count.textContent = i + " / " + frames.length; }

    function typeCmd(el, done) {
      var span = el.querySelector(".cmdtext");
      if (!span) { done(); return; }
      if (span._full == null) span._full = span.textContent;
      var full = span._full, stub = span.getAttribute("data-stub") || "", box = el.querySelector(".fr-cmd");
      var src = stub || full, k = 0, tabbed = false;
      span.textContent = ""; el.classList.add("typing"); typingEl = el;
      (function t() {
        if (k <= src.length) { span.textContent = src.slice(0, k); k++; typing = setTimeout(t, (stub ? 115 : 60) / speed); return; }
        // the user hit tab: show the hint, then the completion fills in the namespaced command
        if (stub && !tabbed) {
          tabbed = true;
          if (box) box.classList.add("tabbing");
          typing = setTimeout(function () {
            if (box) { box.classList.remove("tabbing"); box.classList.add("tabbed"); }
            span.textContent = full;
            typing = setTimeout(function () {
              if (box) box.classList.remove("tabbed");
              el.classList.remove("typing"); typing = null; typingEl = null; done();
            }, 320 / speed);
          }, 380 / speed);
          return;
        }
        el.classList.remove("typing"); typing = null; typingEl = null; done();
      })();
    }
    function reveal(idx, done) {
      var f = frames[idx], el = els[idx];
      // emulate the CLI's "Thinking…" beat before a Claude response
      if (opts.thinking && f.t === "claude") {
        thinkBubble = document.createElement("div");
        thinkBubble.className = "fr fr-thinking show";
        thinkBubble.innerHTML = '<span class="tk">· Thinking…</span><span class="tk-meta"> (thinking)</span>';
        tape.insertBefore(thinkBubble, el);
        thinkEl = el;
        thinkTimer = setTimeout(function () {
          if (thinkBubble) thinkBubble.remove();
          el.classList.add("show");
          thinkBubble = thinkEl = thinkTimer = null;
          done();
        }, 1500 / speed);
        return;
      }
      el.classList.add("show");
      if (opts.typewriter && f.t === "cmd") typeCmd(el, done); else done();
    }
    function advance() {
      if (i >= frames.length) { playing = false; if (ctl) ctl.setPlaying(false); return; }
      var idx = i; i++; count();
      reveal(idx, function () { if (playing) timer = setTimeout(advance, delayFor(frames[idx]) / speed); });
    }
    function play() { if (playing || i >= frames.length) return; playing = true; if (ctl) ctl.setPlaying(true); advance(); }
    function pause() {
      playing = false; if (ctl) ctl.setPlaying(false); clearTimeout(timer); clearTimeout(typing); typing = null;
      if (typingEl) { var s = typingEl.querySelector(".cmdtext"); if (s && s._full != null) s.textContent = s._full;
        var cb = typingEl.querySelector(".fr-cmd"); if (cb) cb.classList.remove("tabbing", "tabbed");
        typingEl.classList.remove("typing"); typingEl = null; }
      // finalize an in-progress Thinking… beat: drop the bubble, reveal the response
      if (thinkTimer) { clearTimeout(thinkTimer); thinkTimer = null; }
      if (thinkBubble) { thinkBubble.remove(); thinkBubble = null; }
      if (thinkEl) { thinkEl.classList.add("show"); thinkEl = null; }
    }
    function step() { pause(); if (i >= frames.length) return; var idx = i; i++; count(); reveal(idx, function () {}); }
    function scrollToSection() {
      var sec = (container.closest && container.closest("section")) || container;
      sec.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
    }
    function restart() {
      scrollToSection(); pause(); i = 0;
      var tb = tape.querySelectorAll(".fr-thinking");
      for (var k = 0; k < tb.length; k++) tb[k].remove();
      els.forEach(function (e) { e.classList.remove("show", "typing");
        var s = e.querySelector(".cmdtext"); if (s && s._full != null) s.textContent = s._full;
        var cb = e.querySelector(".fr-cmd"); if (cb) cb.classList.remove("tabbing", "tabbed"); });
      count(); play();
    }
    if (ctl) {
      // play from a stopped state restarts (and scrolls up); while playing it pauses
      ctl.play.addEventListener("click", function () { userTouched = true; playing ? pause() : restart(); });
      ctl.step.addEventListener("click", function () { userTouched = true; step(); });
      ctl.restart.addEventListener("click", function () { userTouched = true; restart(); });
      ctl.speed.addEventListener("click", function () { speed = speed === 1 ? 2 : 1; ctl.speed.textContent = speed + "×"; });
      count();
    }
    // auto-play/pause on scroll — until the viewer takes over via the controls
    var sio = new IntersectionObserver(function (ents) {
      ents.forEach(function (en) { if (userTouched) return; if (en.isIntersecting) play(); else pause(); });
    }, { threshold: .2 });
    sio.observe(container);
  }

  window.mountSession = mountSession;

  // --- Docsify spoke: hydrate .cw-session mount points from plugin-docs.json ---
  // A page carries empty mounts; this fills them after docsify renders.
  //   <div class="cw-session" data-cw-session="session">  → suite.session
  //   <div class="cw-session" data-cw-session="examples"> → suite.examples
  //                                                          (label + frames each)
  //
  // Registers a docsify doneEach hook, which re-runs after every page render.
  // The spoke loads this with a plain <script> tag placed after initProject():
  // the tag executes synchronously before docsify core finishes its async load,
  // so the hook is in window.$docsify.plugins in time to fire. Skipped on the
  // hub (no $docsify), where the renderer is driven imperatively.
  if (window.$docsify) {
    var _suite = null;
    function loadSuite() {
      if (!_suite) {
        _suite = fetch("plugin-docs.json").then(function (r) {
          if (!r.ok) throw new Error("plugin-docs.json responded with " + r.status);
          return r.json();
        });
      }
      return _suite;
    }

    function hydrate(mount, suite) {
      mount.setAttribute("data-cw-mounted", "1");
      var key = mount.getAttribute("data-cw-session");
      if (key === "examples" && Array.isArray(suite.examples)) {
        mount.innerHTML = "";
        suite.examples.forEach(function (ex) {
          var label = document.createElement("div");
          label.className = "cw-ex-label";
          if (ex.ac) label.style.setProperty("--ac", "var(" + ex.ac + ")");
          label.textContent = ex.label || "";
          var box = document.createElement("div");
          box.className = "session";
          if (ex.ac) box.style.setProperty("--ac", "var(" + ex.ac + ")");
          mount.appendChild(label);
          mount.appendChild(box);
          mountSession(box, ex.frames || []);
        });
      } else if (Array.isArray(suite[key])) {
        mount.classList.add("session");
        mountSession(mount, suite[key]);
      }
    }

    window.$docsify.plugins = (window.$docsify.plugins || []).concat(function (hook) {
      hook.doneEach(function () {
        var mounts = document.querySelectorAll(".cw-session[data-cw-session]:not([data-cw-mounted])");
        if (!mounts.length) return;
        loadSuite()
          .then(function (suite) { mounts.forEach(function (m) { hydrate(m, suite); }); })
          .catch(function (err) { console.error("session-player: failed to load plugin-docs.json", err); });
      });
    });
  }
})();
