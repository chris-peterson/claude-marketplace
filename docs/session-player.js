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
  // command, ClaudeWatch's block (watch) / ask prompts, and a diff under review.
  function frameEl(f) {
    var el = document.createElement("div");
    el.className = "fr";
    if (f.t === "shell") { el.classList.add("fr-shell"); el.dataset.shcmd = f.cmd || "claude";
      var git = f.branch ? ' <span class="sh-git">git:(<span class="sh-branch">' + f.branch + '</span>)</span>' : '';
      el.innerHTML = '<span class="sh-arrow">➜</span>  <span class="sh-path">' + f.path + '</span>' + git + '<span class="sh-cmd"></span>'; }
    else if (f.t === "banner") { el.classList.add("fr-banner"); el.innerHTML = '<pre class="bnr">'
      + '           <span class="bnr-app">Claude Code</span> <span class="bnr-dim">v2.1.207</span>\n'
      + '<span class="bnr-logo"> ▐▛███▜▌</span>   <span class="bnr-txt">Opus 4.8 (1M context)</span>\n'
      + '<span class="bnr-logo">▝▜█████▛▘</span>  <span class="bnr-txt">Claude Team</span>\n'
      + '<span class="bnr-logo">  ▘▘ ▝▝</span>    <span class="bnr-dim">~/…/' + f.path + '</span>'
      + '</pre>'; }
    else if (f.t === "you") { el.classList.add("fr-you"); if (f.retro) el.classList.add("retro");
      var yc = f.cmd ? '<span class="you-cmd skill"><span class="cmdtext"' + (f.stub ? ' data-stub="' + f.stub + '"' : '') + '>' + f.cmd + '</span></span>' : '';
      el.innerHTML = '<span class="lbl">❯</span><span class="you-text">' + (f.text || "") + '</span>' + yc + (f.out ? '<div class="fr-out">' + f.out + '</div>' : ""); }
    else if (f.t === "claude") { el.classList.add("fr-claude");
      var eds = (f.edits || []).map(function (e) {
        var lines = e.diff.split("\n"), added = 0, removed = 0, oldLn = e.ln || 1, newLn = e.ln || 1;
        var body = lines.map(function (l) {
          var ch = l.charAt(0);
          if (ch === "+") { added++; return '<div class="edl add"><span class="ed-ln">' + (newLn++) + '</span><span class="ed-code">' + l + '</span></div>'; }
          if (ch === "-") { removed++; return '<div class="edl del"><span class="ed-ln">' + (oldLn++) + '</span><span class="ed-code">' + l + '</span></div>'; }
          var n = oldLn++; newLn++; return '<div class="edl"><span class="ed-ln">' + n + '</span><span class="ed-code">' + l + '</span></div>';
        }).join("");
        var sum = "Added " + added + " line" + (added === 1 ? "" : "s") + (removed ? ", removed " + removed + " line" + (removed === 1 ? "" : "s") : "");
        return '<div class="fr-edit"><div class="ed-head"><span class="ed-dot">●</span> Update(<span class="ed-file">' + e.file + '</span>)</div>'
          + '<div class="ed-sum"><span class="ed-branch">⎿</span> ' + sum + '</div><div class="ed-diff">' + body + '</div></div>';
      }).join("");
      el.innerHTML = eds + '<div class="cl-resp"><span class="lbl">⏺</span>' + f.text + '</div>'; }
    else if (f.t === "note") { el.classList.add("fr-note"); el.textContent = f.text; }
    else if (f.t === "thought") { el.classList.add("fr-break"); el.innerHTML = '<span class="bk">thought</span> ⟨' + f.text + '⟩'; }
    else if (f.t === "event") { el.classList.add("fr-break"); el.innerHTML = '<span class="bk">event</span> (' + f.text + ')'; }
    else if (f.t === "sep") { el.classList.add("fr-sep"); }
    else if (f.t === "status") { el.classList.add("fr-status"); el.textContent = f.text; }
    else if (f.t === "cmd") { var skill = /^\//.test(f.cmd) ? " skill" : ""; var stub = f.stub ? ' data-stub="' + f.stub + '"' : ""; el.innerHTML = '<span class="fr-cmd' + skill + '"><span class="cue">›</span><span class="cmdtext"' + stub + '>' + f.cmd + '</span></span>' + (f.out ? '<div class="fr-out">' + f.out + '</div>' : ""); }
    else if (f.t === "watch") { el.innerHTML = '<div class="fr-tool"><div class="t-call"><span class="t-dot">●</span> Bash(<span class="t-cmd">' + f.cmd + '</span>)</div><div class="t-err"><span class="t-branch">⎿</span> Error: ' + f.err + (f.link ? ' — <a href="' + f.link + '" target="_blank" rel="noopener">' + f.link + '</a>' : "") + '</div></div>'; }
    else if (f.t === "ask") { el.innerHTML = '<div class="fr-tool fr-ask">'
      + '<div class="t-call"><span class="t-dot">●</span> Bash(<span class="t-cmd">' + f.cmd + '</span>)</div>'
      + '<div class="t-gate">'
      +   '<div class="t-conf"><span class="t-branch">⎿</span> PreToolUse:Bash requires confirmation</div>'
      +   '<div class="t-reason">' + f.reason + ' — <a href="' + f.link + '" target="_blank" rel="noopener">' + f.link + '</a> <span class="t-plug">[plugin:' + (f.plugin || "ClaudeWatch") + ']</span></div>'
      +   '<div class="t-choices"><span class="t-cursor">❯</span> <span class="t-yes">1. Yes</span> &nbsp;&nbsp; <span class="t-no">2. No</span></div>'
      + '</div>'
      + '<div class="t-result"><span class="t-branch">⎿</span> ' + (f.result || "done") + '</div>'
      + '</div>'; }
    else if (f.t === "diff") {
      // anchor drives whichever review backend git is pointed at, so the window
      // emulates git's own diff output and names none of them. The @@ header is
      // derived from the frame: an added line doesn't count toward the old side,
      // a removed one doesn't count toward the new. Its two ranges follow git's
      // unified format — a count of 1 is left implicit, and a side with no lines
      // is numbered from the line it would be inserted after.
      var dls = f.lines || [], start = dls.length ? dls[0].ln : 1;
      var range = function (n) { return n === 0 ? (start - 1) + ",0" : (n === 1 ? String(start) : start + "," + n); };
      var oldCount = dls.filter(function (l) { return !l.add; }).length,
          newCount = dls.filter(function (l) { return !l.del; }).length;
      var drows = dls.map(function (l) {
        var cls = l.add ? " add" : (l.del ? " del" : ""), sign = l.add ? "+" : (l.del ? "-" : " ");
        var row = '<div class="drow' + cls + '"><span class="dln">' + l.ln + '</span><span class="dsign">' + sign + '</span><span class="dcode">' + l.text + '</span></div>';
        if (f.comment && f.comment.ln === l.ln) {
          row += '<div class="dcmt">' + f.comment.body + '</div>';
        }
        return row;
      }).join("");
      var dv = f.verdict ? '<div class="dverdict">✓ ' + f.verdict + '</div>' : '';
      el.innerHTML = '<div class="fr-diff"><div class="dhead">'
        + '<span class="dfile">diff --git a/' + f.file + ' b/' + f.file + '</span>'
        + '<span class="dhunk">@@ -' + range(oldCount) + ' +' + range(newCount) + ' @@</span>'
        + '</div><div class="dbody">' + drows + dv + '</div></div>';
    }
    else if (f.t === "link") { el.classList.add("fr-linkrow"); var ext = /^https?:/.test(f.href) ? ' target="_blank" rel="noopener"' : '';
      el.innerHTML = '<span class="lbl">⏺</span><a class="fr-link" href="' + f.href + '"' + ext + '>' + f.text + '</a>' + (f.after ? '<span class="fr-linkafter">' + f.after + '</span>' : ""); }
    else if (f.t === "enter") { el.classList.add("fr-confirm"); }  // no line — it selects "Yes" on the ask
    else if (f.t === "done") { el.classList.add("fr-donerow"); el.innerHTML = '<span class="dn-mark">■</span> session done; run <code>/exit</code> to close'; }
    return el;
  }

  var delayFor = function (f) { if (!f) return 1000; if (f.t === "shell") return 700; if (f.t === "banner") return 1500; if (f.t === "sep") return 550; if (f.t === "thought" || f.t === "event") return 1200; if (f.t === "cmd") return 1500; if (f.t === "diff") return 1700; if (f.t === "watch") return 1500; if (f.t === "ask") return 2600; if (f.t === "enter") return 900; if (f.t === "note") return 2200; if (f.t === "status") return 1300; return 1150; };

  // Wall clock of one play at 1x — each frame's dwell plus the keystrokes the
  // typewriter spends on it, off the same constants the typing routines use. The
  // poster prints it, so pressing play is an informed choice.
  function typeMs(f) { return !f.cmd ? 0 : (f.stub ? 115 * f.stub.length + 700 : 60 * f.cmd.length); }
  function runtime(frames, opts) {
    var ms = frames.reduce(function (a, f) {
      var t = delayFor(f);
      if (opts.typewriter && f.t === "shell") t += 800 + 75 * (String(f.cmd || "claude").length + 1);
      if (opts.typewriter && f.t === "you") { t += 15 * String(f.text || "").length + typeMs(f) + (f.retro ? 1300 : 0); }
      if (opts.typewriter && f.t === "cmd") t += typeMs(f);
      if (opts.thinking && f.t === "claude") t += (f.establishes ? 650 : 0) + (f.thinkMs || 1500);
      return a + t;
    }, 0);
    var s = Math.round(ms / 5000) * 5;
    return s >= 60 ? Math.floor(s / 60) + "m " + (s % 60 ? (s % 60) + "s" : "") : s + "s";
  }

  // Plays once then pins the final state (no loop). Reduced-motion shows every
  // frame at once. opts.poster parks it until pressed; otherwise it autostarts
  // on scroll-in and pauses off-screen.
  function buildControls(container) {
    var bar = document.createElement("div");
    bar.className = "sp-controls";
    function btn(cls, glyph, aria) {
      var b = document.createElement("button");
      b.type = "button"; b.className = "sp-btn " + cls; b.textContent = glyph;
      b.setAttribute("aria-label", aria); return b;
    }
    var play = btn("sp-play", "▶", "Play"),
        back = btn("sp-back", "‹", "Step back"),
        step = btn("sp-step", "›", "Step forward"),
        restart = btn("sp-restart", "↻", "Restart");
    [play, back, step, restart].forEach(function (n) { bar.appendChild(n); });
    container.appendChild(bar);
    return { play: play, back: back, step: step, restart: restart,
      setPlaying: function (p) { play.textContent = p ? "⏸" : "▶"; play.setAttribute("aria-label", p ? "Pause" : "Play"); } };
  }

  // The parked screen a poster replay opens on. Its play target borrows the
  // beacon tab's chip treatment — tinted fill inside a hairline ring — so it
  // reads as part of the pane rather than a video control dropped on top of it.
  function buildPoster(stage, frames, opts, onPlay) {
    var p = document.createElement("div");
    p.className = "sp-poster";
    p.innerHTML = '<button class="sp-poster-btn" type="button" aria-label="Play the session replay"><span class="sp-tri">▶</span></button>'
      + '<span class="sp-poster-meta">' + frames.length + ' frames · about ' + runtime(frames, opts) + '</span>';
    p.querySelector(".sp-poster-btn").addEventListener("click", onPlay);
    stage.appendChild(p);
    return p;
  }

  // opts.controls adds a play/pause/step/restart bar; opts.typewriter types
  // command frames out char by char; opts.poster parks the replay behind a play
  // target instead of autostarting. With no opts this is the inline auto-player
  // the per-plugin previews use.
  function mountSession(container, frames, opts) {
    opts = opts || {};
    // the stage is the transcript's viewport: a consumer that fixes its height
    // (the hub pane) gets scrollback inside it instead of a growing page
    container.innerHTML = '<div class="sp-stage"><div class="tape"></div></div>';
    var stage = container.querySelector(".sp-stage");
    var tape = container.querySelector(".tape");
    var els = frames.map(function (f) { var e = frameEl(f); tape.appendChild(e); return e; });
    var reduce = matchMedia("(prefers-reduced-motion:reduce)").matches;
    if (reduce) {
      els.forEach(function (e) { e.classList.add("show"); });
      if (opts.controls) buildControls(container);
      return;
    }
    var i = 0, playing = false, timer = null, typing = null, typingEl = null,
        thinkTimer = null, contextTimer = null, thinkBubble = null, thinkEl = null,
        thinkFrame = null, thinkIdx = -1, speed = 1, userTouched = false;
    var ctl = opts.controls ? buildControls(container) : null;
    var poster = opts.poster ? buildPoster(stage, frames, opts, function () { dismissPoster(); play(); }) : null;
    function dismissPoster() { if (poster) { poster.remove(); poster = null; } }
    function count() { if (ctl && ctl.count) ctl.count.textContent = i + " / " + frames.length; }
    // hold the newest frame in view as the transcript outgrows the stage. A frame
    // taller than the viewport pins its head; anything shorter rides the bottom.
    function follow(el, up) {
      if (!el || stage.scrollHeight <= stage.clientHeight) return;
      var view = stage.clientHeight;
      var target = el.offsetHeight >= view - 24 ? el.offsetTop - 12 : el.offsetTop + el.offsetHeight - view + 18;
      target = Math.max(0, target);
      if (!up && target <= stage.scrollTop) return;
      stage.scrollTop = target;   // a terminal's scrollback jumps; a smooth scroll would trail the frames
    }

    function typeCmd(el, done) {
      var span = el.querySelector(".cmdtext"), box = el.querySelector(".fr-cmd");
      if (!span) { done(); return; }
      el.classList.add("typing"); typingEl = el;
      typeCmdSpan(box, span, function () { el.classList.remove("typing"); typing = null; typingEl = null; done(); });
    }
    // type a command span out to the prefix the user actually types, then submit
    // (the ↵ beat) and flash-complete to the full namespaced command — Claude
    // resolves it on enter, not on tab. Shared by cmd frames and the inline
    // commands a "you" message can carry.
    function typeCmdSpan(wrap, span, done) {
      if (span._full == null) span._full = span.textContent;
      var full = span._full, stub = span.getAttribute("data-stub") || "", src = stub || full, k = 0, submitted = false;
      span.textContent = "";
      (function t() {
        if (k <= src.length) { span.textContent = src.slice(0, k); k++; typing = setTimeout(t, (stub ? 115 : 60) / speed); return; }
        if (stub && !submitted) {
          submitted = true; if (wrap) wrap.classList.add("submitting");
          typing = setTimeout(function () {
            if (wrap) { wrap.classList.remove("submitting"); wrap.classList.add("filled"); }
            span.textContent = full;
            typing = setTimeout(function () { if (wrap) wrap.classList.remove("filled"); done(); }, 320 / speed);
          }, 380 / speed);
          return;
        }
        done();
      })();
    }
    // f.type / f.cmd on a "you" frame types the message out as the user enters it:
    // the leading prose first, then any inline slash command (Claude fills in a
    // mid-message stub — /com → /anchor:commit — once it's submitted).
    function typeYou(el, done) {
      var textSpan = el.querySelector(".you-text");
      var cmdWrap = el.querySelector(".you-cmd"), cmdSpan = cmdWrap && cmdWrap.querySelector(".cmdtext");
      el.classList.add("typing-you"); typingEl = el;
      var full = textSpan ? (textSpan._full != null ? textSpan._full : (textSpan._full = textSpan.textContent)) : "", k = 0;
      if (textSpan) textSpan.textContent = "";
      function finish() { el.classList.remove("typing-you"); typing = null; typingEl = null; done(); }
      (function t() {
        if (k <= full.length) { if (textSpan) textSpan.textContent = full.slice(0, k); k++; typing = setTimeout(t, 15 / speed); return; }
        if (cmdSpan) typeCmdSpan(cmdWrap, cmdSpan, finish); else finish();
      })();
    }
    // opts.typewriter: the user typing a command (`cd …`, `claude`) at a fresh
    // shell prompt. A beat of empty terminal (blinking caret) precedes the keys.
    function typeShell(el, done) {
      var span = el.querySelector(".sh-cmd");
      if (!span) { done(); return; }
      var full = " " + (el.dataset.shcmd || "claude"); span._full = full;
      span.textContent = ""; el.classList.add("typing-sh"); typingEl = el;
      var k = 0;
      typing = setTimeout(function t() {
        if (k <= full.length) { span.textContent = full.slice(0, k); k++; typing = setTimeout(t, 75 / speed); return; }
        el.classList.remove("typing-sh"); typing = null; typingEl = null; done();
      }, 800 / speed);
    }
    // A Claude turn signals through the pane before it answers. onReveal fires
    // 'enter' (Claude picks up the turn — cut the branch), then 'context' (it has
    // settled what it's doing — name the task), and only THEN does the long
    // "Thinking…" beat run: the fleet view is current before the deep think. The
    // branch→task staging is gated to the opening turn (f.establishes); later
    // turns keep the labels they already carry and think straight away.
    function reveal(idx, done) {
      var f = frames[idx], el = els[idx];
      if (opts.thinking && f.t === "claude") {
        thinkEl = el; thinkFrame = f; thinkIdx = idx;
        if (opts.onReveal) opts.onReveal(f, idx, "enter");
        var startThinking = function () {
          thinkBubble = document.createElement("div");
          thinkBubble.className = "fr fr-thinking show";
          thinkBubble.innerHTML = '<span class="tk">· Thinking…</span><span class="tk-meta"> (' + (f.think || "thinking") + ')</span>';
          tape.insertBefore(thinkBubble, el);
          follow(thinkBubble);
          thinkTimer = setTimeout(function () {
            if (thinkBubble) thinkBubble.remove();
            el.classList.add("show"); follow(el);
            thinkBubble = thinkEl = thinkFrame = thinkTimer = null; thinkIdx = -1;
            done();
          }, (f.thinkMs || 1500) / speed);
        };
        if (f.establishes) {
          contextTimer = setTimeout(function () {
            contextTimer = null;
            if (opts.onReveal) opts.onReveal(f, idx, "context");
            startThinking();
          }, 650 / speed);
        } else { startThinking(); }
        return;
      }
      if (opts.onReveal) opts.onReveal(f, idx, f.t === "claude" ? "context" : false);
      el.classList.add("show"); follow(el);
      // the user confirming the permission prompt: press + select "Yes" in place,
      // rather than echoing a carriage return
      if (f.t === "enter") {
        var ask = tape.querySelector(".fr-ask"), yes = ask && ask.querySelector(".t-yes");
        if (!ask) { done(); return; }
        if (yes) yes.classList.add("flash");                 // quick keypress flash
        typing = setTimeout(function () { ask.classList.add("confirmed"); typing = null; done(); }, 340 / speed);  // then the prompt is answered — dismiss the choices
        return;
      }
      // f.retro: the pane doesn't flip to the retro treatment until Claude has
      // thought for a beat — so type the command, then a Thinking… beat, then
      // publish the retro state (green) and hand off.
      var afterYou = (opts.typewriter && f.retro) ? function () {
        thinkBubble = document.createElement("div");
        thinkBubble.className = "fr fr-thinking show";
        thinkBubble.innerHTML = '<span class="tk">· Thinking…</span><span class="tk-meta"> (retro)</span>';
        tape.insertBefore(thinkBubble, el.nextSibling);
        follow(thinkBubble);
        thinkEl = el; thinkFrame = f; thinkIdx = idx;
        thinkTimer = setTimeout(function () {
          if (thinkBubble) thinkBubble.remove();
          if (opts.onReveal) opts.onReveal(f, idx, "retro");
          thinkBubble = thinkEl = thinkFrame = thinkTimer = null; thinkIdx = -1;
          done();
        }, 1300 / speed);
      } : done;
      if (opts.typewriter && f.t === "cmd") typeCmd(el, done);
      else if (opts.typewriter && f.t === "shell") typeShell(el, done);
      else if (opts.typewriter && f.t === "you" && (f.type || f.cmd)) typeYou(el, afterYou);
      else done();
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
        var sh = typingEl.querySelector(".sh-cmd"); if (sh && sh._full != null) sh.textContent = sh._full;
        var yt = typingEl.querySelector(".you-text"); if (yt && yt._full != null) yt.textContent = yt._full;
        var cb = typingEl.querySelector(".fr-cmd, .you-cmd"); if (cb) cb.classList.remove("submitting", "filled");
        typingEl.classList.remove("typing", "typing-sh", "typing-you"); typingEl = null; }
      // finalize an in-progress context/Thinking… beat: publish the state it was
      // about to (task label, or the retro treatment), drop the bubble, reveal
      if (contextTimer) { clearTimeout(contextTimer); contextTimer = null;
        if (opts.onReveal && thinkFrame) opts.onReveal(thinkFrame, thinkIdx, "context"); }
      if (thinkTimer) { clearTimeout(thinkTimer); thinkTimer = null; }
      if (thinkBubble) { thinkBubble.remove(); thinkBubble = null; }
      if (thinkEl) { thinkEl.classList.add("show"); follow(thinkEl);
        if (opts.onReveal && thinkFrame && thinkFrame.retro) opts.onReveal(thinkFrame, thinkIdx, "retro");
        thinkEl = thinkFrame = null; thinkIdx = -1; }
    }
    function step() { pause(); if (i >= frames.length) return; var idx = i; i++; count(); reveal(idx, function () {}); }
    // repaint the beacon pane (tab/branch/state) as of `n` frames revealed,
    // replaying each frame's settled state — so stepping back stays in sync
    function paintStateAt(n) {
      if (!opts.onReveal) return;
      for (var k = 0; k <= (n < 0 ? 0 : n); k++) {
        var fr = frames[k];
        var ph = (fr.t === "claude" && fr.establishes) ? "context"
               : (fr.t === "you" && fr.retro) ? "retro"
               : (fr.t === "claude") ? "enter" : false;
        opts.onReveal(fr, k, ph);
      }
    }
    function stepBack() {
      pause(); if (i <= 0) return;
      i--;
      var e = els[i];
      e.classList.remove("show", "typing", "typing-sh", "typing-you");
      var cb = e.querySelector(".fr-cmd, .you-cmd"); if (cb) cb.classList.remove("submitting", "filled");
      if (frames[i].t === "enter") { var ak = tape.querySelector(".fr-ask"); if (ak) { ak.classList.remove("confirmed"); var ay = ak.querySelector(".t-yes"); if (ay) ay.classList.remove("flash"); } }
      var tb = tape.querySelectorAll(".fr-thinking"); for (var k = 0; k < tb.length; k++) tb[k].remove();
      count(); paintStateAt(i - 1);
      if (i > 0) follow(els[i - 1], true); else stage.scrollTop = 0;
    }
    function scrollToSection() {
      var sec = (container.closest && container.closest("section")) || container;
      sec.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
    }
    function restart() {
      scrollToSection(); pause(); i = 0; stage.scrollTop = 0;
      var tb = tape.querySelectorAll(".fr-thinking");
      for (var k = 0; k < tb.length; k++) tb[k].remove();
      els.forEach(function (e) { e.classList.remove("show", "typing", "typing-sh", "typing-you");
        var s = e.querySelector(".cmdtext"); if (s && s._full != null) s.textContent = s._full;
        var sh = e.querySelector(".sh-cmd"); if (sh && sh._full != null) sh.textContent = sh._full;
        var yt = e.querySelector(".you-text"); if (yt && yt._full != null) yt.textContent = yt._full;
        var cb = e.querySelector(".fr-cmd, .you-cmd"); if (cb) cb.classList.remove("submitting", "filled"); });
      var ak = tape.querySelector(".fr-ask"); if (ak) { ak.classList.remove("confirmed"); var ay = ak.querySelector(".t-yes"); if (ay) ay.classList.remove("flash"); }
      count(); play();
    }
    if (ctl) {
      // the first press leaves the poster; after that, play from a stopped state
      // restarts (and scrolls up), and while playing it pauses
      ctl.play.addEventListener("click", function () {
        if (poster) { dismissPoster(); play(); return; }
        userTouched = true; playing ? pause() : restart(); });
      ctl.back.addEventListener("click", function () { userTouched = true; dismissPoster(); stepBack(); });
      ctl.step.addEventListener("click", function () { userTouched = true; dismissPoster(); step(); });
      ctl.restart.addEventListener("click", function () { userTouched = true; dismissPoster(); restart(); });
      count();
    }
    // auto-play/pause on scroll — until the viewer takes over via the controls
    var sio = new IntersectionObserver(function (ents) {
      ents.forEach(function (en) { if (userTouched || poster) return; if (en.isIntersecting) play(); else pause(); });
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
