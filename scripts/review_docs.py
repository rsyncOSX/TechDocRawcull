#!/usr/bin/env python3
"""Suggest non-package documentation reviews. Never updates the review baseline."""
import argparse
import fnmatch
import hashlib
import json
from pathlib import Path
import subprocess


def git(source, *args):
    return subprocess.check_output(["git", "-C", str(source), *args])


def nul_paths(source, *args):
    return set(git(source, *args).decode().strip("\0").split("\0")) - {""}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path, help="RawCull application checkout")
    parser.add_argument("--target", default="HEAD", help="Committed revision to compare with the reviewed baseline")
    parser.add_argument("--baseline", type=Path, default=Path(__file__).resolve().parents[1] / "data/documentation-review.json")
    args = parser.parse_args()
    baseline = json.loads(args.baseline.read_text())
    source = args.source.resolve()
    previous = baseline["application"]["commit"]
    target = git(source, "rev-parse", "--verify", args.target + "^{commit}").decode().strip()
    if subprocess.run(["git", "-C", str(source), "merge-base", "--is-ancestor", previous, target], capture_output=True).returncode:
        parser.error("Target must descend from the reviewed baseline; select a new baseline for divergent history.")
    changed = nul_paths(source, "diff", "--name-only", "--no-renames", "-z", previous, target)
    head = git(source, "rev-parse", "HEAD").decode().strip()
    working = set()
    if target == head:
        working |= nul_paths(source, "diff", "--name-only", "--no-renames", "-z", "HEAD")
        working |= nul_paths(source, "ls-files", "--others", "--exclude-standard", "-z")
        changed |= working
    pins_path = baseline["application"]["lockfile"]
    # Read the target's lockfile, or the current working copy when reviewing HEAD.
    lock = (source / pins_path).read_bytes() if target == head else git(source, "show", target + ":" + pins_path)
    new_pins = {p["identity"]: p for p in json.loads(lock)["pins"]}
    old_pins = {p["identity"]: p for p in baseline["pins"]}
    pin_changes = {name for name in old_pins.keys() | new_pins.keys() if old_pins.get(name) != new_pins.get(name)}
    covered = set()
    candidates = {}
    docs_root = args.baseline.resolve().parents[1]
    for page in baseline["pages"]:
        hits = {p for p in changed if any(fnmatch.fnmatchcase(p, pattern) for pattern in page["watch_paths"])}
        covered |= hits
        packages = pin_changes & set(page["watch_packages"])
        reasons = sorted(hits) + ["package pin: " + name for name in sorted(packages)]
        doc = docs_root / page["path"]
        if not doc.exists() or hashlib.sha256(doc.read_bytes()).hexdigest() != page["sha256"]:
            reasons.append("documentation changed since recorded review")
        if reasons:
            candidates[page["path"]] = reasons
    unmatched = sorted(changed - covered)
    if changed or pin_changes:
        candidates.setdefault("content/en/docs/update.md", []).append("record reviewed source delta and validation outcome before advancing baseline")
    print(f"Reviewed: {baseline['application']['version']} build {baseline['application']['build']} at {previous}")
    print(f"Target:   {target}")
    if working:
        print(f"Includes {len(working)} staged, unstaged or untracked source paths; a commit alone does not describe these inputs.")
    for page, reasons in sorted(candidates.items()):
        print("\nREVIEW " + page)
        for reason in reasons:
            print("  " + reason)
    if unmatched:
        print("\nUNMAPPED SOURCE CHANGES — triage before concluding which pages can be skipped:")
        for path in unmatched:
            print("  " + path)
    if pin_changes:
        print("\nPackage pins changed: " + ", ".join(sorted(pin_changes)))
        print("Package guides are excluded here; review them separately at their resolved revisions.")
    print(f"\n{len(candidates)} candidate pages; {len(unmatched)} unmapped source paths.")
    print("This is a conservative source-change selector, not semantic verification. It never advances the baseline.")
    print("Dated vendor research and model recipes still require explicit external requalification when reused.")
    return 2 if unmatched else 0


if __name__ == "__main__":
    raise SystemExit(main())
