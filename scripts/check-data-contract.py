#!/usr/bin/env python3
"""
cgv-data boundary check.

Derived from DATA_CONTRACT.md (normative) and
Biblia-LBF/docs/architecture/CGV_DATA_ARCHITECTURE.md.

cgv-data is the distribution repository. It holds published output only: no
drafts, no approvals, no editor state, no repair scripts. Released version
directories are immutable; `current.json` is the only mutable pointer, and it may
only move to a version that is complete and validated.

READ-ONLY. This script never creates, modifies, moves or deletes repository
data. `--emit-baseline` prints JSON to stdout; it writes no file.

Exit codes:
  0  no new violations
  1  new violations found (not present in the baseline)
  2  usage or internal error
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_NAME = "cgv-data"
BASELINE_FILENAME = ".data-contract-baseline.json"

FINDINGS: list[dict] = []
NOTES: list[str] = []


def add(rule: str, path: str, message: str, key: str = "") -> None:
    FINDINGS.append(
        {"id": f"{rule}|{path}|{key}", "rule": rule, "path": path, "key": key, "message": message}
    )


def note(message: str) -> None:
    NOTES.append(message)


# --------------------------------------------------------------------------
# tiny JSON Schema subset validator (stdlib only)
# --------------------------------------------------------------------------

TYPES = {
    "object": dict,
    "array": list,
    "string": str,
    "number": (int, float),
    "integer": int,
    "boolean": bool,
    "null": type(None),
}


def validate(instance, schema, where="$") -> list[str]:
    errors: list[str] = []
    expected = schema.get("type")
    if expected:
        wanted = TYPES.get(expected)
        if wanted is None:
            return errors
        if expected == "integer" and isinstance(instance, bool):
            return [f"{where}: expected integer, got boolean"]
        if not isinstance(instance, wanted):
            return [f"{where}: expected {expected}, got {type(instance).__name__}"]
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{where}: {instance!r} not one of {schema['enum']}")
    if "pattern" in schema and isinstance(instance, str):
        if not re.search(schema["pattern"], instance):
            errors.append(f"{where}: {instance!r} does not match /{schema['pattern']}/")
    if isinstance(instance, dict):
        for field in schema.get("required", []):
            if field not in instance:
                errors.append(f"{where}: missing required property '{field}'")
        if "minProperties" in schema and len(instance) < schema["minProperties"]:
            errors.append(f"{where}: expected at least {schema['minProperties']} properties")
        props = schema.get("properties", {})
        for name, value in instance.items():
            if name in props:
                errors.extend(validate(value, props[name], f"{where}.{name}"))
            elif schema.get("additionalProperties") is False:
                errors.append(f"{where}: unexpected property '{name}'")
    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(f"{where}: expected at least {schema['minItems']} items")
        if schema.get("items"):
            for index, item in enumerate(instance):
                errors.extend(validate(item, schema["items"], f"{where}[{index}]"))
    return errors


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv"}
VERSION_DIR = re.compile(r"^(?P<dataset>.+)/versions/(?P<version>[^/]+)(?:/|$)")


def walk(repo: Path):
    for dirpath, dirnames, filenames in os.walk(repo):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name == ".DS_Store":
                continue
            yield (Path(dirpath) / name).relative_to(repo)


def tracked_files(repo: Path) -> list[Path]:
    """
    Files as CI sees them: git-tracked only. An untracked scratch copy, a local
    worktree or an ignored build directory is not part of the repository and must
    not affect the result.
    """
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), "ls-files", "-z"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        result = None
    if result is None or result.returncode != 0:
        note("Not a git checkout; falling back to a filesystem walk.")
        return list(walk(repo))
    return [
        Path(entry)
        for entry in result.stdout.split("\0")
        if entry and not entry.endswith(".DS_Store")
    ]


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return exc


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(repo: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    return result.stdout


def resolve_base(repo: Path, requested: str | None) -> str | None:
    for candidate in filter(None, [requested, "origin/main", "main"]):
        if git(repo, "rev-parse", "--verify", "--quiet", f"{candidate}^{{commit}}"):
            return candidate
    return None


# --------------------------------------------------------------------------
# prohibited content
# --------------------------------------------------------------------------

PROHIBITED = [
    (
        "DRAFT_ARTIFACT",
        re.compile(r"(^|/)[^/]*(draft|wip|scratch|tmp|temp)[^/]*/|[-_.](draft|wip)\b", re.I),
        "Drafts do not belong in the distribution repository. Publish from the "
        "source repository instead.",
    ),
    (
        "WORKFLOW_STATE",
        re.compile(r"(^|/)[^/]*(approval|review|queue|comment|editor-state|workflow)[^/]*\.",
                   re.I),
        "Approval, review, queue and editor state live in the source repository, "
        "never in published output.",
    ),
    (
        "USER_PROGRESS",
        re.compile(r"(^|/)[^/]*progress[^/]*\.", re.I),
        "User progress is application state and must never be published here.",
    ),
    (
        "REPAIR_SCRIPT",
        re.compile(
            r"(^|/)[^/]*(align|repair|rebuild|recut|repack|workbench|seed|compile|fix)"
            r"[^/]*\.(py|mjs|js|ts|sh)$",
            re.I,
        ),
        "Alignment generation and repair scripts are prohibited here. They belong "
        "to the repository that owns the editable data.",
    ),
    (
        "APP_FIXTURE",
        re.compile(r"(^|/)(fixtures?|__tests__|test-data|mocks?)(/|$)", re.I),
        "App-specific fixtures must not be mixed into published datasets.",
    ),
    (
        "BACKUP_FILE",
        re.compile(r"\.(bak|orig|rej)$|\.pre-[a-z0-9-]+\.json$|(^|/)backups?/", re.I),
        "Backup and pre-migration copies are not publishable artifacts.",
    ),
]

ALLOWED_SCRIPTS = {"scripts/check-data-contract.py"}


def check_prohibited(repo: Path) -> None:
    for rel in tracked_files(repo):
        posix = rel.as_posix()
        if posix in ALLOWED_SCRIPTS or posix.startswith(".github/"):
            continue
        for rule, pattern, message in PROHIBITED:
            if pattern.search(posix):
                add(rule, posix, message)
                break


# --------------------------------------------------------------------------
# dataset manifests
# --------------------------------------------------------------------------

DATASET_ROOTS = [
    re.compile(r"^bibles/[^/]+$"),
    re.compile(r"^interlinears/[^/]+$"),
    re.compile(r"^morphology/[^/]+$"),
    re.compile(r"^(songs|courses|media|dictionaries|lexicons)$"),
]


def dataset_roots(repo: Path) -> list[str]:
    roots: list[str] = []
    for dirpath, dirnames, _ in os.walk(repo):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        rel = Path(dirpath).relative_to(repo).as_posix()
        if rel == ".":
            continue
        if any(pattern.match(rel) for pattern in DATASET_ROOTS):
            roots.append(rel)
    return sorted(roots)


def check_datasets(repo: Path, schema_dir: Path) -> None:
    manifest_schema = load_json(schema_dir / "dataset-manifest.schema.json")
    pointer_schema = load_json(schema_dir / "current-pointer.schema.json")
    if isinstance(manifest_schema, Exception):
        note(f"dataset-manifest schema unreadable ({manifest_schema}); manifests not validated.")
        manifest_schema = None
    if isinstance(pointer_schema, Exception):
        pointer_schema = None

    for root in dataset_roots(repo):
        root_path = repo / root
        has_versions = (root_path / "versions").is_dir()
        has_current = (root_path / "current.json").is_file()
        if not has_versions:
            add(
                "UNVERSIONED_DATASET",
                root,
                "Dataset has no versions/ directory, so consumers cannot pin an "
                "immutable version. Every dataset needs a versioned, manifested "
                "release.",
                key="no-versions",
            )
            continue
        if not has_current:
            add(
                "MISSING_CURRENT_POINTER",
                f"{root}/current.json",
                "Versioned dataset has no current.json pointer.",
            )

        for version_dir in sorted((root_path / "versions").iterdir()):
            if not version_dir.is_dir():
                continue
            check_version_dir(repo, version_dir, manifest_schema)

        if has_current and pointer_schema:
            pointer_path = root_path / "current.json"
            pointer = load_json(pointer_path)
            rel_pointer = pointer_path.relative_to(repo).as_posix()
            if isinstance(pointer, Exception):
                add("INVALID_JSON", rel_pointer, f"current.json is not valid JSON: {pointer}")
            else:
                for error in validate(pointer, pointer_schema):
                    add("CURRENT_POINTER_INVALID", rel_pointer, error, key=error[:80])
                target = pointer.get("datasetVersion")
                if target and not (root_path / "versions" / str(target)).is_dir():
                    add(
                        "CURRENT_POINTER_INVALID",
                        rel_pointer,
                        f"current.json points at version '{target}', which does not "
                        "exist.",
                        key="dangling",
                    )


def check_version_dir(repo: Path, version_dir: Path, manifest_schema) -> None:
    rel_dir = version_dir.relative_to(repo).as_posix()
    manifest_path = version_dir / "manifest.json"
    if not manifest_path.is_file():
        add(
            "MISSING_MANIFEST",
            rel_dir,
            "Published version has no manifest.json, so nothing declares its "
            "provenance, scope, licence or checksums.",
        )
        return

    manifest = load_json(manifest_path)
    rel_manifest = manifest_path.relative_to(repo).as_posix()
    if isinstance(manifest, Exception):
        add("INVALID_JSON", rel_manifest, f"manifest.json is not valid JSON: {manifest}")
        return

    if manifest_schema:
        for error in validate(manifest, manifest_schema):
            add("MANIFEST_INVALID", rel_manifest, error, key=error[:80])

    checksums = manifest.get("checksums")
    if not isinstance(checksums, dict):
        return

    declared = set(checksums)
    present: set[str] = set()
    for path in version_dir.rglob("*"):
        if path.is_file() and path.name not in {"manifest.json", ".DS_Store"}:
            present.add(path.relative_to(version_dir).as_posix())

    for undeclared in sorted(present - declared):
        add(
            "UNDECLARED_FILE",
            f"{rel_dir}/{undeclared}",
            "File is inside a published version but is not declared in "
            "manifest.json checksums.",
        )
    for missing in sorted(declared - present):
        add(
            "MISSING_DECLARED_FILE",
            f"{rel_dir}/{missing}",
            "manifest.json declares this file, but it is not in the release.",
        )
    for name in sorted(declared & present):
        actual = sha256_of(version_dir / name)
        expected = checksums[name]
        if isinstance(expected, dict):
            expected = expected.get("sha256")
        if actual != expected:
            add(
                "CHECKSUM_MISMATCH",
                f"{rel_dir}/{name}",
                f"Published file does not match its manifest checksum "
                f"(declared {str(expected)[:16]}…, actual {actual[:16]}…). Either the "
                "file was hand-edited or the manifest is stale.",
            )

    atomic = manifest.get("atomicWith") or []
    for partner in atomic:
        partner_current = repo / str(partner) / "current.json"
        if not partner_current.exists() and not (repo / str(partner)).exists():
            add(
                "ATOMIC_PARTNER_MISSING",
                rel_manifest,
                f"Manifest declares an atomic release with '{partner}', which is not "
                "present in this repository.",
                key=str(partner),
            )


# --------------------------------------------------------------------------
# immutability of released versions (git)
# --------------------------------------------------------------------------


def check_immutability(repo: Path, base: str | None) -> None:
    if base is None:
        note("No base ref available; immutable-version and current.json diff checks skipped.")
        return

    merge_base = (git(repo, "merge-base", base, "HEAD") or "").strip() or base
    diff = git(repo, "diff", "--name-status", "-M", f"{merge_base}", "HEAD")
    if diff is None:
        note(f"git diff against {base} failed; immutability check skipped.")
        return

    changed: list[tuple[str, str]] = []
    for line in diff.splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        changed.append((parts[0][0], parts[-1]))

    if not changed:
        note(f"No file changes against {base}.")

    for status, path in changed:
        match = VERSION_DIR.match(path)
        if not match:
            continue
        version_root = f"{match.group('dataset')}/versions/{match.group('version')}"
        existed = git(repo, "cat-file", "-t", f"{merge_base}:{version_root}")
        if not existed:
            continue  # brand new version directory: allowed
        verb = {"M": "modified", "D": "deleted", "R": "renamed", "A": "added to"}.get(
            status, "changed"
        )
        add(
            "IMMUTABLE_VERSION_CHANGED",
            path,
            f"Released version '{version_root}' already exists in {base}, but this "
            f"change {verb} it. Published versions are immutable — publish a new "
            "version directory instead.",
            key=status,
        )

    for status, path in changed:
        if not path.endswith("/current.json"):
            continue
        pointer = load_json(repo / path)
        if isinstance(pointer, Exception):
            continue
        target = pointer.get("datasetVersion")
        dataset_root = path[: -len("/current.json")]
        version_root = repo / dataset_root / "versions" / str(target)
        if not version_root.is_dir():
            add(
                "CURRENT_POINTER_INVALID",
                path,
                f"current.json now points at '{target}', which is not a version "
                "directory in this commit.",
                key="moved-to-missing",
            )
            continue
        if not (version_root / "manifest.json").is_file():
            add(
                "CURRENT_POINTER_INVALID",
                path,
                f"current.json moved to '{target}', which has no manifest.json. The "
                "pointer may only move to a complete, validated release.",
                key="moved-to-unmanifested",
            )


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=f"{REPO_NAME} data-contract boundary check")
    parser.add_argument("--repo", default=str(Path(__file__).resolve().parent.parent))
    parser.add_argument("--schema-dir", default=None, help="Default: <repo>/schemas")
    parser.add_argument("--baseline", default=None)
    parser.add_argument("--base-ref", default=None, help="Git ref to compare against.")
    parser.add_argument("--emit-baseline", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    if not repo.is_dir():
        print(f"error: {repo} is not a directory", file=sys.stderr)
        return 2
    schema_dir = Path(args.schema_dir) if args.schema_dir else repo / "schemas"
    if not schema_dir.is_dir():
        note(f"{schema_dir.name}/ not found; manifest and pointer schemas not applied.")

    check_prohibited(repo)
    if schema_dir.is_dir():
        check_datasets(repo, schema_dir)
    check_immutability(repo, resolve_base(repo, args.base_ref))

    FINDINGS.sort(key=lambda f: (f["rule"], f["path"], f["key"]))

    if args.emit_baseline:
        print(
            json.dumps(
                {
                    "_comment": (
                        "Violations that already existed when the boundary check was "
                        "introduced. CI fails on anything not listed here. Shrink this "
                        "list; never grow it."
                    ),
                    "repository": REPO_NAME,
                    "accepted": [f["id"] for f in FINDINGS],
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return 0

    baseline_path = Path(args.baseline) if args.baseline else repo / BASELINE_FILENAME
    accepted: set[str] = set()
    if baseline_path.is_file():
        loaded = load_json(baseline_path)
        if isinstance(loaded, dict):
            accepted = set(loaded.get("accepted", []))
        else:
            print(f"error: cannot read baseline {baseline_path}", file=sys.stderr)
            return 2

    new = [f for f in FINDINGS if f["id"] not in accepted]
    fixed = sorted(accepted - {f["id"] for f in FINDINGS})

    if args.json:
        print(
            json.dumps(
                {
                    "repository": REPO_NAME,
                    "new": new,
                    "baselined": len(FINDINGS) - len(new),
                    "fixed": fixed,
                    "notes": NOTES,
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return 1 if new else 0

    print(f"{REPO_NAME} data-contract boundary check")
    print(f"  findings: {len(FINDINGS)}   baselined: {len(FINDINGS) - len(new)}   new: {len(new)}")
    if fixed:
        print(f"  fixed since baseline: {len(fixed)} (remove these from the baseline)")
    if NOTES:
        print("\nnotes:")
        for entry in NOTES:
            print(f"  - {entry}")
    if new:
        print("\nNEW VIOLATIONS")
        for finding in new:
            print(f"  [{finding['rule']}] {finding['path']}")
            print(f"      {finding['message']}")
        return 1
    print("\nOK - no new violations.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
