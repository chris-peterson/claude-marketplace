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

.harbor-hero {
  position: relative;
  margin: 0 0 2.5em;
  border-radius: 6px;
  overflow: hidden;
  box-shadow: 0 18px 40px -20px #000, inset 0 0 0 1px var(--surface);
  background: var(--bg-deep);
}

.harbor-hero svg {
  display: block;
  width: 100%;
  height: auto;
}

.harbor-tagline {
  font-family: 'Spectral', serif;
  font-style: italic;
  font-size: 1.08em;
  color: var(--comment);
  border-left: 2px solid var(--purple);
  padding-left: 1em;
  margin: 1.6em 0 2.4em;
}

.harbor-tagline strong {
  font-style: normal;
  font-weight: 500;
  color: var(--fg);
}

.harbor-scene .star {
  fill: #f8f8f2;
}

.harbor-scene .lighthouse-beam {
  mix-blend-mode: screen;
}

.harbor-scene .plugin-link {
  cursor: pointer;
  transition: filter 0.3s ease;
}

.harbor-scene .plugin-link:hover {
  filter: brightness(1.3) drop-shadow(0 0 6px currentColor);
}

.harbor-scene .plugin-link .plugin-label {
  font-family: 'IM Fell English SC', serif;
  font-size: 14px;
  letter-spacing: 0.32em;
  fill: var(--fg);
  opacity: 0.78;
  transition: opacity 0.25s ease, fill 0.25s ease;
}

.harbor-scene .plugin-link:hover .plugin-label {
  opacity: 1;
  fill: currentColor;
}

.harbor-scene .plugin-link .underline {
  stroke: currentColor;
  stroke-width: 0.8;
  stroke-dasharray: 2 3;
  opacity: 0;
  transition: opacity 0.25s ease;
}

.harbor-scene .plugin-link:hover .underline {
  opacity: 0.7;
}

.harbor-scene .beacon-link    { color: var(--cyan); }
.harbor-scene .tack-link      { color: var(--pink); }
.harbor-scene .logbook-link   { color: var(--green); }

.harbor-scene .compass {
  opacity: 0.18;
}

@media (max-width: 760px) {
  .harbor-hero { margin: 0 0 2em; }
  .harbor-scene .plugin-label { font-size: 18px; }
}
</style>

