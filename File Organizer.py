
import argparse
import os
import shutil
import sys
from collections import Counter
from pathlib import Path

# Extension, category folder. Add your own as needed.
EXTENSION_MAP = {
    # Documents
    ".pdf": "Documents", ".doc": "Documents", ".docx": "Documents",
    ".txt": "Documents", ".rtf": "Documents", ".odt": "Documents",
    ".xls": "Documents", ".xlsx": "Documents", ".csv": "Documents",
    ".ppt": "Documents", ".pptx": "Documents", ".md": "Documents",
    # Images
    ".jpg": "Images", ".jpeg": "Images", ".png": "Images", ".gif": "Images",
    ".bmp": "Images", ".webp": "Images", ".svg": "Images", ".heic": "Images",
    # Videos
    ".mp4": "Videos", ".mkv": "Videos", ".avi": "Videos",
    ".mov": "Videos", ".wmv": "Videos", ".flv": "Videos", ".webm": "Videos",
    # Archives
    ".zip": "Archives", ".rar": "Archives", ".7z": "Archives",
    ".tar": "Archives", ".gz": "Archives", ".bz2": "Archives",
    # Code
    ".py": "Code", ".js": "Code", ".ts": "Code", ".html": "Code",
    ".css": "Code", ".java": "Code", ".c": "Code", ".cpp": "Code",
    ".go": "Code", ".rs": "Code", ".json": "Code", ".sh": "Code",
}

# Files that are probably still downloading - never touch these.
SKIP_SUFFIXES = {".crdownload", ".part", ".tmp", ".download"}

CATEGORY_NAMES = set(EXTENSION_MAP.values())


def unique_destination(dest_dir: Path, filename: str) -> Path:
    """Return a path in dest_dir that doesn't exist yet: name.ext, name (1).ext, ..."""
    candidate = dest_dir / filename
    if not candidate.exists():
        return candidate
    stem, suffix = Path(filename).stem, Path(filename).suffix
    counter = 1
    while True:
        candidate = dest_dir / f"{stem} ({counter}){suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def organize(target: Path, dry_run: bool = False) -> dict:
    """Organize files directly inside `target`. Returns a stats dictionary."""
    stats = {
        "moved": 0,
        "renamed": 0,      # moved, but renamed to avoid a collision
        "skipped": 0,      # unknown extension, hidden, partial download, etc.
        "errors": [],      # (filename, reason)
        "by_category": Counter(),
    }
    script_path = Path(__file__).resolve()

    try:
        # Materialize the listing first so moving files doesn't disturb the iterator.
        with os.scandir(target) as it:
            entries = list(it)
    except PermissionError:
        print(f"Permission denied reading directory: {target}", file=sys.stderr)
        stats["errors"].append((str(target), "cannot read directory"))
        return stats

    for entry in entries:
        try:
            # Only regular files; ignore folders (incl. our category folders) and symlinks.
            if not entry.is_file(follow_symlinks=False):
                continue
        except OSError as exc:
            stats["errors"].append((entry.name, f"stat failed: {exc.strerror}"))
            continue

        path = Path(entry.path)
        ext = path.suffix.lower()

        if (
            entry.name.startswith(".")
            or ext in SKIP_SUFFIXES
            or path.resolve() == script_path
        ):
            stats["skipped"] += 1
            continue

        category = EXTENSION_MAP.get(ext)
        if category is None:
            stats["skipped"] += 1
            continue

        dest_dir = target / category

        try:
            if not dry_run:
                dest_dir.mkdir(exist_ok=True)   # create category folder on demand
            final_path = unique_destination(dest_dir, entry.name)
            if not dry_run:
                shutil.move(str(path), str(final_path))
        except PermissionError:
            stats["errors"].append((entry.name, "permission denied (file in use or read-only)"))
            continue
        except FileExistsError:
            stats["errors"].append((entry.name, "destination already exists"))
            continue
        except OSError as exc:
            stats["errors"].append((entry.name, exc.strerror or str(exc)))
            continue

        stats["moved"] += 1
        stats["by_category"][category] += 1
        if final_path.name != entry.name:
            stats["renamed"] += 1
        label = "WOULD MOVE" if dry_run else "MOVED"
        print(f"  [{label}] {entry.name}  ->  {category}/{final_path.name}")

    return stats


def print_summary(target: Path, stats: dict, dry_run: bool) -> None:
    line = "=" * 52
    print(f"\n{line}")
    print(f" ORGANIZER SUMMARY{'  (DRY RUN)' if dry_run else ''}")
    print(line)
    print(f" Directory : {target}")
    print(f" {'Would relocate' if dry_run else 'Files relocated'}: {stats['moved']}")
    print(f" Renamed (name collisions): {stats['renamed']}")
    print(f" Skipped   : {stats['skipped']}")
    print(f" Errors    : {len(stats['errors'])}")
    if stats["by_category"]:
        print("-" * 52)
        print(f" {'Category':<20}{'Files':>6}")
        for category, count in sorted(stats["by_category"].items()):
            print(f" {category:<20}{count:>6}")
    if stats["errors"]:
        print("-" * 52)
        print(" Problems:")
        for name, reason in stats["errors"]:
            print(f"  - {name}: {reason}")
    print(line)


def main() -> int:
    parser = argparse.ArgumentParser(description="Organize a directory into category folders.")
    parser.add_argument("directory", nargs="?", default=str(Path.home() / "Downloads"),
                        help="folder to organize (default: ~/Downloads)")
    parser.add_argument("--dry-run", action="store_true",
                        help="show what would happen without moving anything")
    args = parser.parse_args()

    target = Path(args.directory).expanduser().resolve()
    if not target.is_dir():
        print(f"Error: '{target}' is not a directory.", file=sys.stderr)
        return 1

    print(f"Organizing: {target}\n")
    stats = organize(target, dry_run=args.dry_run)
    print_summary(target, stats, args.dry_run)
    return 0 if not stats["errors"] else 2


if __name__ == "__main__":
    sys.exit(main())