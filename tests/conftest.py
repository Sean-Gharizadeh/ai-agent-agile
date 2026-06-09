import sys
from pathlib import Path

# project root = one level above /tests
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
