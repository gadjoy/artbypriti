# Legacy archive — where the old migration files went

The `legacy/` directory was removed from the working tree. **Nothing was deleted from git
history**, so every file is still retrievable at the commit below, permanently.

## The reference

| | |
| --- | --- |
| **Tag** | `legacy-archive` |
| **Commit** | `8d0cf6e376da7eb0e482d328cda45b472408ef6b` |
| **Subject** | Merge pull request #14 from vivekanandba/docs/update-repo-owner-readme |
| **Date** | 2026-06-07 |
| **Contents** | 1477 files, 1380 MB under `legacy/` |

The `legacy-archive` tag exists so this reference cannot rot: the commit stays reachable
regardless of what happens to branch history.

## Why it was removed

`legacy/` was 1380 MB of the repository's 1497 MB tip tree — 92% of everything CI downloaded
and wrote on *every single deploy*, for files that no build step reads. Removing it from the
tree cuts a fresh checkout to roughly 117 MB.

## What was in it

| Path | Files | Size | What it is |
| --- | --- | --- | --- |
| `legacy/wordpress` | 8 | 335 MB | The original WordPress site backup, including a `.wpress` export split across four `*_part_0*` files |
| `legacy/migration_1` | 414 | 257 MB | First WordPress → Hugo migration attempt (`wp_to_hugo.py`, exports, image tree) |
| `legacy/migration_2` | 424 | 262 MB | Second attempt (`migrate_all.sh`, original-title logs) |
| `legacy/migration_3` | 428 | 263 MB | Third attempt |
| `legacy/migration_4` | 101 | 131 MB | Fourth attempt (`migrate4.py`) |
| `legacy/migration_5` | 102 | 131 MB | Fifth attempt — the flat-content restructure (`flatten-content.py`) that produced today's layout |

The five migration snapshots are near-identical copies of the same WordPress-era image set,
which is why the total is so large relative to the ~116 MB of live artwork.

## How to get it back

Inspect without restoring anything:

```bash
git show legacy-archive --stat -- legacy/          # what changed at that commit
git ls-tree -r --name-only legacy-archive -- legacy/   # full file listing
git show legacy-archive:legacy/migration_5/flatten-content.py   # read a single file
```

Restore the whole directory into the working tree:

```bash
git restore --source=legacy-archive -- legacy/
# older git: git checkout legacy-archive -- legacy/
```

Restore just one subdirectory:

```bash
git restore --source=legacy-archive -- legacy/wordpress/
```

Reassemble the split WordPress backup after restoring it (see also
`docs/linux-file-split-and-merge-guide.md`):

```bash
cat legacy/wordpress/backup/*.wpress_part_* > artbypriti.wpress
```

**If you cloned shallowly** (CI does this by default), the archive commit won't be present
locally. Fetch it first:

```bash
git fetch --unshallow            # or: git fetch --depth=1 origin tag legacy-archive
```

Anything restored this way is deliberately untracked-by-intent — don't commit it back onto
`main`, or the checkout cost returns.
