"""Export complete immutable forecast runs for an API-only machine."""
import argparse
import shutil
from pathlib import Path

from .storage import list_runs, load_surface


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--output", type=Path, required=True,
                        help="New directory; transfer its forecasts/ subdirectory to the API data-dir.")
    args = parser.parse_args()
    source, target = args.data_dir.resolve(), args.output.resolve()
    if target.exists() or target.is_relative_to(source) or source.is_relative_to(target):
        raise SystemExit("Output must be a new directory outside data-dir.")
    runs = list_runs(source)
    if not runs:
        raise SystemExit("No published forecast runs.")
    # Verify every file before copying. Published directories are immutable.
    for run in runs:
        for point in run["manifest"]["points"]:
            array = load_surface(run["folder"], point)
            del array
    for run in runs:
        shutil.copytree(run["folder"], target/"forecasts"/run["manifest"]["run_id"])
    print(target)


if __name__ == "__main__":
    main()
