/* Session player — animated transcript playback for bridge.ai surfaces.
   A suite asset: lives with the marketplace and is loaded by the marketplace
   hub and by each plugin's docs site (not by the generic project portal). One
   renderer, two consumers:
     • the hub calls window.mountSession(el, frames) directly;
     • a plugin's docsify site loads this file with a plain <script> tag; any
       <div class="cw-session" data-cw-session="..."> on the page is hydrated
       from that site's suite.json after each render.
   Frame data is the suite.{examples,session} shape from each plugin.yml. */
(function () {
  "use strict";

  // Build one frame's DOM node. Frame types mirror a Claude Code transcript:
  // chat (you/claude/note), structural (thought/event/sep/status), a shell
  // command, ClaudeWatch's block (watch) / ask prompts, and a moor diff.
  function frameEl(f) {
    var el = document.createElement("div");
    el.className = "fr";
    if (f.t === "you") { el.classList.add("fr-you"); el.innerHTML = '<span class="lbl">&gt;</span>' + f.text; }
    else if (f.t === "claude") { el.classList.add("fr-claude"); el.innerHTML = '<span class="lbl">*</span>' + f.text; }
    else if (f.t === "note") { el.classList.add("fr-note"); el.textContent = f.text; }
    else if (f.t === "thought") { el.classList.add("fr-break"); el.innerHTML = '<span class="bk">thought</span> ⟨' + f.text + '⟩'; }
    else if (f.t === "event") { el.classList.add("fr-break"); el.innerHTML = '<span class="bk">event</span> (' + f.text + ')'; }
    else if (f.t === "sep") { el.classList.add("fr-sep"); }
    else if (f.t === "status") { el.classList.add("fr-status"); el.textContent = f.text; }
    else if (f.t === "cmd") { el.innerHTML = '<span class="fr-cmd"><span class="cue">›</span>' + f.cmd + '</span>' + (f.out ? '<div class="fr-out">' + f.out + '</div>' : ""); }
    else if (f.t === "watch") { el.innerHTML = '<div class="fr-tool"><div class="t-call"><span class="t-dot">●</span> Bash(<span class="t-cmd">' + f.cmd + '</span>)</div><div class="t-err"><span class="t-branch">⎿</span> Error: ' + f.err + (f.link ? ' — <a href="' + f.link + '" target="_blank" rel="noopener">' + f.link + '</a>' : "") + '</div></div>'; }
    else if (f.t === "ask") { el.innerHTML = '<div class="fr-tool fr-ask"><div class="t-call"><span class="t-dot">●</span> Bash(<span class="t-cmd">' + f.cmd + '</span>)</div><div class="t-conf"><span class="t-branch">⎿</span> PreToolUse:Bash requires confirmation</div><div class="t-reason">' + f.reason + ' — <a href="' + f.link + '" target="_blank" rel="noopener">' + f.link + '</a> <span class="t-plug">[plugin:' + (f.plugin || "ClaudeWatch") + ']</span></div><div class="t-choices"><span class="t-cursor">❯</span> 1. Yes &nbsp;&nbsp; 2. No</div></div>'; }
    else if (f.t === "moor") { el.innerHTML = '<div class="fr-moor"><div class="mbar">moor · reviewing</div><div class="ml del">- ' + f.del + '</div><div class="ml add">+ ' + f.add + '</div><div class="ml rej">' + f.rej + '</div></div>'; }
    return el;
  }

  var delayFor = function (f) { if (!f) return 1000; if (f.t === "sep") return 550; if (f.t === "thought" || f.t === "event") return 1200; if (f.t === "cmd") return 1500; if (f.t === "moor") return 1700; if (f.t === "watch") return 1500; if (f.t === "ask") return 2000; if (f.t === "status") return 1300; return 1150; };

  // Autostarts on scroll-in, pauses off-screen, plays once then pins the final
  // state (no loop). Reduced-motion shows every frame at once.
  function mountSession(container, frames) {
    container.innerHTML = '<div class="tape"></div>';
    var tape = container.querySelector(".tape");
    var els = frames.map(function (f) { var e = frameEl(f); tape.appendChild(e); return e; });
    if (matchMedia("(prefers-reduced-motion:reduce)").matches) { els.forEach(function (e) { e.classList.add("show"); }); return; }
    var i = 0, vis = false, timer = null;
    var tick = function () {
      if (!vis) return;
      if (i >= frames.length) return;   // finished — hold the final state, don't loop
      els[i].classList.add("show"); i++; timer = setTimeout(tick, delayFor(frames[i - 1]));
    };
    var sio = new IntersectionObserver(function (ents) { ents.forEach(function (en) { if (en.isIntersecting) { if (!vis) { vis = true; tick(); } } else { vis = false; clearTimeout(timer); } }); }, { threshold: .2 });
    sio.observe(container);
  }

  window.mountSession = mountSession;

  // --- Docsify spoke: hydrate .cw-session mount points from suite.json ---
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
        _suite = fetch("suite.json").then(function (r) {
          if (!r.ok) throw new Error("suite.json responded with " + r.status);
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
          .catch(function (err) { console.error("session-player: failed to load suite.json", err); });
      });
    });
  }
})();
