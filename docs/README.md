<style>
@import url('https://fonts.googleapis.com/css2?family=IM+Fell+English:ital@0;1&family=IM+Fell+English+SC&family=Spectral:ital,wght@0,300;0,400;0,500;0,600;1,400&family=JetBrains+Mono:wght@400;500&display=swap');

.markdown-section {
  --bg: #282a36;
  --bg-deep: #1a1b26;
  --surface: #44475a;
  --comment: #6272a4;
  --fg: #f8f8f2;
  --cyan: #8be9fd;
  --green: #50fa7b;
  --orange: #ffb86c;
  --pink: #ff79c6;
  --purple: #bd93f9;
  --red: #ff5555;
  --yellow: #f1fa8c;

  font-family: 'Spectral', 'Iowan Old Style', Georgia, serif;
  font-weight: 400;
  font-size: 17px;
  line-height: 1.7;
  max-width: 1100px;
}

.markdown-section h1,
.markdown-section h2,
.markdown-section h3 {
  font-family: 'IM Fell English', 'Iowan Old Style', Georgia, serif;
  font-weight: 400;
  letter-spacing: 0.01em;
}

.markdown-section h2 {
  font-size: 1.85em;
  margin-top: 2.4em;
  position: relative;
  padding-left: 1.4em;
  color: var(--fg);
}

.markdown-section h2::before {
  content: "";
  position: absolute;
  left: 0;
  top: 0.45em;
  width: 0.9em;
  height: 0.9em;
  background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><g fill='none' stroke='%23bd93f9' stroke-width='1.4' stroke-linecap='round'><circle cx='16' cy='16' r='13'/><path d='M16 3 L16 29 M3 16 L29 16'/><path d='M16 6 L18 16 L16 26 L14 16 Z' fill='%23bd93f9' fill-opacity='0.4'/><path d='M6 16 L16 14 L26 16 L16 18 Z' fill='%238be9fd' fill-opacity='0.4'/></g></svg>");
  background-size: contain;
  background-repeat: no-repeat;
}

.markdown-section code,
.markdown-section pre code {
  font-family: 'JetBrains Mono', ui-monospace, monospace;
  font-size: 0.92em;
}

.markdown-section pre {
  background: linear-gradient(180deg, #1f2030 0%, #16171f 100%);
  border: 1px solid var(--surface);
  border-left: 3px solid var(--purple);
  border-radius: 4px;
  box-shadow: inset 0 0 24px rgba(0,0,0,0.35);
  padding: 1em 1.2em;
}

.markdown-section pre[data-lang]::after {
  content: attr(data-lang);
  font-family: 'IM Fell English SC', serif;
  letter-spacing: 0.18em;
  color: var(--comment);
  font-size: 0.7em;
}

.markdown-section table {
  border-collapse: collapse;
  width: 100%;
  background: transparent;
  font-family: 'Spectral', serif;
  margin-top: 1.2em;
}

.markdown-section table thead th {
  font-family: 'IM Fell English SC', serif;
  font-weight: 400;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  font-size: 0.78em;
  color: var(--cyan);
  border-bottom: 1px solid var(--comment);
  background: transparent;
  padding: 0.7em 1em;
  text-align: left;
}

.markdown-section table tbody td {
  border-bottom: 1px dotted var(--surface);
  padding: 0.85em 1em;
  vertical-align: top;
  background: transparent;
}

.markdown-section table tbody tr:nth-child(even) td {
  background: rgba(68, 71, 90, 0.18);
}

.markdown-section table tbody tr:hover td {
  background: rgba(139, 233, 253, 0.06);
}

.markdown-section table a {
  font-family: 'IM Fell English SC', serif;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  font-size: 0.95em;
  color: var(--purple);
  text-decoration: none;
  border-bottom: 1px solid transparent;
}

.markdown-section table a:hover {
  color: var(--pink);
  border-bottom-color: var(--pink);
}

.plugin-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.9em;
  margin: 1.4em 0 2.4em;
}

.plugin-card {
  display: flex;
  align-items: center;
  gap: 1em;
  padding: 1em 1.2em 0.95em;
  background: linear-gradient(160deg, #2f3142 0%, #25262f 100%);
  border-radius: 8px;
  border: 1px solid var(--surface);
  border-bottom-width: 2px;
  text-decoration: none !important;
  transition: transform 0.18s ease, border-color 0.2s ease, box-shadow 0.25s ease;
}

.plugin-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 14px 28px -16px #000;
  text-decoration: none !important;
}

.plugin-card .icon {
  width: 48px;
  height: 48px;
  flex-shrink: 0;
  border-radius: 10px;
}

.plugin-card .meta {
  display: flex;
  flex-direction: column;
  gap: 0.2em;
  min-width: 0;
}

.plugin-card .name {
  font-family: 'JetBrains Mono', ui-monospace, monospace;
  font-weight: 500;
  font-size: 1.05em;
  color: var(--fg);
  letter-spacing: -0.01em;
}

.plugin-card .desc {
  font-family: 'Spectral', serif;
  font-size: 0.93em;
  color: var(--comment);
  line-height: 1.45;
}

.plugin-card.beacon-card           { border-bottom-color: var(--cyan); }
.plugin-card.beacon-card:hover     { border-color: var(--cyan); }
.plugin-card.claudewatch-card      { border-bottom-color: var(--orange); }
.plugin-card.claudewatch-card:hover{ border-color: var(--orange); }
.plugin-card.logbook-card          { border-bottom-color: var(--green); }
.plugin-card.logbook-card:hover    { border-color: var(--green); }
.plugin-card.tack-card             { border-bottom-color: var(--purple); }
.plugin-card.tack-card:hover       { border-color: var(--purple); }

@media (max-width: 760px) {
  .plugin-grid { grid-template-columns: 1fr; }
}
</style>

<div class="plugin-grid">
  <a class="plugin-card beacon-card" href="https://chris-peterson.github.io/beacon/#/">
    <img class="icon" src="https://chris-peterson.github.io/beacon/favicon.svg" alt=""/>
    <div class="meta">
      <span class="name">beacon</span>
      <span class="desc">At-a-glance Claude Code session awareness</span>
    </div>
  </a>
  <a class="plugin-card claudewatch-card" href="https://chris-peterson.github.io/ClaudeWatch/#/">
    <img class="icon" src="https://chris-peterson.github.io/ClaudeWatch/favicon.svg" alt=""/>
    <div class="meta">
      <span class="name">ClaudeWatch</span>
      <span class="desc">Pre-tool-call command-safety hook</span>
    </div>
  </a>
  <a class="plugin-card logbook-card" href="https://chris-peterson.github.io/logbook/#/">
    <img class="icon" src="https://chris-peterson.github.io/logbook/favicon.svg" alt=""/>
    <div class="meta">
      <span class="name">logbook</span>
      <span class="desc">AI-coding-session retros, committed to git</span>
    </div>
  </a>
  <a class="plugin-card tack-card" href="https://chris-peterson.github.io/tack/#/">
    <img class="icon" src="https://chris-peterson.github.io/tack/favicon.svg" alt=""/>
    <div class="meta">
      <span class="name">tack</span>
      <span class="desc">Route-aware tracker for AI-assisted development</span>
    </div>
  </a>
</div>

## Add the marketplace

```bash
claude plugins marketplace add https://github.com/chris-peterson/claude-marketplace
```

## Install plugins

```bash
claude plugins install beacon@chris-peterson
claude plugins install ClaudeWatch@chris-peterson
claude plugins install logbook@chris-peterson
claude plugins install tack@chris-peterson
```

See [How they fit together](/relationships) for the workflow roles each plugin plays and how they interact.
