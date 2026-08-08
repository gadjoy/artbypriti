#!/usr/bin/env bash
#
# Everything CI will check, run before you push.
#
# A failure costs seconds here instead of a round trip through GitHub, and the
# checks keep working if this project ever moves off GitHub entirely.
#
#   scripts/preflight.sh            # spec + content + strict build + output assertions
#   scripts/preflight.sh --quick    # skip the build; validators only (near-instant)
#
# Visual regression runs too when Docker is available. It is skipped, loudly, when
# not — a hook that fails because of a missing tool teaches people to use
# --no-verify, and a bypassed hook protects nothing.
#
# Bypass: git push --no-verify
set -uo pipefail
cd "$(git rev-parse --show-toplevel)" || exit 2

QUICK=false
[ "${1:-}" = "--quick" ] && QUICK=true
FAILED=0

step() { printf '\n\033[1m%s\033[0m\n' "$1"; }
fail() { printf '\033[31mblocked:\033[0m %s\n' "$1"; FAILED=1; }

step "specs"
python3 scripts/check-specs.py || fail "spec hygiene"

step "content"
python3 scripts/check-content.py || fail "front matter"

if [ "$QUICK" = true ]; then
  printf '\n(--quick: skipped build, output assertions and visual regression)\n'
  exit $FAILED
fi

step "build"
# A cold image cache makes this ~200s; warm it is ~0.5s. Say so rather than
# leaving someone staring at a silent hook.
if [ ! -d "$(hugo config 2>/dev/null | awk -F"'" '/^ *dir = .:cacheDir/ {print $2}' | head -1)" ] 2>/dev/null; then
  printf '  (first run after a clean cache can take a couple of minutes)\n'
fi
hugo --minify --gc --cleanDestinationDir --panicOnWarning --printPathWarnings >/dev/null \
  || fail "hugo build (warnings are errors here)"

step "output"
python3 scripts/check-output.py public || fail "built-site assertions"

step "visual"
if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
  make visual >/dev/null 2>&1 || fail "visual regression — run 'make visual' to see the diffs"
  [ "$FAILED" = 0 ] && printf '  screenshots match the committed baselines\n'
else
  printf '  skipped: Docker not available (CI still runs it)\n'
fi

if [ "$FAILED" != 0 ]; then
  printf '\nPush blocked. Fix the above, or push with --no-verify to let CI judge.\n'
fi
exit $FAILED
