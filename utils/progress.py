"""
进度显示工具
============
为批量处理提供终端进度条

使用方式：
    from progress import ProgressBar
    with ProgressBar(total=100, desc="Processing") as p:
        for i in range(100):
            process(item)
            p.update(1)
"""

from __future__ import annotations

import sys
import time
from typing import Optional


class ProgressBar:
    """终端进度条"""

    BAR_WIDTH = 40

    def __init__(
        self,
        total: int,
        desc: str = "",
        width: int = 60,
    ):
        self.total = total
        self.desc = desc
        self.width = width
        self.current = 0
        self.start_time = time.monotonic()

    def __enter__(self):
        self._draw()
        return self

    def __exit__(self, *args):
        print()  # 换行

    def update(self, n: int = 1) -> None:
        self.current += n
        self._draw()

    def _draw(self) -> None:
        if self.total == 0:
            frac = 1.0
        else:
            frac = min(self.current / self.total, 1.0)

        filled = int(self.BAR_WIDTH * frac)
        empty = self.BAR_WIDTH - filled
        pct = int(frac * 100)

        elapsed = time.monotonic() - self.start_time
        if self.current > 0:
            rate = self.current / elapsed  # items/sec
            eta = (self.total - self.current) / rate if rate > 0 else 0
        else:
            rate = 0
            eta = 0

        eta_str = f"{eta:.1f}s" if eta > 0 else "0s"

        bar = "█" * filled + "░" * empty
        line = f"\r{self.desc} |{bar}| {pct:3d}% ({self.current}/{self.total}) {rate:.1f}/s  ETA {eta_str}"

        # 截断到终端宽度
        if len(line) > self.width:
            line = line[: self.width - 1] + "…"

        sys.stdout.write(line)
        sys.stdout.flush()


def spinner(desc: str) -> "Spinner":
    """返回一个一次性 spinner（用于未知总数的任务）"""
    return Spinner(desc)


class Spinner:
    """加载 spinner"""

    FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def __init__(self, desc: str):
        self.desc = desc
        self.index = 0

    def __enter__(self):
        return self

    def __exit__(self, *args):
        print()

    def tick(self) -> None:
        frame = self.FRAMES[self.index % len(self.FRAMES)]
        self.index += 1
        line = f"\r{frame} {self.desc}"
        sys.stdout.write(line)
        sys.stdout.flush()