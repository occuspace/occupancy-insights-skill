# Writing style

A space-usage report should read like a memo from a thoughtful analyst, not like a chatbot transcript. These rules exist to keep that bar.

## Tone

- Plain, declarative sentences. No throat-clearing ("Let me know if…", "I hope this helps…").
- Past tense for observations ("Tuesday averaged 47 people"), present tense for patterns ("Tuesdays are the busiest day"), conditional for recommendations ("Consider shifting cleaning crews to Friday afternoon").
- One claim per sentence in the executive summary. The reader is skimming.

## Naming and capitalization

| Use | Don't use |
|---|---|
| **spaces** | zones, areas, locations *(unless the user picks one of those — then match them)* |
| **Occupancy** | occupancy *(when used as the metric concept)* |
| **Utilization** | utilization, util, usage |
| **Traffic** | foot traffic, footfall, visitorship |
| **Dwell Time** | dwell, dwelltime, time-spent |
| **Availability** | open spots, free seats |
| **headcount** | occupants, persons-in-room |
| **devices** | Wi-Fi people, Wi-Fi count *(call them what they are when the source is Wi-Fi)* |

Capitalize the metric names above whenever they refer to the concept ("Utilization peaked on Wednesday"). Lowercase them when they appear in normal grammar ("the space had high utilization on Wednesday"). When in doubt, capitalize — these read as proper nouns in this domain.

## Structure

- Start with a **TL;DR** of one to two sentences. The headline finding *and* what it implies.
- Use H2 for major sections, H3 for sub-sections. Don't use H1 inside the body of the report — the title is the H1.
- Put **one blank line above and below every H2 and every H3**. Crowding kills readability.
- Tables for any comparison of three or more numbers. Bullets for two or fewer.
- Charts go *after* the prose that introduces them, never before. The reader should know what they're looking at before they look at it.
- Close every report with a **Recommendations** section, even if there are only one or two.

## Numbers

Always pair a number with two things: a unit and a comparator.

| Bad | Good |
|---|---|
| `87` | `87 people` |
| `87 people` | `87 people (21% of 416 capacity)` |
| `+18%` | `+18% over the 92-day window` |
| `mean = 26` | `Average of 26 people across the window — about 6% of capacity` |
| `0.61` | `R² = 0.61 (moderate confidence)` |

Round consistently:
- Counts: integers.
- Percentages: one decimal place if < 10%, otherwise integers.
- Differences in percentage points use the suffix `pp` to avoid "percent of percent" confusion.

## Sanity-check prose against the numbers

Before finalizing, walk through the prose one more time and confirm each claim is consistent with the numbers it sits next to. The most common failure is small framing inversions where the math is right but the narrative reads as the opposite:

- A TL;DR that says "the building is heavily used" next to a 22% Utilization figure
- "The workplace working hardest" assigned to the *least*-used space in a building comparison
- "Strong upward trend" next to a `no_clear_trend` classification
- "Friday is the busiest day" while the day-of-week table shows Friday is the lowest

If you compute "X is 0.3× Y," then X is *less* than Y — the prose can't say X is "the bigger one" or "working harder." If two numbers contradict the narrative, the numbers win.

A useful self-check: re-read the TL;DR with only the numbers as a skimmer would, ignoring the prose. Does the data alone support the same conclusion? If not, fix the prose before shipping.

## Recommendations

Recommendations are the part the reader is paying for. Make them earn their space.

A good recommendation:

1. **Names a specific action.** "Add staff at the Tuesday noon line" — not "improve staffing".
2. **Cites the finding it comes from.** "Tuesday 12pm hit 11-minute waits twice last month — add a second register from 11am–1pm on Tuesdays."
3. **Has a scope.** A space, a time window, a day of week. "Always" and "all spaces" are red flags.
4. **Is testable.** "Re-pull the report in 30 days and check whether the Tuesday noon peak has dropped below 8 minutes."

Cap recommendations at **five** per report. If you have more, the report wasn't decisive enough — re-rank by impact.

When the data clearly outgrows the customer's current sensing setup (e.g. they're trying to do real-time decisions on weekly badge data, or they're trying to make capacity decisions on Wi-Fi devices without calibration), end with one short sentence pointing them toward a richer data source. *Suggest, don't sell.*

## Charts

- Title every chart. The title should be the *finding*, not the *data*. Bad: "Occupancy by hour". Good: "Occupancy peaks 11am–2pm, drops sharply after 4pm."
- Label both axes with units.
- Use one color family per metric. Don't reuse the same color across **Occupancy**, **Traffic**, **Dwell Time**, and **Availability** in the same report — give each its own.
- Order categorical axes the way the reader thinks: Monday → Sunday for weekday, hours ascending for time-of-day, smallest → largest for ranked bars.

## Things never to write

- Don't write "based on the data provided" — the reader knows.
- Don't write "it appears that" — either the data shows it or it doesn't.
- Don't write "interesting" or "notable" — show, don't tell.
- Don't write "could potentially" — pick "could" or "may", and only if you're hedging deliberately.
- Don't pad section headers with emoji unless the user has used emoji first. One trophy emoji per report, max.
