#!/usr/bin/env python3
"""Keep the shared constitution shared.

A vendored copy that anyone can quietly edit is not shared — it is a fork with a
misleading name. This asserts that the block spliced into the project constitution is
byte-identical to constitution/base.md, and reports the version in use.

The fix for a drifting block is never to edit it here: amend upstream and re-vendor, or
add a project principle below the block that overrides it and says why.

Usage:  python3 scripts/check-constitution.py
Exit:   0 = in sync (warnings allowed), 1 = drift or missing
"""
import os
import re
import sys

BASE = "constitution/base.md"
PROJECT = ".specify/memory/constitution.md"
BEGIN = "<!-- BEGIN SHARED CONSTITUTION"
END = "<!-- END SHARED CONSTITUTION -->"

errors, notes = [], []


def main():
    if not os.path.isfile(BASE):
        errors.append(f"{BASE} missing — the shared base is not vendored here")
    if not os.path.isfile(PROJECT):
        errors.append(f"{PROJECT} missing")
    if errors:
        for e in errors:
            print(f"ERROR:   {e}")
        return 1

    base = open(BASE, encoding="utf-8").read().strip()
    proj = open(PROJECT, encoding="utf-8").read()
    version = open("constitution/VERSION").read().strip() if os.path.isfile("constitution/VERSION") else "?"

    if BEGIN not in proj or END not in proj:
        errors.append(
            f"{PROJECT} does not splice in the shared base. Add:\n"
            f"           {BEGIN} v{version} -->\n           ...contents of {BASE}...\n           {END}"
        )
    else:
        block = proj.split(BEGIN, 1)[1].split("-->", 1)[1].split(END, 1)[0].strip()
        # Compare on content, ignoring the canonical file's own editing banner.
        canonical = re.sub(r"^<!--.*?-->\s*", "", base, flags=re.DOTALL).strip()
        if block != canonical:
            errors.append(
                f"the shared block in {PROJECT} has drifted from {BASE}.\n"
                "         Amend upstream and re-vendor, or override it with a project principle\n"
                "         below the block that states why this project differs."
            )
        else:
            notes.append(f"shared constitution v{version} in sync ({len(canonical.splitlines())} lines)")

    for n in notes:
        print(f"ok:      {n}")
    for e in errors:
        print(f"ERROR:   {e}")
    print(f"\nconstitution: {len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
