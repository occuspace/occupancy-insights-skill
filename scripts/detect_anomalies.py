#!/usr/bin/env python3
"""Flag unusual days against a same-day-of-week baseline.

Reads a CSV with a date column and a numeric value column (one row per day,
or aggregated to one row per day from finer-grained data). For each day,
computes a z-score against the mean and population standard deviation of all
days that share the same weekday. Returns the days whose absolute z-score is
at or above a threshold (default 2.0).

Suggests a *direction* (high or low) and the rough magnitude. Never asserts a
cause — leave that to the user and the report writer.

Usage:
    python3 detect_anomalies.py path/to/daily.csv \
        --date-col date --value-col value --threshold 2.0

Stdlib only — no numpy or pandas required.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import defaultdict
from datetime import datetime


WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("csv_path", help="Path to the input CSV.")
    p.add_argument("--date-col", default="date", help="Name of the date column.")
    p.add_argument("--value-col", default="value", help="Name of the numeric value column.")
    p.add_argument(
        "--threshold",
        type=float,
        default=2.0,
        help="Absolute z-score threshold for flagging a day (default 2.0).",
    )
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
                d = parse_date(raw_date, fmt)
                v = float(raw_val)
            except (ValueError, TypeError):
                continue
            by_day[d.date().isoformat()].append(v)

    out = []
    for d_str, vals in by_day.items():
        avg = sum(vals) / len(vals)
        d = datetime.fromisoformat(d_str)
        out.append((d, avg))
    out.sort(key=lambda r: r[0])
    return out


def population_stdev(values: list[float], mean: float) -> float:
    if not values:
        return 0.0
    return math.sqrt(sum((v - mean) ** 2 for v in values) / len(values))


def main() -> int:
    args = parse_args()
    try:
        series = read_daily_series(args.csv_path, args.date_col, args.value_col, args.date_format)
    except (FileNotFoundError, ValueError) as exc:
        print(json.dumps({"ok": False, "reason": str(exc)}))
        return 1

    if not series:
        print(json.dumps({"ok": False, "reason": "No usable rows found."}))
        return 0

    by_weekday: dict[int, list[float]] = defaultdict(list)
    for d, v in series:
        by_weekday[d.weekday()].append(v)

    baselines = {}
    for wd, vals in by_weekday.items():
        mean = sum(vals) / len(vals)
        std = population_stdev(vals, mean)
        baselines[wd] = (mean, std, len(vals))

    flagged = []
    for d, v in series:
        wd = d.weekday()
        mean, std, n_observations = baselines[wd]
        if std == 0 or n_observations < 3:
            continue
        z = (v - mean) / std
        if abs(z) < args.threshold:
            continue
        flagged.append(
            {
                "date": d.date().isoformat(),
                "weekday": WEEKDAY_NAMES[wd],
                "observed": round(v, 2),
                "expected": round(mean, 2),
                "z_score": round(z, 2),
                "direction": "high" if z > 0 else "low",
                "baseline_sample_size": n_observations,
            }
        )

    flagged.sort(key=lambda r: abs(r["z_score"]), reverse=True)
    output = {
        "ok": True,
        "days_analyzed": len(series),
        "threshold": args.threshold,
        "flagged_count": len(flagged),
        "flagged": flagged,
    }
    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
