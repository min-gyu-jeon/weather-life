"""Start the API on this PC using a persistent, locally generated API key."""
import os
import secrets
from pathlib import Path

import uvicorn


def main():
    root = Path(__file__).resolve().parent
    os.chdir(root)
    key_file = root / "local-api.key"
    if not key_file.exists():
        key_file.write_text(secrets.token_urlsafe(32), encoding="utf-8")
    os.environ["PANGU_API_KEY"] = key_file.read_text(encoding="utf-8").strip()
    os.environ["PANGU_DATA_DIR"] = str(root / "data")
    os.environ["PANGU_STATIONS_CSV"] = str(root / "stations.csv")
    uvicorn.run("pangu_service.api:app", host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
