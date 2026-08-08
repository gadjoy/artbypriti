#!/usr/bin/env bash
#
# Vendor the shared constitution into another repository.
#
#   scripts/install-constitution.sh /path/to/repo
#
# Copies constitution/base.md and the drift check, then splices the base into that
# project's .specify/memory/constitution.md between markers — ABOVE its own principles,
# which are never touched. A project that needs to differ overrides a shared principle
# below the block and says why; a base that cannot be overridden gets the whole thing
# rejected.
#
# Idempotent: re-run to pick up a new base version.
set -euo pipefail

SOURCE="$(cd "$(dirname "$0")/.." && pwd)"
TARGET="$(cd "${1:?usage: install-constitution.sh /path/to/repo}" && pwd)"
VERSION="$(cat "$SOURCE/constitution/VERSION")"
BEGIN="<!-- BEGIN SHARED CONSTITUTION"
END="<!-- END SHARED CONSTITUTION -->"

cd "$TARGET"
git rev-parse --show-toplevel >/dev/null 2>&1 || { echo "$TARGET is not a git repo" >&2; exit 1; }
[ -n "$(git status --porcelain -uall)" ] && { echo "refusing: working tree is dirty" >&2; exit 1; }

mkdir -p constitution
cp "$SOURCE/constitution/base.md" constitution/base.md
cp "$SOURCE/constitution/VERSION" constitution/VERSION
cp "$SOURCE/scripts/check-constitution.py" scripts/check-constitution.py
chmod +x scripts/check-constitution.py
echo "  vendored constitution v$VERSION"

CONST=".specify/memory/constitution.md"
if [ ! -f "$CONST" ]; then
  echo "  no $CONST here — copy the block from constitution/base.md into one when you write it"
  exit 0
fi

python3 - "$CONST" "$VERSION" <<'PY'
import re, sys
const, version = sys.argv[1], sys.argv[2]
base = open('constitution/base.md', encoding='utf-8').read()
canonical = re.sub(r"^<!--.*?-->\s*", "", base, flags=re.DOTALL).strip()
s = open(const, encoding='utf-8').read()
block = (f"<!-- BEGIN SHARED CONSTITUTION v{version} — vendored from constitution/base.md.\n"
         "     Do not edit here; amend upstream and re-vendor. -->\n\n"
         + canonical + "\n\n<!-- END SHARED CONSTITUTION -->\n")
if "<!-- BEGIN SHARED CONSTITUTION" in s:
    pre, rest = s.split("<!-- BEGIN SHARED CONSTITUTION", 1)
    post = rest.split("<!-- END SHARED CONSTITUTION -->", 1)[1]
    open(const, 'w', encoding='utf-8').write(pre + block + post)
    print("  updated the existing shared block; project principles untouched")
else:
    m = re.search(r"^## ", s, re.MULTILINE)
    i = m.start() if m else len(s)
    open(const, 'w', encoding='utf-8').write(s[:i] + block + "\n---\n\n" + s[i:])
    print("  spliced the shared block above this project's own principles")
PY
echo "  run scripts/check-constitution.py, review the diff, then commit."
