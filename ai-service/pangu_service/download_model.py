"""Download the official 24h ONNX model, once (about 1.1 GB)."""
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("models/pangu_weather_24.onnx"))
    args = parser.parse_args()
    target = args.output.resolve()
    if target.exists():
        raise SystemExit(f"Already exists; use this file or choose another --output: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    import gdown
    partial = target.with_suffix(".onnx.part")
    result = gdown.download(id="1lweQlxcn9fG0zKNW8ne1Khr9ehRTI6HP", output=str(partial), quiet=False, use_cookies=False)
    if result is None or not partial.is_file() or partial.stat().st_size < 100_000_000:
        raise SystemExit("Download failed. Use the 24h model link in the official Pangu repository.")
    partial.replace(target)
    print(target)


if __name__ == "__main__":
    main()