<div class="harbor-hero">
  <svg class="harbor-scene" viewBox="0 0 1200 540" role="img" aria-label="A nighttime harbor scene: an open ship's log resting on a foreshore rock, a sailing ship tacking across the water, and a lighthouse on a cliff casting a static beam onto the ship.">
    <defs>
      <linearGradient id="sky" x1="0" x2="0" y1="0" y2="1">
        <stop offset="0%"  stop-color="#15161e"/>
        <stop offset="55%" stop-color="#282a36"/>
        <stop offset="100%" stop-color="#3d3553"/>
      </linearGradient>
      <linearGradient id="sea" x1="0" x2="0" y1="0" y2="1">
        <stop offset="0%"  stop-color="#1f2030"/>
        <stop offset="100%" stop-color="#0c0d14"/>
      </linearGradient>
      <linearGradient id="beam" gradientUnits="userSpaceOnUse" x1="600" y1="158" x2="115" y2="385">
        <stop offset="0%"   stop-color="#8be9fd" stop-opacity="0.6"/>
        <stop offset="55%"  stop-color="#8be9fd" stop-opacity="0.22"/>
        <stop offset="100%" stop-color="#8be9fd" stop-opacity="0"/>
      </linearGradient>
      <pattern id="ripples" x="0" y="0" width="60" height="14" patternUnits="userSpaceOnUse">
        <path d="M0 7 Q15 2 30 7 T60 7" fill="none" stroke="#8be9fd" stroke-width="0.6" opacity="0.35"/>
      </pattern>
      <filter id="soft-glow" x="-50%" y="-50%" width="200%" height="200%">
        <feGaussianBlur stdDeviation="2.5" result="b"/>
        <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
      </filter>
    </defs>
    <rect width="1200" height="540" fill="url(#sky)"/>
    <g class="stars" fill="#f8f8f2">
      <circle cx="60"   cy="38"  r="1.1" class="star twinkle-a"/>
      <circle cx="140"  cy="92"  r="0.7" class="star twinkle-b"/>
      <circle cx="215"  cy="58"  r="0.9" class="star twinkle-c"/>
      <circle cx="290"  cy="120" r="0.6" class="star twinkle-d"/>
      <circle cx="365"  cy="48"  r="1.0" class="star twinkle-b"/>
      <circle cx="430"  cy="100" r="0.7" class="star twinkle-a"/>
      <circle cx="510"  cy="70"  r="0.8" class="star twinkle-d"/>
      <circle cx="595"  cy="35"  r="0.6" class="star twinkle-c"/>
      <circle cx="668"  cy="110" r="0.9" class="star twinkle-a"/>
      <circle cx="745"  cy="60"  r="0.7" class="star twinkle-b"/>
      <circle cx="820"  cy="135" r="1.0" class="star twinkle-c"/>
      <circle cx="900"  cy="40"  r="0.7" class="star twinkle-d"/>
      <circle cx="1095" cy="180" r="0.8" class="star twinkle-a"/>
      <circle cx="1150" cy="140" r="0.6" class="star twinkle-b"/>
      <circle cx="170"  cy="180" r="0.7" class="star twinkle-c"/>
      <circle cx="55"   cy="220" r="0.6" class="star twinkle-d"/>
      <circle cx="930"  cy="155" r="0.7" class="star twinkle-b"/>
      <circle cx="1015" cy="220" r="0.6" class="star twinkle-a"/>
    </g>
    <g class="constellation" stroke="#bd93f9" stroke-width="0.5" opacity="0.35" fill="none">
      <line x1="60"  y1="38"  x2="140" y2="92"/>
      <line x1="140" y1="92"  x2="215" y2="58"/>
      <line x1="215" y1="58"  x2="290" y2="120"/>
    </g>
    <g class="compass" transform="translate(1140 60)">
      <circle r="32" fill="none" stroke="#bd93f9" stroke-width="0.6"/>
      <circle r="22" fill="none" stroke="#bd93f9" stroke-width="0.4"/>
      <path d="M0 -28 L4 0 L0 28 L-4 0 Z" fill="#bd93f9" opacity="0.6"/>
      <path d="M-28 0 L0 -4 L28 0 L0 4 Z" fill="#8be9fd" opacity="0.6"/>
      <text x="0" y="-34" text-anchor="middle" font-family="IM Fell English SC, serif" font-size="9" fill="#bd93f9" letter-spacing="2">N</text>
    </g>
    <g class="gulls" stroke="#f8f8f2" stroke-width="1.2" fill="none" stroke-linecap="round" opacity="0.55">
      <g class="gull" transform="translate(420 95)">
        <path d="M-6 0 Q-3 -4 0 0 Q3 -4 6 0"/>
      </g>
      <g class="gull gull-2" transform="translate(720 75)">
        <path d="M-5 0 Q-2.5 -3.5 0 0 Q2.5 -3.5 5 0"/>
      </g>
      <g class="gull" transform="translate(820 145)" style="animation-delay: -7s">
        <path d="M-4 0 Q-2 -3 0 0 Q2 -3 4 0"/>
      </g>
    </g>
    <rect y="360" width="1200" height="180" fill="url(#sea)"/>
    <g class="beam-glint" opacity="0.55">
      <ellipse cx="115" cy="385" rx="100" ry="10" fill="#8be9fd" opacity="0.12"/>
    </g>
    <g class="ripples" opacity="0.6">
      <g class="ripple">
        <rect x="-60" y="372" width="1320" height="14" fill="url(#ripples)"/>
      </g>
      <g class="ripple" style="animation-delay: -3s; animation-duration: 14s">
        <rect x="-60" y="395" width="1320" height="14" fill="url(#ripples)" opacity="0.7"/>
      </g>
      <g class="ripple" style="animation-direction: reverse; animation-duration: 17s">
        <rect x="-60" y="425" width="1320" height="14" fill="url(#ripples)" opacity="0.5"/>
      </g>
      <g class="ripple" style="animation-delay: -5s; animation-duration: 19s">
        <rect x="-60" y="465" width="1320" height="14" fill="url(#ripples)" opacity="0.35"/>
      </g>
    </g>
    <g class="distant-ship" opacity="0.45">
      <line x1="850" y1="368" x2="850" y2="352" stroke="#6272a4" stroke-width="0.8"/>
      <path d="M845 368 L855 368 L853 372 L847 372 Z" fill="#6272a4"/>
      <path d="M850 354 L856 366 L850 366 Z" fill="#6272a4"/>
    </g>
    <a href="https://chris-peterson.github.io/tack/#/" xlink:href="https://chris-peterson.github.io/tack/#/" class="plugin-link tack-link">
      <title>tack — route-aware work tracker</title>
      <rect x="160" y="200" width="180" height="265" fill="transparent" pointer-events="all"/>
      <g class="ship" transform="translate(-350 0)">
        <path d="M518 348 L535 368 L665 368 L682 348 Z" fill="#21222c"/>
        <path d="M518 348 L535 368 L665 368 L682 348 Z" fill="none" stroke="#6272a4" stroke-width="0.8"/>
        <line x1="525" y1="354" x2="675" y2="354" stroke="#6272a4" stroke-width="0.4" opacity="0.7"/>
        <rect x="540" y="343" width="6" height="6" fill="#f1fa8c" opacity="0.7"/>
        <rect x="555" y="343" width="6" height="6" fill="#f1fa8c" opacity="0.5"/>
        <line x1="600" y1="348" x2="600" y2="218" stroke="#bd93f9" stroke-width="2"/>
        <line x1="555" y1="240" x2="645" y2="240" stroke="#bd93f9" stroke-width="1.4"/>
        <line x1="600" y1="218" x2="540" y2="320" stroke="#6272a4" stroke-width="0.5" opacity="0.7"/>
        <line x1="600" y1="218" x2="660" y2="320" stroke="#6272a4" stroke-width="0.5" opacity="0.7"/>
        <line x1="600" y1="240" x2="555" y2="320" stroke="#6272a4" stroke-width="0.4" opacity="0.5"/>
        <line x1="600" y1="240" x2="645" y2="320" stroke="#6272a4" stroke-width="0.4" opacity="0.5"/>
        <path d="M600 245 Q564 285 562 338 L600 338 Z" fill="#f8f8f2" opacity="0.92"/>
        <path d="M600 245 Q562 285 562 338 L562 338" fill="none" stroke="#bd93f9" stroke-width="0.6" opacity="0.6"/>
        <path d="M600 245 Q636 282 632 338 L600 338 Z" fill="#ff79c6" opacity="0.88"/>
        <path d="M600 260 Q620 280 620 320" fill="none" stroke="#f8f8f2" stroke-width="0.5" opacity="0.4"/>
        <path d="M600 232 L548 326 L600 326 Z" fill="#f8f8f2" opacity="0.85"/>
        <path d="M600 232 L548 326" fill="none" stroke="#bd93f9" stroke-width="0.6" opacity="0.6"/>
        <line x1="600" y1="218" x2="600" y2="206" stroke="#bd93f9" stroke-width="0.8"/>
        <path d="M600 206 L622 211 L616 215 L622 219 L600 214 Z" fill="#50fa7b"/>
        <path d="M512 364 Q525 370 538 364" fill="none" stroke="#8be9fd" stroke-width="0.8" opacity="0.6"/>
        <path d="M662 364 Q678 372 692 364" fill="none" stroke="#8be9fd" stroke-width="0.8" opacity="0.6"/>
        <text x="600" y="450" class="plugin-label" text-anchor="middle">TACK</text>
        <line x1="572" y1="458" x2="628" y2="458" class="underline"/>
      </g>
    </a>
    <a href="https://chris-peterson.github.io/beacon/#/" xlink:href="https://chris-peterson.github.io/beacon/#/" class="plugin-link beacon-link">
      <title>beacon — at-a-glance session awareness</title>
      <rect x="470" y="115" width="260" height="350" fill="transparent" pointer-events="all"/>
      <g transform="translate(-385 0)">
        <path d="M880 360 Q910 320 945 312 Q985 304 1020 312 Q1060 320 1090 360 Z" fill="#15161e"/>
        <path d="M895 350 Q920 332 945 326" fill="none" stroke="#44475a" stroke-width="0.6" opacity="0.7"/>
        <path d="M1010 322 Q1050 332 1075 350" fill="none" stroke="#44475a" stroke-width="0.6" opacity="0.7"/>
        <polygon points="970,312 1000,312 1006,170 964,170" fill="#f8f8f2"/>
        <rect x="965" y="200" width="40" height="14" fill="#ff5555"/>
        <rect x="965" y="240" width="41" height="14" fill="#ff5555"/>
        <rect x="965" y="280" width="42" height="14" fill="#ff5555"/>
        <line x1="964" y1="312" x2="1006" y2="312" stroke="#6272a4" stroke-width="0.6"/>
        <rect x="960" y="166" width="50" height="6" fill="#6272a4"/>
        <rect x="966" y="148" width="38" height="20" fill="#21222c" stroke="#6272a4" stroke-width="0.6"/>
        <line x1="975" y1="148" x2="975" y2="168" stroke="#6272a4" stroke-width="0.4"/>
        <line x1="985" y1="148" x2="985" y2="168" stroke="#6272a4" stroke-width="0.4"/>
        <line x1="995" y1="148" x2="995" y2="168" stroke="#6272a4" stroke-width="0.4"/>
        <circle cx="985" cy="158" r="6" fill="#8be9fd" filter="url(#soft-glow)"/>
        <path d="M962 148 L985 128 L1008 148 Z" fill="#ff79c6"/>
        <path d="M962 148 L985 128 L1008 148 Z" fill="none" stroke="#bd93f9" stroke-width="0.5" opacity="0.7"/>
        <line x1="985" y1="128" x2="985" y2="116" stroke="#bd93f9" stroke-width="1.2"/>
        <circle cx="985" cy="115" r="2" fill="#f1fa8c"/>
        <text x="985" y="450" class="plugin-label" text-anchor="middle">BEACON</text>
        <line x1="958" y1="458" x2="1012" y2="458" class="underline"/>
      </g>
      <g class="lighthouse-beam">
        <path d="M600 158 L150 290 L80 480 Z" fill="url(#beam)"/>
      </g>
    </a>
    <a href="https://github.com/chris-peterson/logbook" xlink:href="https://github.com/chris-peterson/logbook" class="plugin-link logbook-link">
      <title>logbook — retrospective capture</title>
      <rect x="942" y="278" width="120" height="190" fill="transparent" pointer-events="all"/>
      <g>
        <g transform="translate(958 282)">
          <rect x="0" y="0" width="84" height="112" rx="3" fill="#f8f8f2" stroke="#f8f8f2" stroke-width="2.6" stroke-linejoin="round"/>
          <g stroke="#ffb86c" stroke-width="3" fill="none" stroke-linecap="round">
            <ellipse cx="0" cy="9"   rx="4.4" ry="6"/>
            <ellipse cx="0" cy="23"  rx="4.4" ry="6"/>
            <ellipse cx="0" cy="37"  rx="4.4" ry="6"/>
            <ellipse cx="0" cy="51"  rx="4.4" ry="6"/>
            <ellipse cx="0" cy="65"  rx="4.4" ry="6"/>
            <ellipse cx="0" cy="79"  rx="4.4" ry="6"/>
            <ellipse cx="0" cy="93"  rx="4.4" ry="6"/>
            <ellipse cx="0" cy="104" rx="4.4" ry="6"/>
          </g>
        </g>
        <text x="1000" y="450" class="plugin-label" text-anchor="middle">LOGBOOK</text>
        <line x1="968" y1="458" x2="1032" y2="458" class="underline"/>
      </g>
    </a>
    <g class="anchor-decor" opacity="0.4">
      <g transform="translate(1130 490)">
        <circle r="3" fill="none" stroke="#6272a4" stroke-width="0.8"/>
        <line x1="0" y1="3" x2="0" y2="20" stroke="#6272a4" stroke-width="0.8"/>
        <line x1="-8" y1="14" x2="8" y2="14" stroke="#6272a4" stroke-width="0.8"/>
        <path d="M-12 20 Q-8 26 0 22" fill="none" stroke="#6272a4" stroke-width="0.8"/>
        <path d="M12 20 Q8 26 0 22" fill="none" stroke="#6272a4" stroke-width="0.8"/>
      </g>
    </g>
    <rect x="0" y="0" width="1200" height="540" fill="url(#sky)" opacity="0" pointer-events="none"/>
  </svg>
</div>

<p class="harbor-tagline"><strong>AI-assisted development is uncharted water.</strong> These plugins are the instruments that keep you oriented: a <em>tack</em> sets the heading, a <em>beacon</em> signals what's underway, and the <em>logbook</em> charts lessons from prior voyages — <em>thar be dragons</em>.</p>

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

## Catalog

| Plugin | Category | What it does |
|---|---|---|
| [beacon](https://chris-peterson.github.io/beacon/#/) | development | At-a-glance session awareness for Claude Code in iTerm2 |
| [ClaudeWatch](https://chris-peterson.github.io/ClaudeWatch/#/) | security | `PreToolUse` hook that enforces command safety rules via `claude-watches` |
| [logbook](https://github.com/chris-peterson/logbook) | development | Capture, sanitize, and publish AI-coding-session retrospectives to a team-owned git repo |
| [tack](https://chris-peterson.github.io/tack/#/) | productivity | Route-aware work tracker — pivots, deliverables, and dependencies across session boundaries |

See [How they fit together](/relationships) for the workflow roles each plugin plays and how they interact.
