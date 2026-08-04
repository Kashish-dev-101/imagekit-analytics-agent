---
name: clear-analytics-data
description: "Clears data/input/ (customer JSON exports) and data/extracted/ (cached extractor output) to prepare a clean slate for a new round of testing. Never touches data/output/ — those are potential customer deliverables and are never deleted by this skill. Lists exactly what will be removed before removing it."
when_to_use: When starting a fresh testing round and you want to clear customer JSON inputs and cached extracted files without touching the output folder.
---

# Clear Analytics Data

Clears working/derived data only — never touches `data/output/`.

## Scope — what this does and does not touch

- **`data/input/`** — deletes all JSON files, both loose files directly in `data/input/` and files inside any per-customer subfolder. Subfolders themselves are kept (empty), so the working structure is ready for new drops without recreating folders.
- **`data/extracted/`** — deletes all `.txt` cache files. These are fully regenerable from source JSON by `agent/extract.py`, so there's no data loss.
- **`data/output/` is never touched by this skill, under any circumstance.** Those files may already be in front of a customer — clearing them is a separate, deliberate decision the user makes explicitly, not something this skill does as a side effect.

## Steps

1. List every file that will be deleted:
   ```bash
   find data/input -type f -not -name ".gitkeep" -not -name "README.md"
   find data/extracted -type f -not -name ".gitkeep"
   ```
2. Show this list to the user and ask for explicit confirmation before deleting anything — `data/` is gitignored, so nothing removed here can be recovered via git.
3. On confirmation, delete:
   ```bash
   find data/input -type f -not -name ".gitkeep" -not -name "README.md" -delete
   find data/extracted -type f -not -name ".gitkeep" -delete
   ```
4. Confirm what was removed and state plainly that `data/output/` was not touched.
