import hashlib
import sys
import tomllib
from datetime import datetime
from pathlib import Path
from core.logs import logger

from core.config import PROJECT_ROOT

PYPROJECT = PROJECT_ROOT / "pyproject.toml"
REQUIREMENTS = PROJECT_ROOT / "requirements.txt"
HASH_CACHE = PROJECT_ROOT / "hash_files" / "deps.hash"
UV = "uv"


def deps_hash(deps: list[str]) -> str:
    canonical = "\n".join(sorted(deps))
    return hashlib.sha256(canonical.encode()).hexdigest()


def read_deps() -> list[str]:
    with PYPROJECT.open("rb") as f:
        data = tomllib.load(f)
    return data.get("project", {}).get("dependencies", [])


def cached_hash() -> str:
    try:
        return HASH_CACHE.read_text().strip()
    except OSError:
        return ""


def write_hash(h: str) -> None:
    HASH_CACHE.parent.mkdir(parents=True, exist_ok=True)
    HASH_CACHE.write_text(h)


def export_requirements(deps: list[str]) -> bool:
    REQUIREMENTS.write_text("\n".join(deps) + "\n")
    return True


def main() -> int:
    if not PYPROJECT.exists():
        logger.error(f"ERROR: {PYPROJECT} not found")
        return 1

    try:
        deps = read_deps()
    except Exception as e:
        logger.error(f"ERROR: failed to parse pyproject.toml: {e}")
        return 1

    current = deps_hash(deps)
    previous = cached_hash()

    if current == previous:
        logger.info("SKIP: [project].dependencies unchanged, no sync needed")
        return 0

    logger.info (f"SYNC: dependencies changed, exporting requirements.txt")
    if not export_requirements(deps):
        return 1

    write_hash(current)
    logger.info(f"OK: requirements.txt updated ({len(deps)} direct deps)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
