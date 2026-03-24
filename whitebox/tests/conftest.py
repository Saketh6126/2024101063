import sys
from pathlib import Path


def pytest_configure():
    """Ensure `moneypoly` is importable when tests live in `whitebox/tests`."""
    whitebox_dir = Path(__file__).resolve().parent.parent
    code_dir = whitebox_dir / "code"
    sys.path.insert(0, str(code_dir))
