"""Run the Windows CPU forecast worker with a verified memory limit."""
import os
from pathlib import Path
from pangu_service.guarded_run import main

if __name__ == "__main__":
    os.chdir(Path(__file__).resolve().parent)
    main()
