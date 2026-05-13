#!/usr/bin/env python3
"""Compute a daily-occupancy trend with linear regression.

Reads a CSV with at least two columns: a date and a numeric value (one row per day).
Outputs a JSON object describing the slope, R-squared, fitted endpoints, and a
classification bucket.

Refuses to compute a trend on fewer than 90 days of data because day-of-week
seasonality dominates shorter windows.

Usage:
    python3 compute_trend.py path/to/daily.csv \
        --date-col date --value-col value

The CSV may have either:
    - one row per day (preferred), or
    - multiple rows per day, in which case the script aggregates by mean per date.

Stdlib only — no numpy or pandas required.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime
from collections import defaultdict


CLASSIFICATION_THRESHOLDS = (
    (-15.0, "strongly_decreasing"),
    (-5.0, "decreasing"),
    (5.0, "flat"),
    (15.0, "increasing"),
    (float("inf"), "strongly_increasing"),
)

MIN_DAYS = 90


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("csv_path", help="Path to the input CSV.")
    p.add_argument("--date-col", default="date", help="Name of the date column.")
    p.add_argument("--value-col", default="value", help="Name of the numeric value column.")
    p.add_argument(
        "--date-format",
        default=None,
        help="Optional strptime format. Defaults to ISO-8601 / common formats.",
    )
    return p.parse_args()


def parse_date(raw: str, fmt: str | None) -> datetime:
    raw = raw.strip()
    if fmt:
        return datetime.strptime(raw, fmt)
    for candidate in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y/%m/%d", "%m/%d/%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(raw, candidate)
        except ValueError:
            continue
    return datetime.fromisoformat(raw)


def read_daily_series(path: str, date_col: str, value_col: str, fmt: str | None):
    by_day: dict[str, list[float]] = defaultdict(list)
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None or date_col not in reader.fieldnames or value_col not in reader.fieldnames:
            raise ValueError(
                f"CSV must contain columns {date_col!r} and {value_col!r}. "
                f"Found: {reader.fieldnames}"
            )
        for row in reader:
            raw_date = row[date_col]
            raw_val = row[value_col]
            if raw_date is None or raw_val is None or raw_val == "":
                continue
            try:
                d = parse_date(raw_date, fmt).date().isoformat()
                v = float(raw_val)
            except (ValueError, TypeError):
                continue
            by_day[d].append(v)
    return sorted((d, sum(vals) / len(vals)) for d, vals in by_day.items())


def linreg(xs: list[float], ys: list[float]) -> tuple[float, float, float]:
    n = len(xs)
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    sxx = sum((x - mean_x) ** 2 for x in xs)
    sxy = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    if sxx == 0:
        return 0.0, mean_y, 0.0
    slope = sxy / sxx
    intercept = mean_y - slope * mean_x
    ss_tot = sum((y - mean_y) ** 2 for y in ys)
    if ss_tot == 0:
        r_squared = 0.0
    else:
        ss_res = sum((y - (intercept + slope * x)) ** 2 for x, y in zip(xs, ys))
        r_squared = max(0.0, 1.0 - ss_res / ss_tot)
    return slope, intercept, r_squared


def classify(percent_change: float) -> str:
    for threshold, label in CLASSIFICATION_THRESHOLDS:
        if percent_change <= threshold:
            return label
    return CLASSIFICATION_THRESHOLDS[-1][1]


def main() -> int:
    args = parse_args()
    try:
        series = read_daily_series(args.csv_path, args.date_col, args.value_col, args.date_format)
    except (FileNotFoundError, ValueError) as exc:
        print(json.dumps({"ok": False, "reason": str(exc)}))
        return 1

    if len(series) < MIN_DAYS:
        print(
            json.dumps(
                {
                    "ok": False,
                    "reason": f"Need at least {MIN_DAYS} days of data; got {len(series)}.",
                    "days": len(series),
                }
            )
        )
        return 0

    xs = [float(i) for i in range(len(series))]
    ys = [v for _, v in series]
    slope, intercept, r_squared = linreg(xs, ys)
    fitted_start = intercept
    fitted_end = intercept + slope * (len(series) - 1)

    if fitted_start == 0:
        percent_change = 0.0
    else:
        percent_change = (fitted_end - fitted_start) / abs(fitted_start) * 100.0

    low_confidence = r_squared < 0.2
    raw_classification = classify(percent_change)
    # When the fit is too weak to trust, the headline classification must say so —
    # otherwise a model reading just the JSON could lead with a misleading
    # direction. The slope, R², and percent_change stay raw for inspection.
    classification = "no_clear_trend" if low_confidence else raw_classification

    output = {
        "ok": True,
        "days": len(series),
        "first_date": series[0][0],
        "last_date": series[-1][0],
        "slope_per_day": round(slope, 4),
        "r_squared": round(r_squared, 3),
        "percent_change": round(percent_change, 2),
        "fitted_start": round(fitted_start, 2),
        "fitted_end": round(fitted_end, 2),
        "classification": classification,
        "raw_classification": raw_classification,
        "low_confidence": low_confidence,
    }
    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
