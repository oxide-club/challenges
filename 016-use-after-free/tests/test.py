from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.vector_runner import main

if __name__ == "__main__":
    sys.exit(main(Path(__file__).with_name("cases.json")))
