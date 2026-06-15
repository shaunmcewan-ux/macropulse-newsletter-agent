"""
Chart-freshness helper.

A new issue must never silently reuse the previous issue's spotlight
screenshots. At the start of each run the orchestrator calls
`archive_stale_charts`, which moves any chart image in drafts/charts/ that was
last modified *before today* into drafts/charts/_archive/<date>/. Images saved
today (this issue's freshly-captured screenshots) are left in place, so a
re-run later the same day still picks them up.

This makes the workflow deterministic:
  1. First run of a new issue archives last week's images -> the test draft
     shows placeholders + the written analysis, telling the user exactly which
     charts to capture.
  2. The user saves this week's TradingView screenshots into drafts/charts/.
  3. A re-run keeps those (mtime == today) and embeds them in the final.
"""

from __future__ import annotations

import os
import shutil
from datetime import date

_IMAGE_EXTS = (".png", ".jpg", ".jpeg")


def archive_stale_charts(charts_dir: str, today: date) -> list[str]:
    """Move chart images older than `today` into _archive/<mdate>/.

    Returns the list of filenames moved. Never touches the _archive folder
    itself, sub-directories, or files modified today.
    """
    if not os.path.isdir(charts_dir):
        return []

    moved: list[str] = []
    archive_root = os.path.join(charts_dir, "_archive")

    for name in sorted(os.listdir(charts_dir)):
        if not name.lower().endswith(_IMAGE_EXTS):
            continue
        path = os.path.join(charts_dir, name)
        if not os.path.isfile(path):
            continue

        mdate = date.fromtimestamp(os.path.getmtime(path))
        if mdate >= today:
            continue  # this issue's screenshot — keep it

        dest_dir = os.path.join(archive_root, mdate.isoformat())
        os.makedirs(dest_dir, exist_ok=True)
        # If a same-named file already sits in the archive, suffix to avoid clobber.
        dest = os.path.join(dest_dir, name)
        if os.path.exists(dest):
            stem, ext = os.path.splitext(name)
            dest = os.path.join(dest_dir, f"{stem}-{int(os.path.getmtime(path))}{ext}")
        shutil.move(path, dest)
        moved.append(name)

    return moved
