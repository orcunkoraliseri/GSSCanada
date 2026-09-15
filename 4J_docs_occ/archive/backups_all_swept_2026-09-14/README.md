# Backup sweep, 2026-09-14

Every `*.bak*` file that was sitting loose in a working directory was moved here on 2026-09-14,
preserving its path relative to `4J_docs_occ/`. 306 files. **Nothing was deleted and nothing was
renamed** - to restore one, copy it back to the same relative path.

The files themselves date from 2026-08-14 onward; only the sweep is dated 2026-09-14. Backups that
already lived in a `previous/` directory were left where they were, since those directories are the
project's own established archive locations.

Written while the Madrid stock campaign was running; no file under `tools/` that any running process
reads was moved, only `.bak` siblings of those files.
