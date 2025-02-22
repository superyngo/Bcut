import sys
import os
from pathlib import Path

runtime_pth: Path = Path(os.path.abspath(sys.argv[0])).parent

# Add the src directory to the Python path
sys.path.insert(0, str(runtime_pth / "src"))

# Import and execute the main function from main_tui.py
from src.main_tui import main

if __name__ == "__main__":
    main()
