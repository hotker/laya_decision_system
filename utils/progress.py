"""
Progress Bar
=============
Display progress bar for long-running operations

Usage:
    from progress import ProgressBar
    with ProgressBar(total=100, desc="Processing") as p:
        for i in range(100):
            # do work
            p.update(1)
"""

from __future__ import annotations

import sys
import time
from typing import Any


class ProgressBar:
    """Simple progress bar"""

    def __init__(
        self,
        total: int,
        desc: str = "Processing",
        width: int = 40,
    ) -> None:
        """Initialize progress bar

        Args:
            total: Total number of items
            desc: Description label
            width: Bar width in characters
        """
        self.total = total
        self.desc = desc
        self.width = width
        self.current = 0
        self.start_time = time.monotonic()

    def __enter__(self) -> "ProgressBar":
        return self

    def __exit__(self, *args: Any) -> None:
        print()  # Newline after progress bar

    def update(self, n: int = 1) -> None:
        """Update progress by n

        Args:
            n: Number of items to advance
        """
        self.current += n
        self._render()

    def _render(self) -> None:
        """Render progress bar"""
        if self.total == 0:
            return

        pct = min(self.current / self.total, 1.0)
        filled = int(self.width * pct)
        bar = "█" * filled + "░" * (self.width - filled)

        elapsed = time.monotonic() - self.start_time
        rate = self.current / elapsed if elapsed > 0 else 0
        eta = (self.total - self.current) / rate if rate > 0 else 0

        # Format ETA
        if eta > 3600:
            eta_str = f"{eta / 3600:.1f}h"
        elif eta > 60:
            eta_str = f"{eta / 60:.1f}m"
        else:
            eta_str = f"{eta:.1f}s"

        # Build the full line
        line = "{} {} |{}| {:5.1f}% {} ETA {}".format(
            self.desc,
            bar,
            f"{pct * 100:.1f}%",
            f"{rate:.1f}/s",
            eta_str,
        )

        sys.stdout.write("\r" + line + " " * 20)
        sys.stdout.flush()


class SimpleProgress:
    """Simple text progress without bar"""

    def __init__(
        self,
        total: int,
        desc: str = "Processing",
    ) -> None:
        self.total = total
        self.desc = desc
        self.current = 0

    def __enter__(self) -> "SimpleProgress":
        return self

    def __exit__(self, *args: Any) -> None:
        print()

    def update(self, n: int = 1) -> None:
        """Update progress by n"""
        self.current += n
        pct = self.current / self.total * 100
        print(f"\r{self.desc}: {self.current}/{self.total} ({pct:.1f}%)", end="", flush=True)