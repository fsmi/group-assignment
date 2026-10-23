"""Check that student names in input files are anonymized, to not leak personal data.

Usage: python scripts/check_students_anonymized.py FILE...
"""

import json
import sys
from pathlib import Path

# the only allowed student name
ANONYMIZED_NAME = "-"


def check(path: Path) -> list[str]:
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        return [f"{path}: invalid JSON ({e})"]
    if not isinstance(data, dict) or not isinstance(data.get("students"), dict):
        return []
    # report only the student id, never the name itself
    return [
        f"{path}: student {sid} has a name other than {ANONYMIZED_NAME!r}"
        for sid, student in data["students"].items()
        if not isinstance(student, dict) or student.get("name") != ANONYMIZED_NAME
    ]


def main() -> int:
    errors = [error for arg in sys.argv[1:] for error in check(Path(arg))]
    for error in errors:
        sys.stderr.write(f"{error}\n")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
