"""Start automatic daily GPU refresh from this project's directory."""
import os
from pathlib import Path


if __name__ == '__main__':
    os.chdir(Path(__file__).resolve().parent)
    from pangu_service.auto_update import main
    main()
