"""Audit downloaded ASOS CSV files and merge Seoul station 108."""

import csv
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path


folder = Path(__file__).resolve().parent
files = sorted(folder.glob("OBS_ASOS_TIM_*.csv"))
if not files:
    raise SystemExit("No source CSVs found")

headers = []
by_file = {}
all_keys = defaultdict(list)
selected = []
for path in files:
    with path.open("r", encoding="cp949", newline="") as source:
        reader = csv.DictReader(source)
        header = reader.fieldnames
        if header is None:
            raise ValueError(f"Missing header: {path.name}")
        headers.append(header)
        rows = list(reader)
    if any(None in row for row in rows):
        raise ValueError(f"Malformed row width: {path.name}")
    stations = Counter(row["지점"] for row in rows)
    dates = []
    for row in rows:
        date = datetime.strptime(row["일시"], "%Y-%m-%d %H:%M")
        dates.append(date)
        all_keys[(row["지점"], date)].append(path.name)
        if row["지점"] == "108":
            selected.append((date, row, path.name))
    by_file[path.name] = (len(rows), stations, min(dates), max(dates), len(dates) - len(set(dates)))

print("HEADERS")
for head in headers:
    print(head)
if any(head != headers[0] for head in headers[1:]):
    raise ValueError("Source headers differ")
print("FILES")
for name, (count, stations, start, end, dup) in by_file.items():
    print(name, "rows", count, "stations", dict(stations), "start", start, "end", end, "duplicate timestamps", dup)
    label_year = int(Path(name).stem.rsplit("_", 1)[-1])
    if label_year != start.year or start.year != end.year:
        print("YEAR LABEL MISMATCH", name, "label", label_year, "data year", start.year)

overlap = {key: names for key, names in all_keys.items() if len(names) > 1}
print("DUPLICATE STATION+TIMESTAMP", len(overlap))
for key, names in list(overlap.items())[:10]:
    print(key, names)

selected.sort(key=lambda item: item[0])
dates = [item[0] for item in selected]
counts = Counter(date.year for date in dates)
print("STATION 108", len(selected), "PER YEAR", dict(sorted(counts.items())))
print("SELECTED RANGE", min(dates), max(dates))
missing = []
expected = min(dates)
seen = set(dates)
while expected <= max(dates):
    if expected not in seen:
        missing.append(expected)
    expected += timedelta(hours=1)
print("MISSING HOURS BETWEEN ENDPOINTS", len(missing))
print("FIRST MISSING", missing[:20])
print("BLANKS", {column: sum(row[column].strip() == "" for _, row, _ in selected) for column in headers[0]})

if overlap:
    raise SystemExit("Merge blocked: duplicate station/timestamp pairs")

output = folder / "ASOS_서울108_2020-2025_병합.csv"
with output.open("w", encoding="utf-8-sig", newline="") as destination:
    writer = csv.DictWriter(destination, fieldnames=headers[0])
    writer.writeheader()
    writer.writerows(row for _, row, _ in selected)
with output.open("r", encoding="utf-8-sig", newline="") as merged_file:
    merged_reader = csv.DictReader(merged_file)
    if merged_reader.fieldnames != headers[0]:
        raise ValueError("Merged header mismatch")
    merged_rows = list(merged_reader)
if merged_rows != [row for _, row, _ in selected]:
    raise ValueError("Merged row content or ordering mismatch")
print("VERIFIED", len(merged_rows), "rows, identical to sorted source records")
print("OUTPUT", output.name, output.stat().st_size, "bytes")
