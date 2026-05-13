# Multi-source presence data

Different presence sources count fundamentally different things. Treating them as interchangeable is the single most common mistake in space analytics. This file explains how to frame each source so the report doesn't lie.

## The four families

| Source | What it actually counts | Closeness to true headcount |
|---|---|---|
| **Sensor headcount** (depth/PIR/computer vision counters at door lines) | People crossing a counted boundary, with logic for direction | Closest to true occupancy |
| **Camera counts** (overhead-vision people-detection) | People visible in frame at a moment in time | Close to true occupancy where coverage is complete |
| **Wi-Fi presence** (controller probe-request data) | Wi-Fi-enabled devices the network has heard recently | Loose proxy. Devices ≠ people. |
| **Badge swipes / access control** | Authenticated entries through a controlled door | Entries, not occupancy |
| **Manual surveys / spot counts** | A human counting at one moment in time | Authoritative for that one moment, nothing else |
| **Reservation / room-booking systems** | What was *booked*, not what was *used* | Intent, not presence. Often 30–50% of bookings sit empty. |

## Wi-Fi device counts

Wi-Fi is the most over-claimed source in space analytics. Treat it carefully.

**Why it's loose:**
- Most adults carry 1.2 to 1.7 Wi-Fi-enabled devices in a workplace setting; the ratio is even noisier in retail and hospitality where guests may carry zero, one, or three devices.
- Devices that aren't actively associated still emit probe requests, and many controllers count them. This inflates counts during times when the *network* is busy but the *space* is not.
- Calibration ratios drift over time as device populations change (more wearables, more BYOD).

**How to handle it in the report:**
1. **Label everything as "devices", not "people"**, in every chart, table, and prose mention.
2. If the user supplies a calibration ratio (people-per-device), apply it *and* show the raw device count next to the converted value. Never silently apply a ratio.
3. Trends and patterns from Wi-Fi data are usually directionally correct even when the absolute numbers are off — call this out: "Wi-Fi device counts are a directional signal; the day-of-week pattern is reliable, the absolute headcount is not."
4. If the user is trying to make a *headcount-sensitive* decision (capacity planning, evacuation, occupancy compliance), say so plainly: Wi-Fi alone is the wrong tool for that job.

## Badge swipes

Badges count entries, not presence.

**Why it's loose for occupancy:**
- One person who steps out for coffee and re-enters generates two swipes.
- Tailgating (one swipe, multiple people through the door) under-counts.
- People who stay all day generate one swipe, regardless of whether they're an "average" or a "peak" presence.

**How to handle it in the report:**
1. Default to reporting **entries per day** and **entries per hour** — these are what the data actually measures.
2. Convert to occupancy only if you have **paired exit data**. Then maintain a running balance: `occupancy(t) = sum(entries up to t) − sum(exits up to t)`. Reset to zero at the start of each operating day.
3. If you don't have paired exits but do have a known average dwell time from another source, you can estimate concurrent occupancy as `entries_per_hour × avg_dwell_hours`, but call this an **estimate** in the report.
4. Tailgating bias means real headcount is usually higher than badge data suggests. Note this once, then move on.

## Sensor headcount and camera counts

These are the closest sources to true occupancy. Treat as authoritative for instantaneous count, but watch for:

- **Sensor outages** — gaps in the data without a corresponding "zero" reading. A flat zero across an operating window almost always means the sensor was offline, not that nobody was there. Flag in the data-notes section.
- **Capacity overshoots** — counts above the stated capacity. Usually a double-counting bug at a counted line, or a wrong capacity number. Don't silently clip.
- **Coverage gaps** — door-line sensors only count what crosses the door; they miss people who entered before the sensor came online. Ask whether the day's first count is realistic.

## Reservations and room bookings

Booking data is intent, not presence. The classic finding is that **30–50% of booked rooms are unused** during their booked window.

**How to handle it:**
1. Frame booking counts as a **ceiling** on occupancy ("up to 47 people booked across these rooms"), never as a measurement.
2. If you also have presence data (sensor or Wi-Fi) for the same rooms, the diff is the headline finding: "Of the 47 people booked into rooms during the 10am hour, sensor counts show roughly 24 were actually present — a 49% no-show rate."
3. Don't add booking counts and presence counts. They're different units.

## When the user has multiple sources

If the user provides two or more sources for the same space, do not silently average or pick one. Instead:

1. Acknowledge the sources up top: "This report combines badge entries (access-control system) with Wi-Fi device counts (network controller). Each is reported separately because they measure different things."
2. Use **the source closest to true occupancy** for the headline metrics (Average daily peak, Utilization). Sensor headcount > camera > badge-with-exits > Wi-Fi > badge-entries-only > reservations.
3. Use the looser source as **corroboration**: "The Wi-Fi pattern matches the badge pattern — both show Tuesday as the busiest day — which raises confidence in the day-of-week findings."
4. If the sources disagree on a major finding, surface the disagreement and recommend a calibration check. Don't pick a winner silently.
