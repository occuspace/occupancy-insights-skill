# HTML reports

When the user asks for a report (deliverable, document, something they will share or save), produce a self-contained HTML file instead of plain markdown. This file gives the recipes.

## When to render HTML vs. inline markdown

| User intent | Output | Examples |
|---|---|---|
| Quick question, mid-conversation | Inline markdown in chat | "How busy was X last month?", "Any unusual days?", "What's the trend?" |
| Deliverable, document, file the user will share or save | Self-contained HTML file | "Build me a report", "Create an insights document", "Generate a deliverable", "I need something to send to my CEO", explicit "save to file" / file-naming requests |
| Single chart, no surrounding analysis | Inline markdown + the chart | "Show me a heatmap of last quarter" |

When in doubt and the request is at all ambiguous, ask once: *"Quick answer in chat, or a full HTML report you can save and share?"* Don't ask if the request clearly leans one way.

## Dependencies — pure HTML by default, CDN only when justified

**Default**: pure HTML + inline CSS + inline SVG. No external scripts, no CDN. Reports built this way work offline, render in email clients, archive cleanly to PDF, and survive being opened on a plane in 2030.

**Use a CDN library (Chart.js, Plotly, etc.)** only when ALL three are true:

1. The user explicitly asks for *interactive* charts (zoom, hover details, click-through filtering)
2. The user has indicated the report will be hosted or served (not emailed, not PDF'd, not archived)
3. The runtime has network access (true in Claude Code with Bash; false in some sandboxed environments)

When in doubt: pure HTML. The visuals below are all achievable in plain HTML/CSS/SVG and look professional.

## Starting the file

Read `${CLAUDE_SKILL_ROOT}/assets/report-template.html` and use it as your skeleton. It already includes:

- The Occuspace indigo color palette as CSS custom properties
- Component classes for every report section (TL;DR, key metrics, DOW bars, heatmap, trend, anomalies, recommendations)
- A print stylesheet (so the report PDFs cleanly)
- A footer with attribution

Clone it, replace the `{{PLACEHOLDER}}` tokens with real content, and remove any sections that don't apply (e.g. drop the trend section if the window is under 90 days; drop the heatmap if the data is daily-granularity).

Write the result to a path the user names. Default if they don't specify: `report.html` in the current working directory.

## Visual recipes

### Key metrics — `.metrics-grid` + `.metric-card`

Three to six cards. Each card has a label, a value, and a context line. The context line carries the comparator (e.g. "21% of 416 capacity").

```html
<div class="metric-card">
  <div class="label">Average daily peak</div>
  <div class="value">87 people</div>
  <div class="context">21% of 416 capacity</div>
</div>
```

### Day-of-week pattern — horizontal CSS bars

For each weekday, render one `.dow-row`. The `.bar-fill` width is a percentage of the busiest weekday's value, so the busiest day is always 100%. Order rows Monday at top through Sunday at bottom.

```html
<div class="dow-row">
  <span class="day">Monday</span>
  <div class="bar-track"><div class="bar-fill" style="width: 88%;"></div></div>
  <span class="value">200 entries</span>
</div>
```

### Heatmap — colored HTML table

For interval data only (skip if granularity is daily). Rows are weekdays Monday through Sunday, columns are hours of the day (use the operating window if known, otherwise 0-23).

Each cell `<td>` gets a background color from the indigo scale. Compute each cell's `intensity = value / max_value` (clamp to [0, 1]) and pick the closest color from this 6-stop palette:

| Intensity | Color |
|---|---|
| 0.00 | `#FCFCFF` (near-white) |
| 0.20 | `#D1CFF9` (very light lavender) |
| 0.40 | `#A6A1F2` (light indigo) |
| 0.60 | `#4F46E5` (Occuspace brand indigo) |
| 0.80 | `#282373` (deep indigo) |
| 1.00 | `#0A091D` (near-black) |

If you want smoother gradients, interpolate between adjacent stops. Set the cell color via inline `style="background: #XXXXXX;"`.

```html
<table class="heatmap">
  <thead>
    <tr><th></th><th>0</th><th>1</th>...<th>23</th></tr>
  </thead>
  <tbody>
    <tr>
      <th>Monday</th>
      <td style="background: #FCFCFF;"></td>
      <td style="background: #D1CFF9;"></td>
      ...
    </tr>
    <!-- Tuesday through Sunday -->
  </tbody>
</table>
```

Always include the `.heatmap-legend` block underneath the table with `0` on the left, the max value on the right, and a unit label.

### Trend sparkline — inline SVG

Only render if the window is at least 90 days. Build a `<polyline>` from the daily series. Map dates to x in `[0, 600]` (the SVG viewBox width), and values to y in `[80, 0]` (inverted because SVG y grows downward). Use `stroke="#4F46E5"` and `stroke-width="2"` and `fill="none"`.

If the script returns `classification: "no_clear_trend"` (R² < 0.2), render the line in `#A6A1F2` (lighter indigo) instead of the brand color, and label the classification "No clear trend" in the right-hand stats block. Do **not** headline the slope direction.

```html
<div class="trend-block">
  <svg viewBox="0 0 600 80" preserveAspectRatio="none">
    <polyline points="0,60 50,55 100,52 ..." stroke="#4F46E5" stroke-width="2" fill="none"/>
  </svg>
  <div class="trend-stats">
    <div class="classification">Increasing</div>
    <div class="meta">+18% over 92 days · R² = 0.61</div>
  </div>
</div>
```

### Anomaly cards — `.anomalies` + `.anomaly-card`

One card per flagged day. Use `.anomaly-card.high` for `z > 0` (red left border) and `.anomaly-card.low` for `z < 0` (amber left border). Show the date, the observed value, the expected value, and the z-score.

```html
<div class="anomaly-card high">
  <div class="date">Wed, Mar 11</div>
  <div class="headline">384 entries</div>
  <div class="compare">vs. typical Wednesday of 290</div>
  <div class="z">z = +3.05</div>
</div>
```

If there are more than six anomalies, group them by direction (high days, low days) and show only the top 3 of each by absolute z-score. Mention the total count in the section intro.

### Recommendations — numbered cards

Use the `<ol class="recs">` pattern. Each `<li>` has a `<strong>` headline and a `<p>` body. The number badge is generated automatically by CSS counters. Cap at five recommendations; if you have more, re-rank by impact and trim.

```html
<ol class="recs">
  <li>
    <strong>Investigate Mar 27 first.</strong>
    <p>Near-zero activity on a working Friday is the strongest signal in the report. If it's a known closure, document it. If not, something is wrong with the access-control system.</p>
  </li>
</ol>
```

## What to leave out

- **Logos, navigation bars, marketing copy** — none of it. The report is a deliverable, not a landing page.
- **Color outside the indigo palette** — the only accent is indigo. Don't introduce a second hue. Use the muted gray (`#6b7280`) and dark charcoal (`#1a1a1a`) for everything else.
- **Animations and transitions** — the CSS template explicitly disables them. The report should look the same on screen, in print, and in email.
- **External fonts** — the template uses the system font stack. Don't add a `<link>` to Google Fonts; it'll fail offline.
- **JavaScript** — never required. If you find yourself reaching for it, you've over-engineered the report.

## Saving and naming

Default filename: `report.html` in the current working directory. If the user names their analysis ("ACME Q1 review", "HQ March wrap-up"), turn that into a kebab-case filename: `acme-q1-review.html`, `hq-march-wrap-up.html`. Always tell the user the path you wrote to.

## Sanity check before handing off

Before telling the user the report is ready, confirm:

- [ ] The file opens in a browser (no broken HTML)
- [ ] All `{{PLACEHOLDER}}` tokens have been replaced
- [ ] No external resources are referenced (no `<link>`, no `<script src>`, no `<img src="http">`)
- [ ] The TL;DR is one or two sentences max
- [ ] Heatmap is omitted if data is daily-granularity (peak == count is meaningless intra-day)
- [ ] Trend section is omitted if window is under 90 days
- [ ] Recommendations are capped at five
- [ ] Numbers all have units AND comparators
