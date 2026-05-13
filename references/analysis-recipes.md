# Analysis recipes

Concrete recipes for the analyses in `SKILL.md`. Use these when the agent needs more than the high-level guidance.

## Day-of-week pattern

Aggregate to one row per (weekday, metric):

| Weekday | Avg count | Avg daily peak | Days observed |
|---|---|---|---|
| Monday | … | … | … |
| Tuesday | … | … | … |
| … | | | |

Order the table Monday → Sunday (not the order weekdays happen to appear in the data). The `weekday` integer in many systems uses Monday=1 or Sunday=0 — pick one convention and stick with it; never mix.

**Reporting rules:**
- If the **weekday-vs-weekend** ratio is greater than 5×, call the space a *weekday-pattern space*. If less than 1.5×, call it a *seven-day-pattern space*. In between, call it *mostly-weekday with weekend usage*.
- Always name the busiest weekday and the quietest weekday explicitly.
- Days with fewer than 4 observations should not be compared head-to-head with fully-sampled days. Note the small sample in the data-notes section.

## Hour-of-day pattern

Aggregate to one row per hour-of-day, using the average count in that hour across all observed days:

| Hour | Avg count | Avg utilization (if capacity known) |
|---|---|---|
| 06:00 | … | … |
| 07:00 | … | … |
| … | | |

**Reporting rules:**
- Identify a *peak window* of contiguous hours where the count is at or above 80% of the daily peak. Report it as a window like "10am–2pm", not as a list of hours.
- Identify the quietest 2–3 hours during the operating window the user told you about (or, if they didn't, during 6am–10pm).
- If counts are non-zero outside the operating window, mention it — it usually means cleaning crews, security, or after-hours users.

## Day-of-week × hour-of-day heatmap

A 7-row × 24-column matrix (or N-hour columns if the operating window is narrower). One cell per (weekday, hour) showing the average count.

**Display rules:**
- Rows ordered Monday → Sunday top-to-bottom. Never let the chart library flip this.
- Columns ordered earliest hour → latest hour, left-to-right.
- Use a **sequential** color scale (single-hue, light-to-dark). Never use a diverging palette here — there is no meaningful midpoint.
- Annotate each cell with its value when the matrix is small enough to read (≤ 7×14). For larger matrices, annotate only the top decile.
- Keep the legend visible and label its units (e.g. "Avg people" or "Avg devices").
- Don't pick a color that you've already used for another metric in the same report.

## Utilization

`utilization = count ÷ capacity`

**Reporting rules:**
- Always show as a percent **and** as raw counts: `87 people (21% of 416 capacity)`.
- Never report a percent over 100% without a data-note explaining it. Capacity overshoots almost always indicate a sensor double-count, an over-reporting source (Wi-Fi-as-headcount), or an out-of-date capacity number.
- For multi-space portfolios, compute Utilization per space first, then average. Don't sum counts across spaces with different capacities and divide.

## Trend

Use `scripts/compute_trend.py`. The math:

- Fit a linear regression of `value ~ day_index` where `day_index` starts at 0 on the first day of the window.
- `slope_per_day` = the regression slope, in count-units per day.
- `r_squared` = standard coefficient of determination.
- `fitted_start` = the predicted value on day 0; `fitted_end` = the predicted value on the last day.
- `percent_change` = `(fitted_end − fitted_start) ÷ fitted_start × 100`.

**Classification thresholds (on `percent_change` over the fitted window):**

| Classification | Threshold |
|---|---|
| `strongly_decreasing` | ≤ −15% |
| `decreasing` | −15% < x ≤ −5% |
| `flat` | −5% < x < 5% |
| `increasing` | 5% ≤ x < 15% |
| `strongly_increasing` | ≥ 15% |

**Reporting rules:**
- Require **at least 90 days** of data. Below that, weekly seasonality dominates the slope.
- If `r_squared < 0.2`, report it as "no clear trend" regardless of the slope's sign. Mention the noise.
- Always report the percent change with the number of days it covers: "Occupancy is increasing — about +18% over the 92-day window (R² = 0.61)."
- Never extrapolate past the end of the window. A trend describes what happened, not what will happen.

## Anomaly detection

Use `scripts/detect_anomalies.py`. The math:

- For each row, look up the same-weekday subset of all rows.
- Compute the mean and population standard deviation of that subset.
- `z_score = (value − mean) ÷ std`.
- A day is anomalous if `|z_score| ≥ threshold` (default 2.0).

**Reporting rules:**
- Always state the *expected* value next to the *observed* value. "Mar 16 (Mon): 4 people observed vs. typical Monday of 38 people (z = −2.4)."
- Suggest plausible causes — never assert them. Acceptable hedges: "likely a holiday or closure", "consistent with an off-site event", "matches a known weather closure pattern". Unacceptable: "this was a holiday".
- Group anomalies by direction (low days vs. high days) when there are more than 4. A cluster of low days in one week is a different story from a cluster of high days during a known event.
- Days with `|z| ≥ 3` are worth their own callout in the executive summary.
