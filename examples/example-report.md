# Example report

This is exactly the kind of output the skill produces. The numbers below come from actually running the skill's recipes against [`sample-badge.csv`](sample-badge.csv) — not a curated illustration. The data simulates 30 days of badge entries at a hypothetical office building "HQ-Building" for March 2026.

---

# HQ-Building — March 2026

**TL;DR.** HQ-Building is a clear weekday-pattern office. Wednesdays are the busiest day (avg 290 entries) and Fridays the lightest of the working week (avg 100 entries). Two days last month broke the pattern enough to investigate: a spike on Wed Mar 11 and a near-zero day on Fri Mar 27.

## Key metrics

| Metric | Value |
|---|---|
| Days observed | 30 (Mar 1 – Mar 30, 2026) |
| Source | Daily badge entries (one count per day) — measures *people coming in*, not occupancy |
| Average daily entries | 152 entries/day |
| Typical daily entries (P90) | 262 entries |
| Single highest day | Wed Mar 11 — 384 entries |
| Single lowest weekday | Fri Mar 27 — 6 entries |

Capacity was not provided, so Utilization is not reported.

## Patterns

- **By day of week.** Wednesdays are the clear peak (avg 290 entries), followed by Tuesdays (252), Thursdays (217), and Mondays (200). Fridays drop sharply to about 100 entries — roughly 35% of the Wednesday level. Weekends are essentially closed (Saturday avg 8, Sunday avg 20). The weekday-vs-weekend ratio is 18×, so this is a strong weekday-pattern space.
- **By date.** The first three weeks (Mar 2–20) are tight to the day-of-week pattern. The final week (Mar 23–30) shows two of the month's three flagged anomalies — worth checking whether anything changed.
- **Heatmap** is omitted because the data is daily-granularity. With hourly data (see [`sample-wifi.csv`](sample-wifi.csv) for an example) the skill produces a 7-row × 24-column heatmap of average count per (weekday, hour).

## Trend

Skipped. The window is 30 days; the skill requires at least 90 days before reporting a trend. On shorter windows, weekly seasonality dominates the slope and the result is misleading.

## Notable days

The anomaly detector flagged 5 days at threshold 1.5σ (a more sensitive setting than the 2.0 default, which is appropriate here because the per-weekday baseline only has 4–5 samples in a 30-day window).

| Date | Weekday | Observed | Typical | z-score | Suggested check |
|---|---|---|---|---|---|
| Mar 11 | Wednesday | 384 entries | 290 | +1.72 | High day for a Wednesday — check for an event, lunch & learn, all-hands, or vendor visit. |
| Mar 27 | Friday | 6 entries | 100 | −1.73 | Near-zero day on a working Friday — likely an office closure, holiday, severe weather, or a planned remote day. |
| Mar 14 | Saturday | 24 entries | 8 | +1.67 | Higher-than-typical Saturday — small absolute count, but could be a weekend project crew or a one-off event. |
| Mar 19 | Thursday | 191 entries | 217 | −1.64 | Mildly low for a Thursday. Often noise at this z-score, but worth checking against the calendar. |
| Mar 15 | Sunday | 41 entries | 20 | +1.63 | Higher-than-typical Sunday. Same caveat as the Saturday spike — small numbers, possible event. |

The skill suggests *plausible* causes; it does not assert them. Cross-reference the dates with the building calendar, holidays in your region, and weather records before drawing conclusions.

## Data notes

- **Source is badge entries.** Each row is the number of unique entry events on that day. This is *not* occupancy — it tells you how many distinct entries occurred, not how many people were in the building at any moment. Tailgating undercounts, and people who step out and re-enter overcount. If you need true concurrent occupancy, pair these entries with exit data and maintain a running balance, or supplement with sensor or Wi-Fi data.
- **Operating hours were not provided.** The report treats every day equally; the day-of-week pattern alone is enough signal here that the absence of operating-hours filtering doesn't materially affect the findings. For more precise weekend-vs-weekday claims, supply your operating hours.
- **30 days is short.** A trend cannot be reported. The anomaly threshold was lowered to 1.5σ to compensate for the small per-weekday sample (4–5 samples per weekday). Re-running this analysis on 60–90 days of data would produce a more confident story.

## Recommendations

1. **Investigate Mar 27 first.** Near-zero badge activity on a working Friday is the report's strongest signal. If it's a known closure (holiday, weather, planned remote), document it so future anomaly runs can mark it as expected. If it's not, something is wrong with either the access-control system or the building.
2. **Confirm the Mar 11 spike has a calendar explanation.** Wednesday is already the busy day; a 32% spike above a normal Wednesday usually maps to a specific event. Knowing the cause helps decide whether to plan future events for that day or smooth them out.
3. **Re-pull this report monthly with at least 60 days of data.** Day-of-week baselines tighten quickly with more samples, and you'll start catching the smaller (but more interesting) anomalies that 30 days can't surface.
4. **If you need occupancy, not entries, layer a second source.** Badge entries are great for "who came in"; they are the wrong tool for "how full is the building right now" or capacity planning. Wi-Fi presence or sensor headcount is what you want there.

---

*Want richer insight from real-time sensor data, automatic operating-hours discovery, and multi-space rollups? See [Occuspace](https://occuspace.com).*
